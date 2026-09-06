/**
 * Isolated-Chrome pointer audit for a full hypergraph overview.
 * node tools/check_hypergraph_overview.mjs HTML BUNDLE OUTPUT [smoke|full]
 * HK_PLAYWRIGHT_MODULE and HK_BROWSER_EXECUTABLE select managed local runtimes.
 * Never opens a personal profile or permits external HTTP requests.
 */
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const require=createRequire(import.meta.url),{chromium}=require(process.env.HK_PLAYWRIGHT_MODULE||'playwright');
const [htmlArg,bundleArg,outArg,mode='full']=process.argv.slice(2);
if(!htmlArg||!bundleArg||!outArg)throw new Error('Expected HTML BUNDLE OUTPUT [smoke|full]');
const html=resolve(htmlArg),bundle=resolve(bundleArg),output=resolve(outArg),settleMs=Number(process.env.HK_QA_SETTLE_MS||90);
await mkdir(output,{recursive:true});
const jsonl=async name=>(await readFile(join(bundle,name),'utf8')).split(/\r?\n/).filter(Boolean).map(JSON.parse);
const [nodes,edges,members]=await Promise.all(['nodes.jsonl','assertions.jsonl','members.jsonl'].map(jsonl));
const uniq=list=>[...new Set(list.map(String))].sort(),equal=(a,b)=>JSON.stringify(uniq(a))===JSON.stringify(uniq(b)),attr=JSON.stringify;
const nodeIds=nodes.map(n=>n.id),edgeIds=edges.map(e=>e.id),memberIds=id=>uniq(members.filter(m=>m.assertion_id===id).map(m=>m.node_id)),incident=id=>uniq(members.filter(m=>m.node_id===id).map(m=>m.assertion_id));
const expectedPairs=uniq(members.map(m=>`${m.assertion_id}|${m.node_id}`));
const digest=bytes=>createHash('sha256').update(bytes).digest('hex'),hash=async()=>digest(await readFile(html));
const report={html,bundle,mode,sha256:await hash(),startedAt:new Date().toISOString(),checks:[],states:[],interactions:[],errors:[],blockedNetwork:[],screenshots:[]};
const check=(name,ok,detail={})=>{report.checks.push({name,ok:Boolean(ok),detail});return ok;};
const browser=await chromium.launch({headless:true,executablePath:process.env.HK_BROWSER_EXECUTABLE||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
const context=await browser.newContext({viewport:{width:1920,height:1080},deviceScaleFactor:1,locale:'zh-CN',colorScheme:'light'}),page=await context.newPage();
page.setDefaultTimeout(4500);page.on('pageerror',e=>report.errors.push({kind:'pageerror',message:e.stack}));page.on('console',m=>{if(m.type()==='error')report.errors.push({kind:'console',message:m.text()});});
await page.route(/^https?:/,route=>{report.blockedNetwork.push(route.request().url());return route.abort();});
const settle=()=>page.waitForTimeout(settleMs);let imageIndex=0;
async function shot(name){if(!name.includes('hover')){await page.mouse.move(1,1);await settle();}const path=join(output,`${String(++imageIndex).padStart(3,'0')}-${name.replace(/[^a-z0-9_-]/gi,'-')}.png`);await page.screenshot({path,fullPage:false});report.screenshots.push(path);return path;}
async function task(name,fn){const start=report.checks.length;try{await fn();}catch(e){check(name,false,{error:e.stack});}const failed=report.checks.slice(start).filter(c=>!c.ok);if(failed.length){const image=await shot(`FAIL-${name}`);failed.forEach(c=>c.screenshot=image);}console.log(JSON.stringify({task:name,checks:report.checks.length-start,failed:failed.length}));}
async function pointer(locator,name,kind='click'){
 locator=locator.first();if(!await locator.count())throw new Error(`Missing ${name}`);await locator.scrollIntoViewIfNeeded();await settle();
 const point=await locator.evaluate(e=>{const b=e.getBoundingClientRect(),m=e.getScreenCTM?.();if(e.getTotalLength&&e.tagName.toLowerCase()==='path'){for(let i=0,length=e.getTotalLength();i<90;i++){const local=e.getPointAtLength(length*(i+.5)/90),p=new DOMPoint(local.x,local.y).matrixTransform(m);if(p.x<0||p.y<0||p.x>=innerWidth||p.y>=innerHeight)continue;const hit=document.elementFromPoint(p.x,p.y);if(hit===e||e.contains(hit))return{x:p.x,y:p.y};}return null;}return{x:b.x+b.width/2,y:b.y+b.height/2};});
 if(!point)throw new Error(`No exposed pointer target ${name}`);
 const hit=await page.evaluate(p=>{const e=document.elementFromPoint(p.x,p.y),a=e?.closest('[data-assertion]'),n=e?.closest('[data-node]');return{tag:e?.tagName,class:e?.getAttribute('class'),assertion:a?.dataset.assertion,node:n?.dataset.node};},point);
 report.interactions.push({name,kind,point,hit});if(kind==='hover')await page.mouse.move(point.x,point.y);else await page.mouse.click(point.x,point.y);await settle();return point;
}
const degree=id=>incident(id).length;
const nodeMark=id=>page.locator(`.overview-node[data-node=${attr(id)}] .node-halo`),edgeMark=id=>page.locator(`.overview-edge[data-assertion=${attr(id)}] .overview-edge-label`),linkMark=(e,n)=>page.locator(`.overview-link[data-assertion=${attr(e)}][data-node=${attr(n)}]`);
const park=async()=>{await page.mouse.move(1,1);await settle();};
const view=async id=>{await pointer(page.locator(`[data-representation=${attr(id)}]`),`view:${id}`);check(`view button:${id}`,await page.locator(`[data-representation=${attr(id)}]`).getAttribute('aria-pressed')==='true');};
const clear=async()=>{await pointer(page.locator('.overview-clear'),'clear overview');await park();};
const reset=async()=>{await pointer(page.locator('[data-action="reset"]'),'reset');await park();};
async function readState(){return page.evaluate(()=>{
 const all=s=>[...document.querySelectorAll(s)],box=e=>{const b=e.getBoundingClientRect();return{x:b.x,y:b.y,width:b.width,height:b.height};};
 const status=e=>({hidden:e.classList.contains('is-hidden')||getComputedStyle(e).display==='none'||getComputedStyle(e).visibility==='hidden',related:e.classList.contains('is-overview-related'),muted:e.classList.contains('is-overview-muted'),selected:e.classList.contains('is-selected'),opacity:Number(getComputedStyle(e).opacity)});
 const nodes=all('.overview-node').map(e=>({id:e.dataset.node,degree:Number(e.dataset.hyperedgeDegree),ring:e.dataset.ring,sharedRing:!!e.querySelector('.shared-ring'),r:Number(e.querySelector('.node-halo')?.getAttribute('r')),transform:e.getAttribute('transform'),box:box(e.querySelector('.node-halo')),...status(e)}));
 const edges=all('.overview-edge').map(e=>({id:e.dataset.assertion,transform:e.getAttribute('transform'),box:box(e.querySelector('.overview-edge-label')),...status(e)}));
 const links=all('.overview-link').map(e=>({assertion:e.dataset.assertion,node:e.dataset.node,d:e.getAttribute('d'),...status(e)}));
 const canvas=document.querySelector('.hypergraph-overview .canvas-wrap'),svg=document.querySelector('.hypergraph-overview .network-svg');
 return{view:document.querySelector('.representation-button[aria-pressed=true]')?.dataset.representation,theme:document.documentElement.dataset.theme,nodes,edges,links,viewport:document.querySelector('.hypergraph-overview .viewport')?.getAttribute('transform'),viewBox:svg?.getAttribute('viewBox'),svgBox:svg?box(svg):null,canvas:canvas?{box:box(canvas),width:canvas.clientWidth,height:canvas.clientHeight,scrollWidth:canvas.scrollWidth,scrollLeft:canvas.scrollLeft,overflow:getComputedStyle(canvas).overflow}:null,drawer:all('#drawer-body .detail-grid dd').map(e=>e.textContent.trim()),focusLabel:document.querySelector('.overview-focus-label')?.textContent,tooltip:document.querySelector('.hypergraph-overview .tooltip.visible')?.textContent||null,readerEdge:document.querySelector('.single-edge-reader')?.dataset.currentAssertion,readerNodes:all('.single-edge-reader .entity-mark').map(e=>e.dataset.node),globalHorizontalOverflow:document.documentElement.scrollWidth>innerWidth,scroll:{x:scrollX,y:scrollY},width:innerWidth,height:innerHeight};
 });}
const geometry=s=>JSON.stringify({nodes:s.nodes.map(n=>[n.id,n.transform,n.r]),edges:s.edges.map(e=>[e.id,e.transform]),links:s.links.map(l=>[l.assertion,l.node,l.d]),viewport:s.viewport,viewBox:s.viewBox});
async function inspect(name,{focus=null,selected=null,baseline=null}={}){
 const s=await readState();s.name=name;report.states.push(s);
 check(`${name}:overview retained`,s.view==='overview');
 check(`${name}:39 unique canonical entities`,s.nodes.length===nodeIds.length&&equal(s.nodes.map(n=>n.id),nodeIds));
 check(`${name}:18 original hyperedges`,s.edges.length===edgeIds.length&&equal(s.edges.map(e=>e.id),edgeIds));
 check(`${name}:65 exact memberships`,s.links.length===expectedPairs.length&&equal(s.links.map(l=>`${l.assertion}|${l.node}`),expectedPairs));
 check(`${name}:nothing removed or hidden`,[...s.nodes,...s.edges,...s.links].every(e=>!e.hidden));
 check(`${name}:global degrees and shared rings`,s.nodes.every(n=>n.degree===degree(n.id)&&n.sharedRing===(degree(n.id)>1)));
 check(`${name}:all paths nonempty`,s.links.every(l=>Boolean(l.d)));
 if(baseline)check(`${name}:layout remains fixed`,geometry(s)===geometry(baseline));
 const focusedEdges=focus?(focus.kind==='node'?incident(focus.id):[focus.id]):[],focusedNodes=focus?uniq([...(focus.kind==='node'?[focus.id]:[]),...focusedEdges.flatMap(memberIds)]):[];
 check(`${name}:exact highlight edges`,equal(s.edges.filter(e=>e.related).map(e=>e.id),focusedEdges));
 check(`${name}:exact highlight entities`,equal(s.nodes.filter(n=>n.related).map(n=>n.id),focusedNodes));
 check(`${name}:exact highlight memberships`,equal(s.links.filter(l=>l.related).map(l=>`${l.assertion}|${l.node}`),expectedPairs.filter(p=>focusedEdges.some(e=>p.startsWith(`${e}|`)))));
 check(`${name}:focus only dims unrelated`,[...s.nodes,...s.edges,...s.links].every(e=>e.muted===(Boolean(focus)&&!e.related)));
 if(selected){check(`${name}:drawer selection`,s.drawer.includes(selected.id),{drawer:s.drawer,id:selected.id});check(`${name}:selection mark`,selected.kind==='node'?equal(s.nodes.filter(n=>n.selected).map(n=>n.id),[selected.id]):equal(s.edges.filter(e=>e.selected).map(e=>e.id),[selected.id]));}
 else check(`${name}:no persistent selection`,[...s.nodes,...s.edges].every(e=>!e.selected));
 return s;
}
async function panelShot(name){await page.locator('.hypergraph-overview .panel-head').scrollIntoViewIfNeeded();await shot(name);}
async function theme(name){if(await page.locator('html').getAttribute('data-theme')!==name)await pointer(page.locator('#theme-toggle'),`theme:${name}`);check(`theme:${name}`,await page.locator('html').getAttribute('data-theme')===name);}
async function readerCheck(name,edge=null,node=null){const s=await readState();s.name=name;report.states.push(s);check(`${name}:reader view`,s.view==='contour'&&Boolean(s.readerEdge));if(edge)check(`${name}:chosen edge`,s.readerEdge===edge,{expected:edge,actual:s.readerEdge});if(node)check(`${name}:chosen node incidence`,incident(node).includes(s.readerEdge));check(`${name}:reader exact members`,equal(s.readerNodes,memberIds(s.readerEdge))&&s.readerNodes.length===memberIds(s.readerEdge).length);check(`${name}:one contour`,await page.locator('.single-edge-reader .hyper-envelope').count()===1);}
const largest=[...edges].sort((a,b)=>memberIds(b.id).length-memberIds(a.id).length)[0].id,highest=[...nodes].sort((a,b)=>degree(b.id)-degree(a.id))[0].id;
try{
 if(process.env.HK_QA_EXPECTED_HASH&&report.sha256!==process.env.HK_QA_EXPECTED_HASH)throw new Error(`Export hash mismatch: ${report.sha256}`);
 await page.goto(pathToFileURL(html).href);await settle();
 await task('source-and-default',async()=>{check('source canonical counts',nodes.length===39&&edges.length===18&&members.length===65,{nodes:nodes.length,edges:edges.length,members:members.length,pairs:expectedPairs.length});check('four existing-and-new views',equal(await page.locator('.representation-button').evaluateAll(es=>es.map(e=>e.dataset.representation)),['overview','contour','matrix','incidence']));check('default light',await page.locator('html').getAttribute('data-theme')==='light');await inspect('default');await shot('default-1920-light-app');});
 for(const size of [{width:1920,height:1080},{width:1440,height:1000}])await task(`preview:${size.width}`,async()=>{
  await page.setViewportSize(size);await page.waitForTimeout(500);await view('overview');await reset();
  for(const name of ['light','dark']){await theme(name);await park();const before=await inspect(`preview:${size.width}:${name}`);await panelShot(`overview-${size.width}-${name}`);await pointer(edgeMark(largest),`hover:${size.width}:${name}:edge:${largest}`,'hover');await inspect(`hover:${size.width}:${name}`,{focus:{kind:'assertion',id:largest},baseline:before});await shot(`overview-${size.width}-${name}-hover`);await park();await inspect(`hover-cleared:${size.width}:${name}`,{baseline:before});}
 });
 if(mode==='full'){
  await page.setViewportSize({width:1920,height:1080});await page.waitForTimeout(500);await view('overview');await theme('light');await reset();
  for(const e of edges)await task(`edge:${e.id}`,async()=>{await clear();const before=await inspect(`before-edge:${e.id}`);const selected={kind:'assertion',id:e.id};await pointer(edgeMark(e.id),`edge-hover:${e.id}`,'hover');await inspect(`edge-hover:${e.id}`,{focus:selected,baseline:before});check(`edge tooltip:${e.id}`,Boolean((await readState()).tooltip));await pointer(edgeMark(e.id),`edge-click:${e.id}`);await park();await inspect(`edge-selected:${e.id}`,{focus:selected,selected,baseline:before});await pointer(page.locator('.overview-read'),`read-edge:${e.id}`);await readerCheck(`reader-edge:${e.id}`,e.id);await pointer(page.locator('.overview-return'),`return-edge:${e.id}`);await park();await inspect(`return-edge:${e.id}`,{focus:selected,selected,baseline:before});});
  for(const n of nodes)await task(`node:${n.id}`,async()=>{await clear();const before=await inspect(`before-node:${n.id}`),selected={kind:'node',id:n.id};await pointer(nodeMark(n.id),`node-hover:${n.id}`,'hover');await inspect(`node-hover:${n.id}`,{focus:selected,baseline:before});check(`node tooltip:${n.id}`,Boolean((await readState()).tooltip));await pointer(nodeMark(n.id),`node-click:${n.id}`);await park();await inspect(`node-selected:${n.id}`,{focus:selected,selected,baseline:before});await pointer(page.locator('.overview-read'),`read-node:${n.id}`);await readerCheck(`reader-node:${n.id}`,null,n.id);await view('overview');await park();await inspect(`return-node:${n.id}`,{focus:selected,selected,baseline:before});});
  for(const pair of expectedPairs)await task(`membership:${pair}`,async()=>{await clear();const [e,n]=pair.split('|'),before=await inspect(`before-link:${pair}`),selected={kind:'assertion',id:e};await pointer(linkMark(e,n),`link-hover:${pair}`,'hover');await inspect(`link-hover:${pair}`,{focus:selected,baseline:before});const tooltip=(await readState()).tooltip,sourceRoles=uniq(members.filter(m=>m.assertion_id===e&&m.node_id===n).map(m=>m.role));check(`membership role tooltip:${pair}`,Boolean(tooltip)&&sourceRoles.every(role=>tooltip.includes(role)),{tooltip,sourceRoles});await pointer(linkMark(e,n),`link-click:${pair}`);await park();await inspect(`link-selected:${pair}`,{focus:selected,selected,baseline:before});});
  await task('selection-hover-restoration',async()=>{await clear();await pointer(nodeMark(highest),'select highest');await park();const selected={kind:'node',id:highest},before=await inspect('highest-selected',{selected,focus:selected});await pointer(edgeMark(largest),'hover edge with node selected','hover');await inspect('transient edge focus',{selected,focus:{kind:'assertion',id:largest},baseline:before});await park();await inspect('node selection restored after hover',{selected,focus:selected,baseline:before});await clear();await inspect('clear returns full overview');});
  await task('pan-zoom-reset',async()=>{await clear();const before=await inspect('before-pan-zoom');await pointer(page.locator('[data-action="zoom-in"]'),'zoom in');check('zoom increases scale',(await readState()).viewport!==before.viewport);await pointer(page.locator('[data-action="zoom-out"]'),'zoom out');check('zoom out restores scale',(await readState()).viewport===before.viewport);await page.locator('.hypergraph-overview .network-svg').scrollIntoViewIfNeeded();const point=await page.locator('.hypergraph-overview .network-svg').evaluate(e=>{const r=e.getBoundingClientRect();for(let x=30;x<r.width-100;x+=37)for(let y=30;y<r.height-100;y+=41){const p={x:r.x+x,y:r.y+y};if(p.x>0&&p.y>0&&p.x<innerWidth-100&&p.y<innerHeight-100&&document.elementFromPoint(p.x,p.y)===e)return p;}return null;});if(!point)throw new Error('No visible empty SVG point for pan');await page.mouse.move(point.x,point.y);await page.mouse.down();await page.mouse.move(point.x+70,point.y+45,{steps:12});await page.mouse.up();await settle();report.interactions.push({name:'pan empty canvas',kind:'drag',point});check('pan changes viewport transform',(await readState()).viewport!==before.viewport);await reset();await inspect('reset restores overview',{baseline:before});await pointer(nodeMark(highest),'select before reset');await reset();await inspect('reset clears selection',{baseline:before});});
  for(const size of [{width:1920,height:1080},{width:1440,height:1000},{width:390,height:844}])await task(`responsive:${size.width}`,async()=>{await page.setViewportSize(size);await page.waitForTimeout(550);await view('overview');await reset();for(const name of ['light','dark']){await theme(name);const s=await inspect(`responsive:${size.width}:${name}`);check(`no page horizontal overflow:${size.width}:${name}`,!s.globalHorizontalOverflow);if(size.width<720)check(`mobile graph scrolls locally:${name}`,s.canvas.scrollWidth>s.canvas.width&&['auto','scroll'].includes(s.canvas.overflow),s.canvas);await panelShot(`responsive-${size.width}-${name}-top`);await page.locator('.hypergraph-overview .panel-foot').scrollIntoViewIfNeeded();await shot(`responsive-${size.width}-${name}-bottom`);}
   await pointer(nodeMark(highest),`responsive select:${size.width}`);await park();await inspect(`responsive-selected:${size.width}`,{selected:{kind:'node',id:highest},focus:{kind:'node',id:highest}});await pointer(page.locator('.overview-read'),`responsive read:${size.width}`);await readerCheck(`responsive-reader:${size.width}`,null,highest);await pointer(page.locator('.overview-return'),`responsive return:${size.width}`);await park();await inspect(`responsive-return:${size.width}`,{selected:{kind:'node',id:highest},focus:{kind:'node',id:highest}});
   for(const other of ['matrix','incidence']){await view(other);check(`existing view retained:${size.width}:${other}`,await page.locator(`[data-representation=${attr(other)}]`).getAttribute('aria-pressed')==='true');await view('overview');await park();await inspect(`return-from-${other}:${size.width}`,{selected:{kind:'node',id:highest},focus:{kind:'node',id:highest}});}
  });
 }
}
catch(e){report.errors.push({kind:'fatal',message:e.stack});}
finally{report.sourceHashAfter=await hash();report.sourceUnchanged=report.sha256===report.sourceHashAfter;report.finishedAt=new Date().toISOString();report.passed=report.sourceUnchanged&&report.errors.length===0&&report.blockedNetwork.length===0&&report.checks.every(c=>c.ok);report.totals={interactions:report.interactions.length,states:report.states.length,checks:report.checks.length,failed:report.checks.filter(c=>!c.ok).length};await writeFile(join(output,'overview-report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({passed:report.passed,sourceUnchanged:report.sourceUnchanged,...report.totals,sha256:report.sha256,errors:report.errors,failures:report.checks.filter(c=>!c.ok)}));await browser.close();if(!report.passed)process.exitCode=1;}
