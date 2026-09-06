// CSS-only delta audit after the exhaustive pointer suite.
// node tools/check_workbench_hover.mjs HTML BUNDLE OUTPUT BASELINE_HTML
// Optional HK_PLAYWRIGHT_MODULE / HK_BROWSER_EXECUTABLE; default Playwright installation.
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const require=createRequire(import.meta.url),{chromium}=require(process.env.HK_PLAYWRIGHT_MODULE||'playwright');
const [html,bundle,output,baseline]=process.argv.slice(2).map(value=>resolve(value));
const text=await readFile(html,'utf8'),base=await readFile(baseline,'utf8'),hash=s=>createHash('sha256').update(s).digest('hex');
await mkdir(output,{recursive:true});
const rows=async name=>(await readFile(join(bundle,name),'utf8')).split(/\r?\n/).filter(Boolean).map(JSON.parse);
const nodes=await rows('nodes.jsonl'),assertions=await rows('assertions.jsonl'),members=await rows('members.jsonl');
const report={sha256:hash(text),baselineSha256:hash(base),checks:[],states:[],errors:[]};
const check=(name,ok,detail)=>report.checks.push({name,ok:!!ok,detail});
const unique=a=>[...new Set(a)].sort(),equal=(a,b)=>JSON.stringify(unique(a))===JSON.stringify(unique(b));
check('Only CSS differs from exhaustive baseline',text.replace(/<style>[\s\S]*?<\/style>/g,'<style></style>')===base.replace(/<style>[\s\S]*?<\/style>/g,'<style></style>'));
const browser=await chromium.launch({headless:true,...(process.env.HK_BROWSER_EXECUTABLE?{executablePath:process.env.HK_BROWSER_EXECUTABLE}:{})});
const context=await browser.newContext({viewport:{width:1920,height:1080},locale:'zh-CN',colorScheme:'light'}),page=await context.newPage();
page.on('pageerror',e=>report.errors.push(e.message));await page.route(/^https?:/,r=>{report.errors.push(`Unexpected network:${r.request().url()}`);return r.abort();});
const settle=()=>page.waitForTimeout(420);
const state=()=>page.evaluate(()=>{
 const nodes=[...document.querySelectorAll('.entity-mark')].map(e=>({id:e.dataset.node,owner:e.dataset.ownerAssertion,muted:e.classList.contains('is-hover-muted'),opacity:+getComputedStyle(e).opacity}));
 const paths=[...document.querySelectorAll('.hyper-envelope,.hyper-envelope-fill')].map(e=>{const s=getComputedStyle(e);return{id:e.dataset.assertion,fill:e.classList.contains('hyper-envelope-fill'),active:e.classList.contains('is-hover-focus'),muted:e.classList.contains('is-hover-muted'),opacity:+s.opacity,color:s.fill,width:parseFloat(s.strokeWidth)};});
 return{nodes,paths,view:document.querySelector('.representation-button[aria-pressed="true"]')?.dataset.representation,rows:document.querySelectorAll('.matrix-row-label').length,columns:document.querySelectorAll('.matrix-column-header').length,cells:document.querySelectorAll('.matrix-cell').length,roleIds:[...document.querySelectorAll('.assertion-mark,.hyperedge-label')].map(e=>e.dataset.assertion),fontMin:Math.min(...[...document.querySelectorAll('.node-inside-label,.matrix-node-text')].map(e=>{const m=e.getScreenCTM();return parseFloat(getComputedStyle(e).fontSize)*Math.hypot(m.a,m.b);})),pageOverflow:document.documentElement.scrollWidth>innerWidth};
});
try{
 await page.goto(pathToFileURL(html).href);await settle();
 for(const theme of ['light','dark']){
  if(await page.locator('html').getAttribute('data-theme')!==theme)await page.locator('#theme-toggle').click();
  for(const a of assertions){
   await page.locator('[data-action="reset"]').click();await page.locator('[data-representation="contour"]').click();await settle();
   const card=page.locator(`.hyperedge-label[data-assertion=${JSON.stringify(a.id)}] .label-block-bg`);await card.scrollIntoViewIfNeeded();await card.hover();await settle();
   const s=await state(),expected=members.filter(m=>m.assertion_id===a.id).map(m=>m.node_id),active=s.paths.filter(p=>p.active),unrelated=s.paths.filter(p=>p.id!==a.id);
   check(`${theme}:${a.id}:crisp canonical members`,equal(s.nodes.filter(n=>!n.muted).map(n=>n.id),expected),s.nodes);
   check(`${theme}:${a.id}:only target active`,equal(active.map(p=>p.id),[a.id]),active);
   check(`${theme}:${a.id}:unrelated fill and outline visibly dim`,unrelated.every(p=>p.muted&&p.opacity<.2),unrelated);
   check(`${theme}:${a.id}:active boundary emphasis`,active.filter(p=>!p.fill).every(p=>p.opacity>.95&&p.width>=3.2),active);
   check(`${theme}:${a.id}:active filled interior`,active.filter(p=>p.fill).length===1&&active.filter(p=>p.fill).every(p=>p.opacity>.95&&!/\/\s*0?\.0[0-9]/.test(p.color)),active);
   s.name=`${theme}:hover:${a.id}`;report.states.push(s);
   if(a.id==='assertion:wutai-poetry-case')await page.screenshot({path:join(output,`${theme}-hover-wutai.png`),fullPage:true});
   await page.locator('.panel-head').first().hover();await settle();const cleared=await state();check(`${theme}:${a.id}:hover clears`,cleared.paths.every(p=>!p.active&&!p.muted));
  }
 }
 if(await page.locator('html').getAttribute('data-theme')!=='light')await page.locator('#theme-toggle').click();
 for(const viewport of [{width:1440,height:1000},{width:1920,height:1080},{width:390,height:844}]){
  await page.setViewportSize(viewport);await settle();
  for(const mode of ['matrix','incidence','contour']){
   await page.locator('[data-action="reset"]').click();await page.locator(`[data-representation="${mode}"]`).click();await page.locator('.panel-head').first().hover();await settle();const s=await state();s.name=`${viewport.width}:${mode}`;report.states.push(s);
   check(`${s.name}:correct view`,s.view===mode);check(`${s.name}:font readable`,s.fontMin>=10,s.fontMin);check(`${s.name}:no document overflow`,!s.pageOverflow);
   if(mode==='contour')check(`${s.name}:all canonical nodes and assertions`,equal(s.nodes.map(n=>n.id),nodes.map(n=>n.id))&&equal(s.roleIds,assertions.map(a=>a.id)));
   if(mode==='matrix')check(`${s.name}:matrix complete`,s.rows===nodes.length&&s.columns===assertions.length&&s.cells===unique(members.map(m=>`${m.assertion_id}|${m.node_id}`)).length);
   await page.screenshot({path:join(output,`${viewport.width}-${mode}.png`),fullPage:true});
  }
 }
}catch(e){report.errors.push(e.stack);}finally{
 report.sourceUnchanged=hash(await readFile(html,'utf8'))===report.sha256;report.passed=report.sourceUnchanged&&report.errors.length===0&&report.checks.every(c=>c.ok);
 await writeFile(join(output,'hover-delta-report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({passed:report.passed,sha256:report.sha256,baselineSha256:report.baselineSha256,states:report.states.length,checks:report.checks.length,errors:report.errors,failures:report.checks.filter(c=>!c.ok)}));await browser.close();if(!report.passed)process.exitCode=1;
}
