/** Real-pointer QA for the opt-in one-hyperedge reader; no user browser profile. */
import {createRequire} from 'node:module';
import {readFile, writeFile, mkdir} from 'node:fs/promises';
import {resolve, join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const require=createRequire(import.meta.url),{chromium}=require(process.env.HK_PLAYWRIGHT_MODULE||'playwright');
const [htmlArg,bundleArg,outArg,mode='full']=process.argv.slice(2);
if(!htmlArg||!bundleArg||!outArg)throw new Error('Usage: node check_single_edge_reader.mjs HTML BUNDLE OUTPUT [smoke|full|visual]');
const html=resolve(htmlArg),bundle=resolve(bundleArg),output=resolve(outArg),pause=Number(process.env.HK_QA_SETTLE_MS||55);
await mkdir(output,{recursive:true});
const jsonl=async name=>(await readFile(join(bundle,name),'utf8')).split(/\r?\n/).filter(Boolean).map(JSON.parse);
const [nodes,edges,members]=await Promise.all(['nodes.jsonl','assertions.jsonl','members.jsonl'].map(jsonl));
const uniq=a=>[...new Set(a.map(String))].sort(),eq=(a,b)=>JSON.stringify(uniq(a))===JSON.stringify(uniq(b)),attr=JSON.stringify;
const nodeIds=nodes.map(n=>n.id),edgeIds=edges.map(e=>e.id),memberIds=id=>uniq(members.filter(m=>m.assertion_id===id).map(m=>m.node_id)),incident=id=>uniq(members.filter(m=>m.node_id===id).map(m=>m.assertion_id));
const degree=id=>incident(id).length,metrics=id=>({members:memberIds(id).length,shared:memberIds(id).filter(n=>degree(n)>1).length,neighbors:uniq(memberIds(id).flatMap(incident)).filter(e=>e!==id).length});
const hash=async()=>createHash('sha256').update(await readFile(html)).digest('hex');
const report={html,bundle,mode,sha256:await hash(),startedAt:new Date().toISOString(),checks:[],states:[],interactions:[],errors:[],blockedNetwork:[],screenshots:[]};
const check=(name,ok,detail={})=>{report.checks.push({name,ok:Boolean(ok),detail});return ok;};
const browser=await chromium.launch({headless:true,executablePath:process.env.HK_BROWSER_EXECUTABLE||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
const context=await browser.newContext({viewport:{width:1440,height:1000},deviceScaleFactor:1,locale:'zh-CN',colorScheme:'light'}),page=await context.newPage();
page.setDefaultTimeout(4000);page.on('pageerror',e=>report.errors.push(e.stack));page.on('console',m=>{if(m.type()==='error')report.errors.push(m.text());});
await page.route(/^https?:/,r=>{report.blockedNetwork.push(r.request().url());return r.abort();});
const settle=()=>page.waitForTimeout(pause);let imageIndex=0;
async function screenshot(name){const path=join(output,`${String(++imageIndex).padStart(3,'0')}-${name.replace(/[^a-z0-9_-]/gi,'-')}.png`);if(!name.includes('hover')){await page.mouse.move(1,1);await settle();}await page.screenshot({path,fullPage:false});report.screenshots.push(path);return path;}
async function task(name,fn){const start=report.checks.length;try{await fn();}catch(e){check(name,false,{error:e.stack});}const failures=report.checks.slice(start).filter(c=>!c.ok);if(failures.length){const path=await screenshot(`FAIL-${name}`);failures.forEach(f=>f.screenshot=path);}console.log(JSON.stringify({task:name,checks:report.checks.length-start,failed:failures.length}));}
async function click(locator,name,kind='box'){
  locator=locator.first();if(!await locator.count())throw new Error(`Missing target ${name}`);
  await locator.scrollIntoViewIfNeeded();await settle();
  let point;
  if(kind==='path'||kind==='fill')point=await locator.evaluate((e,kind)=>{const b=e.getBoundingClientRect(),m=e.getScreenCTM(),points=[];if(kind==='path'){const length=e.getTotalLength();for(let i=0;i<80;i++){const p=e.getPointAtLength(length*(i+.5)/80);points.push(new DOMPoint(p.x,p.y).matrixTransform(m));}}else for(let x=1;x<10;x++)for(let y=1;y<10;y++)points.push({x:b.x+b.width*x/10,y:b.y+b.height*y/10});return points.find(p=>p.x>=0&&p.y>=0&&p.x<innerWidth&&p.y<innerHeight&&document.elementFromPoint(p.x,p.y)===e)||null;},kind);
  else{const b=await locator.boundingBox();if(b)point={x:b.x+b.width/2,y:b.y+b.height/2};}
  if(!point)throw new Error(`No exposed target ${name}`);
  const hit=await page.evaluate(p=>{const e=document.elementFromPoint(p.x,p.y),s=e?.closest('[data-node],[data-assertion]');return{tag:e?.tagName,class:e?.getAttribute('class'),node:s?.dataset.node,assertion:s?.dataset.assertion};},point);
  report.interactions.push({name,kind,point,hit});await page.mouse.click(point.x,point.y);await settle();
}
const view=async v=>{await click(page.locator(`[data-representation=${attr(v)}]`),`view:${v}`);check(`selected view ${v}`,await page.locator(`[data-representation=${attr(v)}]`).getAttribute('aria-pressed')==='true');};
const reset=async()=>click(page.locator('[data-action="reset"]'),'reset');
const tab=async id=>click(page.locator(`.reader-tab[data-tab=${attr(id)}]`),`tab:${id}`);
const clear=async()=>{if(await page.locator('.reader-clear-filter').count())await click(page.locator('.reader-clear-filter'),'clear filter');};
const glyph=id=>page.locator(`.entity-mark[data-node=${attr(id)}] .node-halo`);
const edgeRow=id=>page.locator(`.reader-edge-row[data-assertion=${attr(id)}]`);
async function choose(id){await clear();await tab('edges');await click(edgeRow(id),`edge:${id}`);}
async function readState(){return page.evaluate(()=>{
  const q=s=>[...document.querySelectorAll(s)],shown=e=>!e.classList.contains('is-hidden')&&getComputedStyle(e).display!=='none';
  const box=e=>{const b=e.getBoundingClientRect();return{x:b.x,y:b.y,width:b.width,height:b.height,right:b.right,bottom:b.bottom};};
  const entities=q('.entity-mark').filter(shown).map(e=>{const c=e.querySelector('.node-halo'),m=e.transform.baseVal.consolidate()?.matrix;return{id:e.dataset.node,owner:e.dataset.assertion,degree:Number(e.dataset.hyperedgeDegree),r:Number(c?.getAttribute('r')),x:m?.e,y:m?.f,box:box(c),ring:!!e.querySelector('.shared-ring')};});
  const contours=q('.hyper-envelope').filter(shown).map(e=>{const b=e.getBBox(),cx=b.x+b.width/2,cy=b.y+b.height/2,length=e.getTotalLength(),r=b.width/2;let residual=0;for(let i=0;i<48;i++){const p=e.getPointAtLength(length*i/48);residual=Math.max(residual,Math.abs(Math.hypot(p.x-cx,p.y-cy)/r-1));}return{id:e.dataset.assertion,cx,cy,r,aspect:b.width/b.height,residual,d:e.getAttribute('d')};});
  const collisions=[];for(let i=0;i<entities.length;i++)for(let j=i+1;j<entities.length;j++){const a=entities[i].box,b=entities[j].box,d=Math.hypot(a.x+a.width/2-b.x-b.width/2,a.y+a.height/2-b.y-b.height/2);if(d<(a.width+b.width)/2-1)collisions.push([entities[i].id,entities[j].id]);}
  const rows=q('.reader-row').map(e=>({id:e.dataset.assertion||e.dataset.node,value:Number(e.dataset.value),rank:Number(e.dataset.rank),kind:e.dataset.assertion?'edge':'node',selected:e.getAttribute('aria-pressed')}));
  return{current:q('.single-edge-reader')[0]?.dataset.currentAssertion,view:q('.representation-button[aria-pressed=true]')[0]?.dataset.representation,reader:typeof readerState!=='undefined'?JSON.parse(JSON.stringify(readerState)):null,entities,contours,collisions,rows,metrics:q('.reader-metric').map(e=>({key:e.dataset.metric,value:Number(e.dataset.value),text:Number(e.querySelector('strong')?.textContent)})),chips:q('.reader-node-degree').map(e=>({node:e.dataset.node,value:Number(e.querySelector('b')?.textContent)})),drawer:q('#drawer-body .detail-grid dd').map(e=>e.textContent.trim()),index:q('.reader-index')[0]?.textContent,filter:q('.reader-filter')[0]?.textContent,prevDisabled:q('.reader-prev')[0]?.disabled,nextDisabled:q('.reader-next')[0]?.disabled,paths:q('.link').filter(shown).map(e=>({assertion:e.dataset.assertion,node:e.dataset.node,secondary:e.dataset.nodeSecondary,d:e.getAttribute('d'),pairwise:e.classList.contains('pairwise')})),matrixRows:q('.matrix-row-label').map(e=>e.dataset.node),matrixEdges:q('.matrix-column-header').map(e=>e.dataset.assertion),cells:q('.matrix-cell').map(e=>({node:e.dataset.node,assertion:e.dataset.assertion,roles:JSON.parse(e.dataset.roles||'[]')})),globalMetrics:typeof structuralMetrics==='function'?{nodes:[...structuralMetrics().nodes].map(([id,m])=>({id,degree:m.degree})),edges:[...structuralMetrics().edges].map(([id,m])=>({id,...m}))}:null,overflow:document.documentElement.scrollWidth>innerWidth};
});}
async function inspect(name,expected={}){
  const s=await readState();s.name=name;report.states.push(s);
  if(expected.node&&!expected.edge)check(`${name}:selected node drawer`,s.drawer.includes(expected.node),s.drawer);
  if(expected.edge)check(`${name}:selected edge drawer`,s.drawer.includes(expected.edge),s.drawer);
  check(`${name}:global node degrees`,s.globalMetrics?.nodes.every(n=>n.degree===degree(n.id)),s.globalMetrics?.nodes);
  check(`${name}:global edge metrics`,s.globalMetrics?.edges.every(e=>Object.keys(metrics(e.id)).every(k=>e[k]===metrics(e.id)[k])),s.globalMetrics?.edges);
  if(s.view==='contour'){
    check(`${name}:reader exists`,Boolean(s.current));if(expected.edge)check(`${name}:current edge`,s.current===expected.edge,{actual:s.current,expected:expected.edge});
    check(`${name}:exact distinct members`,eq(s.entities.map(e=>e.id),memberIds(s.current))&&s.entities.length===memberIds(s.current).length,{actual:s.entities.map(e=>e.id),expected:memberIds(s.current)});
    check(`${name}:one enclosure`,s.contours.length===1&&s.contours[0].id===s.current,s.contours);
    check(`${name}:regular circle`,s.contours.every(c=>Math.abs(c.aspect-1)<.001&&c.residual<.003),s.contours);
    check(`${name}:no circle collision`,s.collisions.length===0,s.collisions);
    check(`${name}:no misleading binary lines`,s.paths.length===0,s.paths);
    check(`${name}:metric cards match global graph`,s.metrics.length===3&&s.metrics.every(m=>metrics(s.current)[m.key]===m.value&&m.value===m.text),s.metrics);
    check(`${name}:member chips match global degrees`,eq(s.chips.map(c=>c.node),memberIds(s.current))&&s.chips.every(c=>c.value===degree(c.node)),s.chips);
    check(`${name}:glyph degrees and rings`,s.entities.every(e=>e.degree===degree(e.id)&&e.ring===(degree(e.id)>1)),s.entities);
    const max=Math.max(...nodeIds.map(degree));check(`${name}:degree based radius independent of text`,s.entities.every(e=>Math.abs(e.r-Math.sqrt(31**2+(Math.max(0,degree(e.id)-1)/Math.max(1,max-1))*(52**2-31**2)))<.001),s.entities.map(e=>({id:e.id,r:e.r,degree:e.degree})));
    if(s.contours[0]){const c=s.contours[0],angles=s.entities.map(e=>Math.atan2(e.y-c.cy,e.x-c.cx)).sort((a,b)=>a-b);check(`${name}:equal angular spacing`,angles.every((a,i)=>Math.abs(((angles[(i+1)%angles.length]-a+Math.PI*2)%(Math.PI*2))-Math.PI*2/angles.length)<.001),angles);}
    const ids=s.reader.tab==='edges'?(s.reader.nodeId?incident(s.reader.nodeId):edgeIds):nodeIds;
    check(`${name}:navigation scope`,eq(s.rows.map(r=>r.id),ids),{actual:s.rows.map(r=>r.id),expected:ids});
    const expectedValue=r=>r.kind==='node'?degree(r.id):metrics(r.id)[s.reader.sort];
    check(`${name}:global ranked values`,s.rows.every(r=>r.value===expectedValue(r)),s.rows);
    check(`${name}:descending stable ranks with ties`,s.rows.every((r,i)=>(!i||s.rows[i-1].value>=r.value)&&r.rank===1+s.rows.filter(x=>x.value>r.value).length),s.rows);
    const activeVisible=await page.locator('.reader-list').evaluate(e=>{const active=e.querySelector('[aria-pressed=true]');if(!active)return{hasActive:false,visible:true};const a=active.getBoundingClientRect(),b=e.getBoundingClientRect();return{hasActive:true,visible:a.top>=b.top-1&&a.bottom<=b.bottom+1,a:{top:a.top,bottom:a.bottom},b:{top:b.top,bottom:b.bottom}};});
    check(`${name}:selected navigation row visible`,activeVisible.visible,activeVisible);
    const list=await page.evaluate(()=>readerEdges().map(e=>e.id)),index=list.indexOf(s.current);check(`${name}:pager`,s.index===`${index+1} / ${list.length}`&&s.prevDisabled===(index===0)&&s.nextDisabled===(index===list.length-1),{index,list,text:s.index,prev:s.prevDisabled,next:s.nextDisabled});
    if(expected.node)check(`${name}:node filter`,s.reader.nodeId===expected.node&&incident(expected.node).includes(s.current),s.reader);
  }else if(s.view==='matrix'){
    check(`${name}:matrix full canonical sets`,eq(s.matrixRows,nodeIds)&&eq(s.matrixEdges,edgeIds));
    check(`${name}:matrix exact incidence`,eq(s.cells.map(c=>`${c.assertion}|${c.node}`),members.map(m=>`${m.assertion_id}|${m.node_id}`)));
    check(`${name}:roles preserved`,s.cells.every(c=>eq(c.roles,members.filter(m=>m.node_id===c.node&&m.assertion_id===c.assertion).map(m=>m.role))));
  }else{
    check(`${name}:no binary projection`,s.paths.every(p=>!p.pairwise));
    check(`${name}:no dangling paths`,s.paths.every(p=>s.entities.some(n=>n.id===p.node)&&Boolean(p.d)));
    if(expected.edge){check(`${name}:focused incidence members`,eq(s.entities.map(e=>e.id),memberIds(expected.edge)));check(`${name}:focused incidence edges`,eq(s.paths.map(p=>p.assertion),[expected.edge]));check(`${name}:complete incidence membership`,eq(s.paths.map(p=>p.node),memberIds(expected.edge)));}
  }
  return s;
}
const largest=[...edges].sort((a,b)=>metrics(b.id).members-metrics(a.id).members)[0].id,two=edges.find(e=>metrics(e.id).members===2)?.id,highest=[...nodes].sort((a,b)=>degree(b.id)-degree(a.id))[0].id;
try{
 if(mode==='visual'&&process.env.HK_QA_BASELINE_HASH){const text=await readFile(html,'utf8'),baseline=text.replace(/^html\[data-theme="dark"\] \.single-edge-reader \.node-inside-label\{fill:#10223b\}\r?\n/m,'');const recovered=createHash('sha256').update(baseline).digest('hex');check('Only scoped dark text CSS differs from exhaustive baseline',recovered===process.env.HK_QA_BASELINE_HASH,{recovered,expected:process.env.HK_QA_BASELINE_HASH});}
 await page.goto(pathToFileURL(html).href);await settle();await click(page.locator('[data-language="zh"]'),'language zh');await view('contour');
 await task('source',async()=>{check('source counts',nodes.length===39&&edges.length===18&&members.length===65,{nodes:nodes.length,edges:edges.length,members:members.length});check('two member hyperedges allowed',Boolean(two)&&edges.every(e=>e.topology==='hyperedge'&&memberIds(e.id).length>=2));check('exactly three views',eq(await page.locator('.representation-button').evaluateAll(es=>es.map(e=>e.dataset.representation)),['matrix','incidence','contour']));});
 for(const size of [{width:1440,height:1000},{width:1920,height:1080}])await task(`smoke-${size.width}`,async()=>{await page.setViewportSize(size);await settle();await reset();await inspect(`default-${size.width}`);await screenshot(`default-${size.width}`);await choose(two);await inspect(`two-${size.width}`,{edge:two});await screenshot(`two-member-${size.width}`);await choose(largest);await inspect(`largest-${size.width}`,{edge:largest});await screenshot(`largest-${size.width}`);await click(glyph(highest),`highest node ${size.width}`);await inspect(`node-filter-${size.width}`,{node:highest});await screenshot(`node-filter-${size.width}`);});
 await task('node-ranking-visual',async()=>{await tab('nodes');await inspect('node-ranking-visual',{node:highest});await screenshot('node-ranking-1920');await tab('edges');});
 if(mode==='visual'){
  for(const size of [{width:1920,height:1080},{width:1440,height:1000},{width:390,height:844},{width:1920,height:1080}])await task(`visual:${size.width}`,async()=>{await page.setViewportSize(size);await page.waitForTimeout(600);await choose(two);await inspect(`stable-resize:${size.width}`,{edge:two});await screenshot(`stable-resize-${size.width}`);await choose(largest);for(const v of ['matrix','incidence','contour']){await view(v);await inspect(`visual:${size.width}:${v}`,{edge:largest});await page.locator('.panel-head').first().scrollIntoViewIfNeeded();await screenshot(`visual-${size.width}-${v}`);}await click(page.locator('[data-language="en"]'),'visual en');await inspect(`visual-en:${size.width}`,{edge:largest});await screenshot(`visual-en-${size.width}`);await click(page.locator('[data-language="zh"]'),'visual zh');await click(page.locator('#theme-toggle'),'visual dark');await inspect(`visual-dark:${size.width}`,{edge:largest});await screenshot(`visual-dark-${size.width}`);await click(page.locator('#theme-toggle'),'visual light');});
  await task('scoped-dark-text-and-all-node-clicks',async()=>{
   await page.setViewportSize({width:1920,height:1080});await click(page.locator('#theme-toggle'),'delta dark');
   for(const n of nodes){await tab('nodes');await click(page.locator(`.reader-node-row[data-node=${attr(n.id)}]`),`dark ranking:${n.id}`);await click(glyph(n.id),`dark glyph:${n.id}`);await inspect(`dark-node:${n.id}`,{node:n.id});const contrast=await page.locator('.entity-mark').evaluateAll(es=>{const lum=c=>{const rgb=c.match(/[\d.]+/g).slice(0,3).map(Number).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;});return rgb[0]*.2126+rgb[1]*.7152+rgb[2]*.0722;};return es.map(e=>{const text=getComputedStyle(e.querySelector('.node-inside-label')).fill,fill=getComputedStyle(e.querySelector('.node-halo')).fill,a=lum(text),b=lum(fill);return{id:e.dataset.node,text,fill,ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)};});});check(`dark node contrast:${n.id}`,contrast.every(c=>c.ratio>=4.5),contrast);}
   await tab('nodes');await click(page.locator(`.reader-node-row[data-node=${attr(highest)}]`),'dark top node');await page.locator('.panel-head').first().scrollIntoViewIfNeeded();await screenshot('final-dark-node-ranking');await click(page.locator('#theme-toggle'),'delta light');await page.locator('.panel-head').first().scrollIntoViewIfNeeded();await screenshot('final-light-node-ranking');
   await page.setViewportSize({width:390,height:844});await page.waitForTimeout(500);await choose(largest);await page.locator('.single-edge-reader .canvas-wrap').scrollIntoViewIfNeeded();await screenshot('final-mobile-scrolled-circle');await inspect('mobile scrolled circle',{edge:largest});
  });
 }
 if(mode==='full'){
  await page.setViewportSize({width:1440,height:1000});await reset();
  for(const edge of edges)await task(`edge:${edge.id}`,async()=>{
   await choose(edge.id);await inspect(`edge:${edge.id}`,{edge:edge.id});
   for(const target of ['title','outline','fill']){const locator=page.locator(`.${target==='title'?'hyperedge-label':target==='outline'?'hyper-envelope':'hyper-envelope-fill'}[data-assertion=${attr(edge.id)}]${target==='title'?' .label-block-bg':''}`);await click(locator,`${target}:${edge.id}`,target==='outline'?'path':target==='fill'?'fill':'box');await inspect(`${target}:${edge.id}`,{edge:edge.id});}
   for(const node of memberIds(edge.id)){await choose(edge.id);await click(glyph(node),`glyph:${edge.id}:${node}`);await inspect(`glyph:${edge.id}:${node}`,{node});await choose(edge.id);await click(page.locator(`.reader-node-degree[data-node=${attr(node)}]`),`degree-chip:${edge.id}:${node}`);await inspect(`chip:${edge.id}:${node}`,{node});}
  });
  for(const sort of ['shared','members','neighbors'])await task(`sort-and-pager:${sort}`,async()=>{
   await clear();await tab('edges');await page.locator('.reader-sort').selectOption(sort);report.interactions.push({name:`sort:${sort}`,kind:'native-select'});await settle();await inspect(`sort:${sort}`);const ids=await page.locator('.reader-edge-row').evaluateAll(es=>es.map(e=>e.dataset.assertion));await click(edgeRow(ids[0]),`first:${sort}`);
   for(let i=0;i<ids.length;i++){await inspect(`pager-forward:${sort}:${i}`,{edge:ids[i]});if(i<ids.length-1)await click(page.locator('.reader-next'),`next:${sort}:${i}`);}
   for(let i=ids.length-1;i>0;i--){await click(page.locator('.reader-prev'),`prev:${sort}:${i}`);await inspect(`pager-back:${sort}:${i}`,{edge:ids[i-1]});}
  });
  for(const node of nodes)await task(`node-ranking:${node.id}`,async()=>{await tab('nodes');await click(page.locator(`.reader-node-row[data-node=${attr(node.id)}]`),`node-rank:${node.id}`);await inspect(`node-ranking:${node.id}`,{node:node.id});await tab('edges');await inspect(`node-edges:${node.id}`,{node:node.id});for(const id of incident(node.id)){await click(edgeRow(id),`filtered-edge:${node.id}:${id}`);await inspect(`filtered-edge:${node.id}:${id}`,{edge:id,node:node.id});}await clear();await inspect(`clear-node:${node.id}`);});
  for(const node of nodes)await task(`matrix-node:${node.id}`,async()=>{await view('matrix');await click(page.locator(`.matrix-row-label[data-node=${attr(node.id)}]`),`matrix-node:${node.id}`);for(const v of ['matrix','incidence','contour','matrix','contour']){await view(v);await inspect(`matrix-node:${node.id}:${v}`,{node:node.id});}await clear();});
  for(const edge of edges)await task(`cross-view:${edge.id}`,async()=>{await choose(edge.id);for(const v of ['matrix','incidence','contour']){await view(v);await inspect(`cross-view:${edge.id}:${v}`,{edge:edge.id});}await view('incidence');for(const node of memberIds(edge.id)){await click(page.locator(`#drawer-body .member-row[data-node=${attr(node)}]`),`drawer-member:${edge.id}:${node}`);await view('contour');await inspect(`drawer-member:${edge.id}:${node}`,{node});await choose(edge.id);await view('incidence');}await view('contour');});
  for(const m of members)await task(`matrix-cell:${m.assertion_id}:${m.node_id}`,async()=>{await view('matrix');await click(page.locator(`.matrix-cell[data-assertion=${attr(m.assertion_id)}][data-node=${attr(m.node_id)}]`),`matrix-cell:${m.assertion_id}:${m.node_id}`);await view('contour');await inspect(`matrix-cell:${m.assertion_id}:${m.node_id}`,{edge:m.assertion_id});});
  for(const e of edges)await task(`hover:${e.id}`,async()=>{await choose(e.id);const fill=page.locator('.hyper-envelope-fill'),label=page.locator('.hyperedge-label .label-block-bg');await page.mouse.move(1,1);await page.waitForTimeout(250);const before=await fill.evaluate(e=>getComputedStyle(e).fill);await label.hover();await page.waitForTimeout(350);const after=await fill.evaluate(e=>getComputedStyle(e).fill);check(`hover tint ${e.id}`,before!==after,{before,after});check(`hover member set ${e.id}`,eq(await page.locator('.entity-mark:not(.is-hover-muted)').evaluateAll(es=>es.map(e=>e.dataset.node)),memberIds(e.id)));if(e.id===largest)await screenshot('hover-largest');await page.mouse.move(1,1);await page.waitForTimeout(250);check(`hover clear ${e.id}`,await fill.evaluate(e=>!e.classList.contains('is-hover-focus')));});
  await task('drag-and-controls',async()=>{
   await choose(largest);const n=memberIds(largest)[0];await glyph(n).scrollIntoViewIfNeeded();const before=await glyph(n).evaluate(e=>e.parentElement.getAttribute('transform')),b=await glyph(n).boundingBox();await page.mouse.move(b.x+b.width/2,b.y+b.height/2);await page.mouse.down();await page.mouse.move(b.x+b.width/2+90,b.y+b.height/2+50,{steps:20});await page.mouse.up();await settle();const after=await glyph(n).evaluate(e=>e.parentElement.getAttribute('transform'));check('drag changes ring position',before!==after,{before,after});await inspect('after-drag',{edge:largest});await screenshot('drag');await reset();await choose(largest);check('reset restores initial coordinates',before===await glyph(n).evaluate(e=>e.parentElement.getAttribute('transform')));
   for(const action of ['zoom-in','zoom-out','reset'])await click(page.locator(`[data-action=${attr(action)}]`),action);
   await click(page.locator('.reader-method summary'),'metric definitions');check('metric definitions expanded',await page.locator('.reader-method').getAttribute('open')!==null);
   await choose(two);const label=page.locator('.hyperedge-label');await label.focus();await page.keyboard.press('Enter');await settle();await inspect('keyboard edge',{edge:two});check('keyboard edge retains focus',await page.evaluate(()=>document.activeElement?.classList.contains('hyperedge-label')));
  });
  for(const size of [{width:1440,height:1000},{width:1920,height:1080},{width:390,height:844}])await task(`responsive:${size.width}`,async()=>{
   await page.setViewportSize(size);await settle();await view('contour');await reset();await choose(largest);
   for(const v of ['matrix','incidence','contour']){await view(v);await inspect(`responsive:${size.width}:${v}`,{edge:largest});await screenshot(`responsive-${size.width}-${v}`);}
   for(const language of ['en','zh']){await click(page.locator(`[data-language=${attr(language)}]`),`language:${language}`);await inspect(`language:${size.width}:${language}`,{edge:largest});await screenshot(`language-${size.width}-${language}`);}
   for(const theme of ['dark','light']){await click(page.locator('#theme-toggle'),`theme:${theme}`);check(`theme ${theme}`,await page.locator('html').getAttribute('data-theme')===theme);await inspect(`theme:${size.width}:${theme}`,{edge:largest});await screenshot(`theme-${size.width}-${theme}`);}
   await tab('nodes');await click(page.locator(`.reader-node-row[data-node=${attr(nodeIds[nodeIds.length-1])}]`),'last rank node');await inspect(`last-node:${size.width}`,{node:nodeIds[nodeIds.length-1]});
  });
 }
}catch(e){report.errors.push(e.stack);}
finally{report.sourceUnchanged=report.sha256===await hash();report.finishedAt=new Date().toISOString();report.passed=report.sourceUnchanged&&report.errors.length===0&&report.blockedNetwork.length===0&&report.checks.every(c=>c.ok);report.totals={interactions:report.interactions.length,states:report.states.length,checks:report.checks.length,failed:report.checks.filter(c=>!c.ok).length};await writeFile(join(output,'reader-report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({passed:report.passed,sourceUnchanged:report.sourceUnchanged,...report.totals,errors:report.errors,failures:report.checks.filter(c=>!c.ok),screenshots:report.screenshots}));await browser.close();if(!report.passed)process.exitCode=1;}
