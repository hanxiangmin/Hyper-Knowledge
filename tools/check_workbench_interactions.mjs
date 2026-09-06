/**
 * Exhaustive, real-pointer regression audit for an exported offline workbench.
 * Usage: node tools/check_workbench_interactions.mjs HTML BUNDLE OUTPUT
 * Optional: HK_BROWSER_EXECUTABLE, HK_PLAYWRIGHT_MODULE, HK_QA_WIDTH,
 * HK_QA_HEIGHT, HK_QA_SETTLE_MS. With no override, require('playwright').
 * Uses a fresh isolated context; never reads a personal browser profile.
 * Every failed assertion is reported and the process exits nonzero.
 */
import {createRequire} from 'node:module';
import {readFile, writeFile, mkdir} from 'node:fs/promises';
import {resolve, join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';

const require = createRequire(import.meta.url);
const {chromium} = require(process.env.HK_PLAYWRIGHT_MODULE || 'playwright');
const [htmlArg, bundleArg, outArg] = process.argv.slice(2);
if (!htmlArg || !bundleArg || !outArg) throw new Error('Expected HTML BUNDLE OUTPUT');
const html = resolve(htmlArg), bundle = resolve(bundleArg), output = resolve(outArg);
const viewport = {width: Number(process.env.HK_QA_WIDTH || 1440), height: Number(process.env.HK_QA_HEIGHT || 1000)};
const settleMs = Number(process.env.HK_QA_SETTLE_MS || 65);
await mkdir(output, {recursive: true});
const readJsonl = async name => (await readFile(join(bundle, name), 'utf8')).split(/\r?\n/).filter(Boolean).map(JSON.parse);
const [nodes, assertions, members] = await Promise.all(['nodes.jsonl', 'assertions.jsonl', 'members.jsonl'].map(readJsonl));
const unique = list => [...new Set(list.map(String))].sort();
const equal = (a, b) => JSON.stringify(unique(a)) === JSON.stringify(unique(b));
const nodeIds = unique(nodes.map(n => n.id)), assertionIds = unique(assertions.map(a => a.id));
const membersOf = id => unique(members.filter(m => m.assertion_id === id).map(m => m.node_id));
const incidentTo = id => unique(members.filter(m => m.node_id === id).map(m => m.assertion_id));
const unionOf = ids => unique(ids.flatMap(membersOf));
const attr = value => JSON.stringify(String(value));
const sourceHash = () => readFile(html).then(bytes => createHash('sha256').update(bytes).digest('hex'));
const report = {html, bundle, viewport, sha256: await sourceHash(), startedAt: new Date().toISOString(), interactions: [], checks: [], states: [], errors: [], blockedNetwork: []};
const record = (name, ok, detail = {}) => { report.checks.push({name, ok: Boolean(ok), detail}); return ok; };
const browser = await chromium.launch({headless: true, ...(process.env.HK_BROWSER_EXECUTABLE ? {executablePath: process.env.HK_BROWSER_EXECUTABLE} : {})});
const context = await browser.newContext({viewport, deviceScaleFactor: 1, locale: 'zh-CN', colorScheme: 'light'});
const page = await context.newPage();
page.setDefaultTimeout(3500);
page.on('pageerror', error => report.errors.push({kind: 'pageerror', message: error.message}));
page.on('console', msg => {if (msg.type() === 'error') report.errors.push({kind: 'console', message: msg.text()});});
await page.route(/^https?:/, route => {report.blockedNetwork.push(route.request().url());return route.abort();});
let serial = 0;
const settle = () => page.waitForTimeout(settleMs);
const screenshot = async name => {
  const filename = `${String(++serial).padStart(4, '0')}-${name.replace(/[^a-z0-9_-]+/gi, '-').slice(0, 100)}.png`;
  await page.screenshot({path: join(output, filename), fullPage: true});
  return filename;
};
async function task(name, fn) {
  const start = report.checks.length;
  try { await fn(); }
  catch (error) { record(name, false, {error: error.stack}); }
  const failures = report.checks.slice(start).filter(c => !c.ok);
  if (failures.length) {
    const image = await screenshot(`FAIL-${name}`);
    for (const failure of failures) failure.screenshot = image;
    await writeFile(join(output,`${image}.json`),JSON.stringify(failures,null,2));
  }
  console.log(JSON.stringify({task: name, checks: report.checks.length - start, failures: failures.length}));
}
async function click(locator, name, targetKind = 'box') {
  if (await locator.count() === 0) throw new Error(`Missing click target: ${name}`);
  locator = locator.first();
  await locator.scrollIntoViewIfNeeded();
  await settle();
  let point;
  if (targetKind === 'outline' || targetKind === 'fill' || targetKind === 'link') {
    point = await locator.evaluate((element, kind) => {
      const bounds = element.getBoundingClientRect(), candidates = [], matrix = element.getScreenCTM();
      if (kind !== 'fill' && element.getTotalLength) {
        const length = element.getTotalLength();
        for (let i = 0; i < 80; i++) {const p = element.getPointAtLength(length * ((i + .35) / 80));candidates.push(new DOMPoint(p.x, p.y).matrixTransform(matrix));}
      } else {
        for (let iy = 1; iy < 10; iy++) for (let ix = 1; ix < 10; ix++) candidates.push({x: bounds.x + bounds.width * ix / 10, y: bounds.y + bounds.height * iy / 10});
      }
      for (const p of candidates) {
        if (p.x < 0 || p.y < 0 || p.x >= innerWidth || p.y >= innerHeight) continue;
        const hit = document.elementFromPoint(p.x, p.y);
        if (hit === element || element.contains(hit)) return {x: p.x, y: p.y};
      }
      return null;
    }, targetKind);
    if (!point) throw new Error(`No exposed ${targetKind} hit point: ${name}`);
  } else {
    const b = await locator.boundingBox();
    if (!b) throw new Error(`No bounds: ${name}`);
    point = {x: b.x + b.width / 2, y: b.y + b.height / 2};
  }
  const hit = await page.evaluate(p => {
    const e = document.elementFromPoint(p.x, p.y), semantic = e?.closest('[data-node],[data-assertion]');
    return {tag: e?.tagName, class: e?.getAttribute('class'), node: semantic?.dataset.node, assertion: semantic?.dataset.assertion};
  }, point);
  report.interactions.push({name, kind: targetKind, point, hit});
  await page.mouse.click(point.x, point.y);
  await settle();
}
const view = async mode => {await click(page.locator(`[data-representation=${attr(mode)}]`), `switch:${mode}`);record(`view:${mode}`, await page.locator(`[data-representation=${attr(mode)}]`).getAttribute('aria-pressed') === 'true');};
const reset = async () => click(page.locator('[data-action="reset"]'), 'reset');
const nodeMark = id => page.locator(`.entity-mark[data-node=${attr(id)}] .node-halo`);
const rowMark = id => page.locator(`.matrix-row-label[data-node=${attr(id)}]`);
const columnMark = id => page.locator(`.matrix-column-header[data-assertion=${attr(id)}] circle`);
const assertionMark = (mode, id) => page.locator(`${mode === 'contour' ? '.hyperedge-label' : '.assertion-mark'}[data-assertion=${attr(id)}] .label-block-bg`);
async function inspect(name, selection = null, collect = true) {
  const state = await page.evaluate(() => {
    const q = selector => [...document.querySelectorAll(selector)];
    const shown = e => !e.classList.contains('is-hidden') && getComputedStyle(e).display !== 'none';
    const rect = e => {const b = e.getBoundingClientRect();return {x:b.x,y:b.y,width:b.width,height:b.height,right:b.right,bottom:b.bottom};};
    const entities = q('.entity-mark').filter(shown).map(e => ({id:e.dataset.node, assertion:e.dataset.assertion, box:rect(e.querySelector('.node-halo'))}));
    const relations = q('.hyperedge-label,.assertion-mark').filter(shown).map(e => ({id:e.dataset.assertion,box:rect(e.querySelector('.label-block'))}));
    const paths = q('.link').filter(shown).map(e => ({assertion:e.dataset.assertion,node:e.dataset.node,secondary:e.dataset.nodeSecondary,d:e.getAttribute('d'),kind:e.classList.contains('pairwise')?'pairwise':'incidence'}));
    const contours = q('.hyper-envelope').filter(shown).map(e => {const b=e.getBBox(),cx=b.x+b.width/2,cy=b.y+b.height/2,length=e.getTotalLength(),r=b.width/2;let circleResidual=0;for(let i=0;i<48;i++){const p=e.getPointAtLength(length*i/48);circleResidual=Math.max(circleResidual,Math.abs(Math.hypot(p.x-cx,p.y-cy)/r-1));}return {id:e.dataset.assertion,d:e.getAttribute('d'),circleResidual,aspect:b.width/b.height};});
    const drawerIds = q('#drawer-body .detail-grid dd').map(e => e.textContent.trim());
    const cells = q('.matrix-cell').map(e => ({node:e.dataset.node,assertion:e.dataset.assertion,roles:JSON.parse(e.dataset.roles || '[]')}));
    const rows = q('.matrix-row-label').map(e => e.dataset.node), columns = q('.matrix-column-header').map(e => e.dataset.assertion);
    const fonts = q('.node-inside-label,.matrix-node-text,.matrix-column-text').map(e => {const m=e.getScreenCTM();return parseFloat(getComputedStyle(e).fontSize)*Math.hypot(m.a,m.b);});
    const collisions = [];
    for (let i=0;i<entities.length;i++) for(let j=i+1;j<entities.length;j++) {const a=entities[i],b=entities[j],d=Math.hypot(a.box.x+a.box.width/2-b.box.x-b.box.width/2,a.box.y+a.box.height/2-b.box.y-b.box.height/2),radius=(a.box.width+b.box.width)/2;if(d<radius-1)collisions.push({kind:'node-node',a:a.id,b:b.id,depth:radius-d});}
    for(let i=0;i<relations.length;i++)for(let j=i+1;j<relations.length;j++){const a=relations[i],b=relations[j];if(Math.min(a.box.right,b.box.right)>Math.max(a.box.x,b.box.x)+1&&Math.min(a.box.bottom,b.box.bottom)>Math.max(a.box.y,b.box.y)+1)collisions.push({kind:'title-title',a:a.id,b:b.id});}
    const canvas=document.querySelector('.canvas-wrap').getBoundingClientRect();
    const titleHits = relations.map(r=>{const b=r.box,x=b.x+b.width/2,y=b.y+b.height/2;if(x<Math.max(0,canvas.x)||y<Math.max(0,canvas.y)||x>=Math.min(innerWidth,canvas.right)||y>=Math.min(innerHeight,canvas.bottom))return null;const hit=document.elementFromPoint(x,y);return {expected:r.id,actual:hit?.closest('[data-assertion]')?.dataset.assertion,node:hit?.closest('[data-node]')?.dataset.node};}).filter(Boolean);
    return {view:document.querySelector('.representation-button[aria-pressed="true"]')?.dataset.representation,summary:!!document.querySelector('.membership-summary'),symmetric:!!document.querySelector('.symmetric-contour'),entities,relations,paths,contours,drawerIds,cells,rows,columns,fonts:{min:fonts.length?Math.min(...fonts):null,max:fonts.length?Math.max(...fonts):null},collisions,titleHits,selected:q('.mark.is-selected').map(e=>({node:e.dataset.node,assertion:e.dataset.assertion})),pageOverflow:document.documentElement.scrollWidth>innerWidth};
  });
  state.name = name;
  if (collect) report.states.push(state);
  const inMatrix = state.view === 'matrix';
  if (selection) record(`${name}:drawer identity`, state.drawerIds.includes(selection.id), {expected:selection.id,actual:state.drawerIds});
  if (inMatrix) {
    record(`${name}:matrix node set`, equal(state.rows,nodeIds), {actual:state.rows,expected:nodeIds});
    record(`${name}:matrix assertion set`, equal(state.columns,assertionIds), {actual:state.columns,expected:assertionIds});
    record(`${name}:matrix complete incidence`, equal(state.cells.map(c=>`${c.assertion}|${c.node}`),members.map(m=>`${m.assertion_id}|${m.node_id}`)));
    for(const cell of state.cells) record(`${name}:roles:${cell.assertion}:${cell.node}`,equal(cell.roles,members.filter(m=>m.assertion_id===cell.assertion&&m.node_id===cell.node).map(m=>m.role)));
  } else {
    const actualNodes = unique(state.entities.map(n=>n.id)), actualRelations = unique(state.relations.map(r=>r.id));
    let expectedAssertions = assertionIds, expectedNodes = nodeIds;
    if(selection?.kind==='assertion'){expectedAssertions=[selection.id];expectedNodes=membersOf(selection.id);}
    if(selection?.kind==='node'){expectedAssertions=incidentTo(selection.id);expectedNodes=state.summary?[selection.id]:unionOf(expectedAssertions);}
    if(state.summary&&!selection){expectedAssertions=actualRelations;expectedNodes=actualNodes;record(`${name}:summary actual membership`,actualRelations.every(id=>membersOf(id).includes(actualNodes[0])));}
    record(`${name}:node set`,equal(actualNodes,expectedNodes),{actual:actualNodes,expected:expectedNodes});
    record(`${name}:assertion set`,equal(actualRelations,expectedAssertions),{actual:actualRelations,expected:expectedAssertions});
    record(`${name}:no orphan paths`,state.paths.every(p=>actualNodes.includes(p.node)&&actualRelations.includes(p.assertion)&&(!p.secondary||actualNodes.includes(p.secondary))&&Boolean(p.d)),state.paths);
    if(state.view==='incidence'){
      const expectedLinks=members.filter(m=>expectedAssertions.includes(m.assertion_id)&&expectedNodes.includes(m.node_id)).map(m=>`${m.assertion_id}|${m.node_id}`);
      record(`${name}:exact incidence links`,equal(state.paths.map(p=>`${p.assertion}|${p.node}`),expectedLinks),{actual:state.paths.map(p=>`${p.assertion}|${p.node}`),expected:expectedLinks});
    }
    record(`${name}:no orphan contour`,state.contours.every(p=>actualRelations.includes(p.id)&&Boolean(p.d)),state.contours);
    if(state.symmetric)record(`${name}:regular circles`,state.contours.every(p=>Math.abs(p.aspect-1)<.001&&p.circleResidual<.003),state.contours.map(p=>({id:p.id,aspect:p.aspect,residual:p.circleResidual})));
    record(`${name}:no native binary paths`,state.paths.every(p=>p.kind!=='pairwise'));
    record(`${name}:no circle or title collision`,state.collisions.length===0,state.collisions);
    record(`${name}:correct title hit`,state.titleHits.every(h=>h.expected===h.actual),state.titleHits.filter(h=>h.expected!==h.actual));
    if(state.view==='contour'&&state.entities.some(n=>n.assertion))for(const assertion of actualRelations)record(`${name}:occurrence members:${assertion}`,equal(state.entities.filter(n=>n.assertion===assertion).map(n=>n.id),membersOf(assertion)));
  }
  return state;
}
async function selectFromMatrix(kind,id){await view('matrix');await click(kind==='node'?rowMark(id):columnMark(id),`select:${kind}:${id}`);}
try {
  await page.goto(pathToFileURL(html).href);
  await settle();
  await click(page.locator('[data-language="zh"]'),'language:zh');
  record('exactly three representations',equal(await page.locator('.representation-button').evaluateAll(es=>es.map(e=>e.dataset.representation)),['matrix','incidence','contour']));
  record('high-order source only',assertions.every(a=>membersOf(a.id).length>=3)&&assertions.every(a=>a.topology==='hyperedge'),assertions.map(a=>({id:a.id,topology:a.topology,arity:membersOf(a.id).length})));
  for(const mode of ['matrix','incidence','contour']) await task(`overview:${mode}`,async()=>{await reset();await view(mode);await inspect(`overview:${mode}`);await screenshot(`overview-${mode}`);});
  for(const node of nodes) await task(`node:${node.id}`,async()=>{
    await reset();await selectFromMatrix('node',node.id);await inspect(`node:${node.id}:matrix`,{kind:'node',id:node.id});
    for(const mode of ['contour','incidence','matrix','incidence','contour','matrix']){
      await view(mode);
      if(mode!=='matrix')await click(nodeMark(node.id),`node-${mode}:${node.id}`);
      await inspect(`node:${node.id}:${mode}`,{kind:'node',id:node.id});
    }
    const incident=incidentTo(node.id);
    for(const id of incident){
      await selectFromMatrix('node',node.id);await view('incidence');
      await click(page.locator(`#drawer-body .member-row[data-assertion=${attr(id)}]`),`drawer-related:${node.id}:${id}`);
      await inspect(`drawer-related:${node.id}:${id}`,{kind:'assertion',id});
    }
  });
  for(const assertion of assertions) await task(`assertion:${assertion.id}`,async()=>{
    const id=assertion.id;
    await reset();await selectFromMatrix('assertion',id);await inspect(`assertion:${id}:matrix`,{kind:'assertion',id});
    await click(page.locator(`.matrix-key-item[data-assertion=${attr(id)}]`),`matrix-key:${id}`);await inspect(`matrix-key:${id}`,{kind:'assertion',id});
    await reset();await view('contour');await click(assertionMark('contour',id),`overview-title:${id}`);await inspect(`overview-title:${id}`,{kind:'assertion',id});await screenshot(`focused-contour-${id}`);
    let incidenceCaptured=false;
    for(const mode of ['contour','incidence','matrix','incidence','contour','matrix']){
      await view(mode);
      if(mode!=='matrix')await click(assertionMark(mode,id),`title-${mode}:${id}`);
      await inspect(`assertion:${id}:${mode}`,{kind:'assertion',id});
      if(mode==='incidence'&&!incidenceCaptured){await screenshot(`focused-incidence-${id}`);incidenceCaptured=true;}
    }
    for(const kind of ['fill','outline']){
      await reset();await view('contour');
      await click(page.locator(`.${kind==='fill'?'hyper-envelope-fill':'hyper-envelope'}[data-assertion=${attr(id)}]`),`contour-${kind}:${id}`,kind);
      await inspect(`contour-${kind}:${id}`,{kind:'assertion',id});
    }
    for(const nodeId of membersOf(id)){
      await selectFromMatrix('assertion',id);await view('incidence');
      await click(page.locator(`#drawer-body .member-row[data-node=${attr(nodeId)}]`),`drawer-member:${id}:${nodeId}`);
      await inspect(`drawer-member:${id}:${nodeId}`,{kind:'node',id:nodeId});
      await selectFromMatrix('assertion',id);await view('incidence');
      await click(page.locator(`.link.incidence[data-assertion=${attr(id)}][data-node=${attr(nodeId)}]`),`incidence-link:${id}:${nodeId}`,'link');
      await inspect(`incidence-link:${id}:${nodeId}`,{kind:'assertion',id});
    }
  });
  for(const member of members)await task(`matrix-cell:${member.assertion_id}:${member.node_id}`,async()=>{
    await reset();await view('matrix');
    await click(page.locator(`.matrix-cell[data-assertion=${attr(member.assertion_id)}][data-node=${attr(member.node_id)}]`),`matrix-cell:${member.assertion_id}:${member.node_id}`);
    await inspect(`matrix-cell:${member.assertion_id}:${member.node_id}`,{kind:'assertion',id:member.assertion_id});
    for(const mode of ['incidence','contour','matrix']){await view(mode);await inspect(`cell-switch:${mode}:${member.assertion_id}:${member.node_id}`,{kind:'assertion',id:member.assertion_id});}
  });
  for(const member of members)await task(`contour-occurrence:${member.assertion_id}:${member.node_id}`,async()=>{
    await reset();await view('contour');
    const repeated=page.locator(`.entity-mark[data-node=${attr(member.node_id)}][data-owner-assertion=${attr(member.assertion_id)}] .node-halo`);
    const target=await repeated.count()?repeated:nodeMark(member.node_id);
    await click(target,`contour-occurrence:${member.assertion_id}:${member.node_id}`);
    await inspect(`contour-occurrence:${member.assertion_id}:${member.node_id}`,{kind:'node',id:member.node_id});
  });
  for(const assertion of assertions)await task(`hover:${assertion.id}`,async()=>{
    const id=assertion.id;await reset();await view('contour');
    const fillStyle=()=>page.locator(`.hyper-envelope-fill[data-assertion=${attr(id)}]`).first().evaluate(e=>{const s=getComputedStyle(e);return{fill:s.fill,opacity:s.opacity};});
    const plainFill=await fillStyle();
    const card=assertionMark('contour',id).first();await card.scrollIntoViewIfNeeded();await card.hover();await page.waitForTimeout(420);
    const readHover=()=>page.evaluate(()=>({fills:[...document.querySelectorAll('.hyper-envelope-fill.is-hover-focus')].map(e=>e.dataset.assertion),crispNodes:[...document.querySelectorAll('.entity-mark:not(.is-hover-muted)')].map(e=>e.dataset.node),mutedNodes:[...document.querySelectorAll('.entity-mark.is-hover-muted')].map(e=>e.dataset.node),paths:[...document.querySelectorAll('.hyper-envelope,.hyper-envelope-fill')].map(e=>({id:e.dataset.assertion,active:e.classList.contains('is-hover-focus'),opacity:+getComputedStyle(e).opacity,width:parseFloat(getComputedStyle(e).strokeWidth),fill:e.classList.contains('hyper-envelope-fill')}))}));
    const hover=await readHover();record(`hover:${id}:exact members`,equal(hover.crispNodes,membersOf(id)),hover);record(`hover:${id}:one tinted enclosure`,equal(hover.fills,[id]),hover);
    record(`hover:${id}:computed unrelated boundaries dim`,hover.paths.filter(p=>p.id!==id).every(p=>p.opacity<.2),hover.paths);
    record(`hover:${id}:computed active emphasis`,hover.paths.filter(p=>p.id===id).every(p=>p.opacity>.95&&(p.fill||p.width>=3.2)),hover.paths);
    const tintedFill=await fillStyle();record(`hover:${id}:actual fill changes`,JSON.stringify(plainFill)!==JSON.stringify(tintedFill),{plainFill,tintedFill});
    if(id===assertions[assertions.length-1].id)await screenshot(`hover-tint-${id}`);
    await nodeMark(membersOf(id)[0]).first().hover();await settle();record(`hover:${id}:member continuity`,equal((await readHover()).fills,[id]));
    await page.locator('.panel-head').first().hover();await page.waitForTimeout(160);record(`hover:${id}:clear`,(await readHover()).fills.length===0);
  });
  await task('controls-and-keyboard',async()=>{
    for(const mode of ['matrix','incidence','contour']){
      await reset();await view(mode);
      const before=await page.locator('.viewport').getAttribute('transform');
      await click(page.locator('[data-action="zoom-in"]'),`zoom-in:${mode}`);const after=await page.locator('.viewport').getAttribute('transform');
      record(`zoom:${mode}`,before!==after,{before,after});
      await click(page.locator('[data-action="zoom-out"]'),`zoom-out:${mode}`);await reset();await inspect(`reset:${mode}`);
      for(const language of ['en','zh']){await click(page.locator(`[data-language=${attr(language)}]`),`language:${language}:${mode}`);await inspect(`language:${language}:${mode}`);}
      await click(page.locator('#theme-toggle'),`theme-dark:${mode}`);record(`theme-dark:${mode}`,await page.locator('html').getAttribute('data-theme')==='dark');await inspect(`dark:${mode}`);if(mode==='contour')await screenshot('dark-contour');await click(page.locator('#theme-toggle'),`theme-light:${mode}`);
    }
    await reset();await view('contour');const id=assertions[0].id,target=page.locator(`.hyperedge-label[data-assertion=${attr(id)}]`).first();await target.focus();await page.keyboard.press('Enter');await settle();await inspect('keyboard-title',{kind:'assertion',id});record('keyboard focus retained',await page.evaluate(id=>document.activeElement?.dataset.assertion===id,id));
    await click(page.locator('#drawer-body .raw-details summary'),'raw-record');record('raw record expanded',await page.locator('#drawer-body .raw-details').first().getAttribute('open')!==null);
  });
  await task('drag-reset',async()=>{
    const id=assertions.find(a=>membersOf(a.id).length>=4)?.id||assertions[0].id;
    for(const mode of ['contour','incidence']){
      await reset();await selectFromMatrix('assertion',id);await view(mode);
      const nid=membersOf(id)[0],glyph=nodeMark(nid).first();await glyph.scrollIntoViewIfNeeded();const b=await glyph.boundingBox();
      const old=await glyph.evaluate(e=>e.closest('.entity-mark').getAttribute('transform'));
      await page.mouse.move(b.x+b.width/2,b.y+b.height/2);await page.mouse.down();await page.mouse.move(b.x+b.width/2+65,b.y+b.height/2+35,{steps:15});await page.mouse.up();await settle();
      const moved=await nodeMark(nid).first().evaluate(e=>e.closest('.entity-mark').getAttribute('transform'));record(`drag:${mode}:moved`,old!==moved,{old,moved});await inspect(`drag:${mode}`,{kind:'assertion',id});await screenshot(`drag-${mode}`);
      await reset();await inspect(`drag-reset:${mode}`);record(`drag-reset:${mode}:empty drawer`,await page.locator('#drawer').evaluate(e=>e.classList.contains('is-empty')));
    }
  });
  for(const small of [{width:1920,height:1080},{width:390,height:844}])await task(`viewport:${small.width}`,async()=>{
    await page.setViewportSize(small);await page.waitForTimeout(220);
    for(const mode of ['matrix','incidence','contour']){await reset();await view(mode);const state=await inspect(`viewport:${small.width}:${mode}`);record(`viewport:${small.width}:${mode}:readable`,state.fonts.min>=10,state.fonts);await screenshot(`viewport-${small.width}-${mode}`);}
    await view('matrix');await click(rowMark(nodeIds[nodeIds.length-1]),`last-row:${small.width}`);await inspect(`last-row:${small.width}`,{kind:'node',id:nodeIds[nodeIds.length-1]});
    const id=assertions[assertions.length-1].id;await selectFromMatrix('assertion',id);await view('contour');await inspect(`last-edge:${small.width}`,{kind:'assertion',id});
  });
} catch(error) { report.errors.push({kind:'fatal',message:error.stack}); }
finally {
  report.finishedAt=new Date().toISOString();report.sourceUnchanged=report.sha256===await sourceHash();
  report.passed=report.sourceUnchanged&&report.errors.length===0&&report.blockedNetwork.length===0&&report.checks.every(c=>c.ok);
  report.totals={nodes:nodes.length,assertions:assertions.length,members:members.length,interactions:report.interactions.length,states:report.states.length,checks:report.checks.length,failed:report.checks.filter(c=>!c.ok).length};
  await writeFile(join(output,'interaction-report.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify({passed:report.passed,...report.totals,errors:report.errors,failures:report.checks.filter(c=>!c.ok).map(c=>({name:c.name,detail:c.detail,screenshot:c.screenshot}))}));
  await browser.close();
  if(!report.passed)process.exitCode=1;
}
