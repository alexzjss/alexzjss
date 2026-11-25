// Captures the ICNDY app running on the web (port 8098): icndy-days.png (onboarding), icndy-home.png and icndy-setup.png.
// See README.md for how to build and serve the web export.
const {chromium}=require('playwright');
const clickText=(p,re)=>p.evaluate((src)=>{const re=new RegExp(src,'i');const e=[...document.querySelectorAll('div,button,[role=button]')].filter(x=>re.test((x.innerText||'').trim())&&(x.innerText||'').trim().length<40).pop();if(e){e.click();return e.innerText.trim()}return null},re.source);
(async()=>{const b=await chromium.launch();
const p=await b.newPage({viewport:{width:390,height:844},deviceScaleFactor:2});
await p.goto('http://localhost:8098/',{waitUntil:'load'});await p.waitForTimeout(9000);
await clickText(p,/^Começar/);await p.waitForTimeout(4000);await p.screenshot({path:'icndy-days.png'});
await clickText(p,/^Continuar/);await p.waitForTimeout(3000);await clickText(p,/^Entrar no ICNDY/);await p.waitForTimeout(6000);
await p.screenshot({path:'icndy-home.png'});
await clickText(p,/^Treinar agora/);await p.waitForTimeout(7000);await p.screenshot({path:'icndy-setup.png'});
await b.close();})();
