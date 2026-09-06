/** Read-only pointer-focus diagnosis; isolated Chrome, frozen file URL only. */
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const require=createRequire(import.meta.url),{chromium}=require(process.env.HK_PLAYWRIGHT_MODULE||'playwright');
const [htmlArg,outArg,mode='marks']=process.argv.slice(2);
if(!htmlArg||!outArg)throw new Error('Expected HTML OUTPUT');
const html=resolve(htmlArg),output=resolve(outArg),sha=async()=>createHash('sha256').update(await readFile(html)).digest('hex');
const report={html,sha256:await sha(),startedAt:new Date().toISOString(),states:[],blockedNetwork:[],errors:[]};
if(process.env.HK_QA_EXPECTED_HASH&&report.sha256!==process.env.HK_QA_EXPECTED_HASH)throw new Error(`Export hash mismatch: ${report.sha256}`);
if(mode==='final'){
 const addedSelector=',.hypergraph-overview .overview-link:focus',source=await readFile(html,'utf8'),reverted=source.replace(addedSelector,'');
 report.controlledDiff={removedSelector:addedSelector,occurrences:source.split(addedSelector).length-1,priorHashFromInMemoryRevert:createHash('sha256').update(reverted).digest('hex'),expectedPriorHash:'61c7ff3e12cea2d7ed2d64563db5c9003bfde4af6a8d292907aea4c09ee99f9a'};
 report.controlledDiff.onlyExpectedCssChange=report.controlledDiff.occurrences===1&&report.controlledDiff.priorHashFromInMemoryRevert===report.controlledDiff.expectedPriorHash;
 if(!report.controlledDiff.onlyExpectedCssChange)throw new Error('The final delta is not the expected CSS selector alone');
 report.frozenPath='E:/GitHub/Hyper-Knowledge/examples/sushi-local-preview/views/workbench.html';report.frozenHash=createHash('sha256').update(await readFile(report.frozenPath)).digest('hex');
}
await mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
try{
 const context=await browser.newContext({viewport:{width:1920,height:1080},locale:'zh-CN',colorScheme:'light'}),page=await context.newPage();
 page.on('pageerror',e=>report.errors.push(e.stack));
 await page.route(/^https?:/,route=>{report.blockedNetwork.push(route.request().url());return route.abort();});
 await page.goto(pathToFileURL(html).href);await page.waitForTimeout(300);
 if(mode==='final')await page.screenshot({path:join(output,'001-final-overview-light.png'),fullPage:false});
 async function click(locator){await locator.scrollIntoViewIfNeeded();const p=await locator.evaluate(e=>{if(e.classList.contains('overview-link')){const matrix=e.getScreenCTM(),length=e.getTotalLength();for(let i=0;i<160;i++){const at=e.getPointAtLength(length*(i+.5)/160),p=new DOMPoint(at.x,at.y).matrixTransform(matrix);if(p.x>=0&&p.y>=0&&p.x<innerWidth&&p.y<innerHeight&&document.elementFromPoint(p.x,p.y)===e)return{x:p.x,y:p.y};}return null;}const b=e.getBoundingClientRect();return{x:b.x+b.width/2,y:b.y+b.height/2};});if(!p)throw new Error('No exposed real pointer target');const hit=await page.evaluate(p=>{const e=document.elementFromPoint(p.x,p.y);return{tag:e?.tagName,class:e?.getAttribute('class')};},p);await page.mouse.click(p.x,p.y);await page.mouse.move(1,1);await page.waitForTimeout(350);return{point:p,hit};}
 const targets=['links','final'].includes(mode)?await page.locator('.overview-link').evaluateAll(es=>es.slice(0,3).map(e=>({class:'overview-link',id:e.dataset.assertion,node:e.dataset.node,attribute:'data-assertion'}))):await page.locator('.overview-node[data-node="person:su-shi"],.overview-edge').evaluateAll(es=>[es.find(e=>e.classList.contains('overview-node')),es.find(e=>e.classList.contains('overview-edge'))].map(e=>({class:e.classList.contains('overview-node')?'overview-node':'overview-edge',id:e.dataset.node||e.dataset.assertion,attribute:e.dataset.node?'data-node':'data-assertion'})));
 if(mode==='final')targets.push({class:'overview-node',id:'person:su-zhe',attribute:'data-node'},{class:'overview-edge',id:'assertion:west-lake-governance-1089',attribute:'data-assertion'});
 for(const t of targets){
  const selector=`.${t.class}[${t.attribute}=${JSON.stringify(t.id)}]${t.node?`[data-node=${JSON.stringify(t.node)}]`:''}`,owner=page.locator(selector),shape=t.class==='overview-link'?owner:owner.locator(t.class==='overview-node'?'.node-halo':'.overview-edge-label'),interaction=await click(shape);
  const state=await owner.evaluate(e=>{
   const cs=getComputedStyle(e),active=document.activeElement,style={outline:cs.outline,outlineStyle:cs.outlineStyle,outlineWidth:cs.outlineWidth,outlineColor:cs.outlineColor,outlineOffset:cs.outlineOffset,filter:cs.filter},authorOutlineRules=[];
   function inspectRules(rules){for(const rule of rules){if(rule.selectorText){let matches=false;try{matches=e.matches(rule.selectorText);}catch{}if(matches&&/outline/.test(rule.style?.cssText||''))authorOutlineRules.push({selector:rule.selectorText,css:rule.style.cssText});}if(rule.cssRules)inspectRules(rule.cssRules);}}
   for(const sheet of document.styleSheets)inspectRules(sheet.cssRules);
   const child=e.querySelector('.node-halo,.overview-edge-label')||e,s=getComputedStyle(child);
   return{owner:{tag:e.tagName,class:e.getAttribute('class'),tabindex:e.getAttribute('tabindex'),focus:e.matches(':focus'),focusVisible:e.matches(':focus-visible')},activeElement:{tag:active?.tagName,class:active?.getAttribute('class'),node:active?.dataset.node,assertion:active?.dataset.assertion,isOwner:active===e},style,authorOutlineRules,shape:{tag:child.tagName,outline:s.outline,stroke:s.stroke,strokeWidth:s.strokeWidth,filter:s.filter}};
  });
  const screenshot=join(output,`${t.class}-${report.states.length+1}-mouse-selected.png`);await page.screenshot({path:screenshot,fullPage:false});report.states.push({target:t,interaction,...state,screenshot});
  if(mode==='final'&&t.class!=='overview-link'){
   await page.keyboard.press('Shift+Tab');await page.keyboard.press('Tab');await page.mouse.move(1,1);await page.waitForTimeout(250);
   const keyboard=await owner.evaluate(e=>{const c=getComputedStyle(e),shape=e.querySelector('.node-halo,.overview-edge-label'),s=getComputedStyle(shape);return{activeIsOwner:document.activeElement===e,focusVisible:e.matches(':focus-visible'),outlineStyle:c.outlineStyle,shape:shape.tagName,stroke:s.stroke,strokeWidth:Number.parseFloat(s.strokeWidth)};});
   report.states.at(-1).keyboard=keyboard;await page.screenshot({path:join(output,`${t.class}-keyboard-shape.png`),fullPage:false});
  }
  await click(page.locator('.overview-clear'));
 }
 if(mode==='final'){
  await click(page.locator('#theme-toggle'));await page.screenshot({path:join(output,'002-final-overview-dark.png'),fullPage:false});
  for(const t of targets.filter(t=>t.class!=='overview-link')){const owner=page.locator(`.${t.class}[${t.attribute}=${JSON.stringify(t.id)}]`);await click(owner.locator(t.class==='overview-node'?'.node-halo':'.overview-edge-label'));await page.screenshot({path:join(output,`${t.class}-final-selected-dark.png`),fullPage:false});await click(page.locator('.overview-clear'));}
 }
}finally{await browser.close();report.hashAfter=await sha();report.sourceUnchanged=report.hashAfter===report.sha256;if(mode==='final'){report.frozenHashAfter=createHash('sha256').update(await readFile(report.frozenPath)).digest('hex');report.frozenUnchanged=report.frozenHashAfter===report.frozenHash&&report.frozenHash==='7652b2a8fd07d7c7927fe1bc1d24fe6284851cd465ea64c834c73e41c6b8e254';report.passed=report.sourceUnchanged&&report.frozenUnchanged&&report.controlledDiff.onlyExpectedCssChange&&report.errors.length===0&&report.blockedNetwork.length===0&&report.states.every(s=>s.owner.focus&&s.activeElement.isOwner&&s.style.outlineStyle==='none'&&(!s.keyboard||(s.keyboard.activeIsOwner&&s.keyboard.focusVisible&&s.keyboard.outlineStyle==='none'&&s.keyboard.strokeWidth===(s.keyboard.shape.toLowerCase()==='circle'?4:3))));}report.finishedAt=new Date().toISOString();await writeFile(join(output,'focus-diagnosis.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));if(report.passed===false)process.exitCode=1;}
