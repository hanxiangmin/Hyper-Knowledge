/** Record real offline workbench interactions in an isolated local Chromium.
 * npm install playwright; npx playwright install chromium ffmpeg
 * node tools/capture_showcase.mjs --out temp/capture --browser /path/to/chrome
 * The optional --ffmpeg creates a private Playwright FFmpeg runtime in --out.
 * No existing browser profiles or graph data are changed.
 */
import {createRequire} from 'node:module';
import {mkdir, readFile, writeFile, copyFile} from 'node:fs/promises';
import {resolve, join, dirname} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {performance} from 'node:perf_hooks';
const args = process.argv.slice(2);
const opt = (name, fallback) => args.includes(name) ? args[args.indexOf(name)+1] : fallback;
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const out = resolve(opt('--out', join(root, 'temp/live-capture')));
const source = resolve(opt('--source', join(root,'examples/sushi-document-test/views/workbench.html')));
const bundle = resolve(opt('--bundle', join(dirname(dirname(source)), 'bundle')));
const requestedModule = opt('--playwright', 'playwright');
const modulePath = /[\\/]/.test(requestedModule) ? resolve(requestedModule) : requestedModule;
await mkdir(out,{recursive:true});
const require = createRequire(import.meta.url);
if (opt('--ffmpeg')) {
  const packageRoot = dirname(require.resolve(modulePath));
  const coreRoot = dirname(require.resolve('playwright-core/package.json', {paths:[packageRoot]}));
  const registry = JSON.parse(await readFile(join(coreRoot,'browsers.json'),'utf8'));
  const revision = registry.browsers.find(b=>b.name==='ffmpeg').revision;
  process.env.PLAYWRIGHT_BROWSERS_PATH = join(out,'runtime');
  const ffmpegDir = join(process.env.PLAYWRIGHT_BROWSERS_PATH, `ffmpeg-${revision}`);
  await mkdir(ffmpegDir,{recursive:true});
  await copyFile(resolve(opt('--ffmpeg')),join(ffmpegDir,process.platform==='win32'?'ffmpeg-win64.exe':'ffmpeg-linux'));
}
const {chromium} = require(modulePath);
const browser = await chromium.launch({headless:true, ...(opt('--browser')?{executablePath:resolve(opt('--browser'))}:{})});
const viewport = {width:1920,height:1200};
const edge = 'assertion:family-san-su';
const node = 'person:su-shi';
const readRows = async name => (await readFile(join(bundle, name), 'utf8')).trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
const [nodesTable, assertionsTable, membersTable] = await Promise.all(['nodes.jsonl', 'assertions.jsonl', 'members.jsonl'].map(readRows));
const uniq = values => [...new Set(values.map(String))].sort();
const edgeMembers = uniq(membersTable.filter(member => String(member.assertion_id) === edge).map(member => member.node_id));
const nodeHyperedges = uniq(membersTable.filter(member => String(member.node_id) === node).map(member => member.assertion_id));
const sourceCounts = {
  nodes: nodesTable.length,
  assertions: assertionsTable.length,
  memberships: membersTable.length,
  edgeMembers: edgeMembers.length,
  nodeHyperedges: nodeHyperedges.length,
};
const sourceHash = createHash('sha256').update(await readFile(source)).digest('hex');
const locales = opt('--locale','zh,en').split(',');
try {
 for (const locale of locales) {
  const folder=join(out,locale); await mkdir(folder,{recursive:true});
  const context = await browser.newContext({viewport,deviceScaleFactor:1,colorScheme:'light',locale:locale==='zh'?'zh-CN':'en-US',recordVideo:{dir:folder,size:viewport}});
  // Only a pointer indicator is added. App layout, entities, and state are untouched.
  await context.addInitScript(()=>{
   document.addEventListener('DOMContentLoaded',()=>{
    const cursor=document.createElement('div');cursor.id='capture-pointer';cursor.setAttribute('aria-hidden','true');
    cursor.style.cssText='position:fixed;left:-50px;top:-50px;width:12px;height:12px;border:2px solid #fff;border-radius:50%;background:#153f34;box-shadow:0 0 0 2px #153f3455;pointer-events:none;z-index:2147483647;transform:translate(-50%,-50%)';document.body.append(cursor);
    document.addEventListener('pointermove',e=>{cursor.style.left=e.clientX+'px';cursor.style.top=e.clientY+'px'});
    document.addEventListener('pointerdown',()=>{cursor.style.boxShadow='0 0 0 9px #153f3430'});
    document.addEventListener('pointerup',()=>{cursor.style.boxShadow='0 0 0 2px #153f3455'});
   });
  });
  const start=performance.now();
  const page = await context.newPage(); const errors=[];
  page.on('pageerror', e=>errors.push(e.message));
  // Block external traffic: this is an offline reader, not a hosted parsing service.
  await page.route(/^https?:/,route=>route.abort());
  await page.goto(pathToFileURL(source).href);
  await page.locator(`[data-language="${locale}"]`).click();
  await page.waitForTimeout(600);
  const enclosureView = await page.locator('[data-representation="overview"]').count() ? 'overview' : 'contour';
  const edgeMarkSelector = await page.locator(`.overview-edge[data-assertion="${edge}"]`).count()
    ? `.overview-edge[data-assertion="${edge}"]`
    : `.hyperedge-label[data-assertion="${edge}"]`;
  const now=()=> (performance.now()-start)/1000;
  const scenes=[];
  const move=async selector=>{const b=await page.locator(selector).boundingBox();if(!b)throw new Error('Missing target: '+selector);await page.mouse.move(b.x+b.width/2,b.y+b.height/2,{steps:18});return b;};
  const click=async selector=>{
   const b=await move(selector),x=b.x+b.width/2,y=b.y+b.height/2;
   // SVG labels may deliberately pass events to the same hyperedge's fill.
   // Hit-test its identity before delivering an ordinary mouse click.
   const valid=await page.evaluate(({selector,x,y})=>{
    const requested=document.querySelector(selector),hit=document.elementFromPoint(x,y);
    if(requested.contains(hit))return true;
    const a=requested.dataset.assertion,n=requested.dataset.node;
    return Boolean(a&&hit.closest('[data-assertion]')?.dataset.assertion===a||n&&hit.closest('[data-node]')?.dataset.node===n);
   },{selector,x,y});
   if(!valid)throw new Error('Unexpected click target: '+selector);
   await page.mouse.click(x,y);await page.waitForTimeout(600);
  };
  const view=async name=>click(`[data-representation="${name}"]`);
  const park=async()=>page.mouse.move(1900,90,{steps:14});
  const inspect=async()=>page.evaluate(()=>({
   representation:document.querySelector('.representation-button[aria-pressed="true"]').dataset.representation,
   nodes:[...new Set([...document.querySelectorAll('.entity-mark,.overview-node')].map(n=>n.dataset.node).filter(Boolean))],
   relations:[...new Set([...document.querySelectorAll('.hyperedge-label,.assertion-mark,.overview-edge')].map(n=>n.dataset.assertion).filter(Boolean))],
   matrixRows:document.querySelectorAll('.matrix-row-label').length,
   matrixColumns:document.querySelectorAll('.matrix-column-header').length,
   matrixCells:document.querySelectorAll('.matrix-cell').length,
   drawerTitle:document.querySelector('.drawer-title')?.textContent||null,
   selected:[...document.querySelectorAll('.is-selected')].map(n=>({node:n.dataset.node,assertion:n.dataset.assertion})),
   hoverNodes:[...new Set([
    ...[...document.querySelectorAll('.entity-mark:not(.is-hover-muted)')].map(n=>n.dataset.node),
    ...[...document.querySelectorAll('.overview-node.is-overview-related')].map(n=>n.dataset.node),
   ].filter(Boolean))],
   hoverMuted:document.querySelectorAll('.is-hover-muted,.is-overview-muted').length,
   hoverFill:[...document.querySelectorAll('.hyper-envelope-fill.is-hover-focus')].map(n=>({id:n.dataset.assertion,fill:getComputedStyle(n).fill,opacity:getComputedStyle(n).opacity})),
   overviewFocus:[...document.querySelectorAll('.overview-edge.is-overview-related')].map(n=>n.dataset.assertion),
   overviewRoles:[...document.querySelectorAll('.overview-role-label')].map(n=>({assertion:n.dataset.assertion,node:n.dataset.node,role:n.dataset.role})),
   bounds:{panel:document.querySelector('.viz-panel').getBoundingClientRect().toJSON(),canvas:document.querySelector('.canvas-wrap').getBoundingClientRect().toJSON()},
   graphOutsideViewport:document.querySelector('.canvas-wrap').getBoundingClientRect().bottom>innerHeight+1,
  }));
  const scene=async(id,action,{hover=false}={})=>{
   const startSec=now(); await page.waitForTimeout(350); await action();
   if(!hover)await park(); await page.waitForTimeout(650);
   const settledSec=now();const state=await inspect();
   if(state.graphOutsideViewport) throw new Error(id+': graph clipped');
   if(id.startsWith('edge-') && state.representation==='incidence' && (state.nodes.length!==sourceCounts.edgeMembers||state.relations.length!==1))throw new Error(id+': wrong edge membership');
   if(id==='node-incidence'&&(state.nodes.length!==1||state.relations.length!==sourceCounts.nodeHyperedges))throw new Error('Wrong node membership summary');
   if(state.representation==='matrix'&&(state.matrixRows!==sourceCounts.nodes||state.matrixColumns!==sourceCounts.assertions||state.matrixCells!==sourceCounts.memberships))throw new Error('Wrong matrix dimensions');
   if(hover){
    const hoverIsValid = (
      state.hoverMuted > 0
      && (
        state.hoverFill.some(f=>f.id===edge)
        || state.overviewFocus.includes(edge)
      )
      && (
        state.hoverNodes.length===sourceCounts.edgeMembers
        || state.overviewRoles.filter(role=>role.assertion===edge).length===sourceCounts.edgeMembers
      )
    );
    if(!hoverIsValid)throw new Error('Hover not exercised');
   }
   const screenshot=`${id}-${locale}.png`;
   await page.screenshot({path:join(folder,screenshot),fullPage:true});
   if(hover){await page.waitForTimeout(2100);await park();await page.waitForTimeout(900);await move(edgeMarkSelector);await page.waitForTimeout(1700);}
   await page.waitForTimeout(Math.max(0,(hover?8:5.5)*1000-(performance.now()-start-startSec*1000)));
   const entry={id,startSec,endSec:now(),settledSec,screenshot,state,bounds:state.bounds};scenes.push(entry);
   await writeFile(join(folder,'timeline.json'),JSON.stringify({locale,video:'session.webm',viewport,source,sourceSha256:sourceHash,bundle,sourceCounts,scenes,errors},null,2));
   console.log(`${locale}: ${id} / ${state.nodes.length} nodes / ${state.relations.length} edges / ${state.matrixRows} matrix rows`);
  };
  await scene('overview-matrix',()=>view('matrix'));
  await scene('overview-incidence',()=>view('incidence'));
  await scene('overview-enclosure',()=>view(enclosureView));
  await scene('edge-enclosure',()=>click(edgeMarkSelector));
  await scene('edge-incidence',()=>view('incidence'));
  await scene('edge-matrix',()=>view('matrix'));
  await scene('node-matrix',()=>click(`.matrix-row-label[data-node="${node}"]`));
  await scene('node-incidence',()=>view('incidence'));
  await scene('node-enclosure',()=>view(enclosureView));
  await click('[data-action="reset"]');await park();await page.waitForTimeout(500);
  await scene('hover-enclosure',()=>move(edgeMarkSelector),{hover:true});
  await park();await page.waitForTimeout(500);
  const cleared=await page.locator('.is-hover-muted,.is-hover-focus').count();if(cleared)throw new Error('Hover did not clear');
  const video=page.video();await context.close();await video.saveAs(join(folder,'session.webm'));
  if(errors.length)throw new Error(errors.join('\n'));
  const hash=createHash('sha256').update(await readFile(join(folder,'session.webm'))).digest('hex');
  await writeFile(join(folder,'timeline.json'),JSON.stringify({locale,video:'session.webm',viewport,source,sourceSha256:sourceHash,bundle,sourceCounts,videoSha256:hash,scenes,errors,hoverCleared:true,clockNote:'Scene timestamps use the local page-creation clock; recording starts within the initial navigation interval.'},null,2));
 }
} finally {await browser.close();}
if(sourceHash!==createHash('sha256').update(await readFile(source)).digest('hex'))throw new Error('Workbench changed during capture');
