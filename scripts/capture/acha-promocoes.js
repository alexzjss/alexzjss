// Renders acha-promocoes.html (an offer as the bot posts it, same fields as services/discord_sender.py; fictional offer) to acha-promocoes.png.
// Run it from this folder: NODE_PATH=$(npm root -g) node acha-promocoes.js
const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();
const p=await b.newPage({viewport:{width:520,height:285},deviceScaleFactor:2});
await p.goto('file://'+process.cwd()+'/acha-promocoes.html');await p.waitForTimeout(500);
await p.screenshot({path:'acha-promocoes.png'});await b.close();})();
