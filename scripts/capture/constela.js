// Captures the Constela app running on the web with made-up positions and synthetic market data (Yahoo, BCB and Tesouro
// requests are answered by the script, so nothing real is shown): constela-1.png (Carteira), constela-2.png (scrolled),
// constela-3.png (Companheiro). See README.md for how to build and serve the web export (port 8099).
const {chromium}=require('playwright');
function rng(seed){let s=0;for(const c of seed)s=(s*31+c.charCodeAt(0))>>>0;return()=>{s=(s*1664525+1013904223)>>>0;return s/4294967296;};}
const META={'KNRI11.SA':['FII Kinea Renda Imobiliaria','BRL',160,.10],'PETR4.SA':['Petroleo Brasileiro S.A. - Petrobras','BRL',32,.28],'WEGE3.SA':['WEG S.A.','BRL',42,.24],'VOO':['Vanguard S&P 500 ETF','USD',480,.16],'BTC-USD':['Bitcoin USD','USD',60000,.55]};
function chart(sym){const m=META[sym]||[sym,'BRL',50,.25];const r=rng(sym);const ts=[],cl=[];let p=m[2];const end=Math.floor(Date.now()/1000);
 for(let d=5*365;d>=0;d--){const t=end-d*86400;const dow=new Date(t*1000).getUTCDay();if(dow==0||dow==6)continue;p*=Math.exp((.0003+ (r()-.5)*m[3]/8));ts.push(t);cl.push(+p.toFixed(2));}
 return {chart:{result:[{meta:{currency:m[1],longName:m[0],symbol:sym},timestamp:ts,indicators:{quote:[{close:cl}],adjclose:[{adjclose:cl}]}}]}};}
(async()=>{const b=await chromium.launch();
const p=await b.newPage({viewport:{width:390,height:844},deviceScaleFactor:2});
await p.route(/query1\.finance\.yahoo\.com\/v8\/finance\/chart\/([^?]+)/,async r=>{const sym=decodeURIComponent(r.request().url().match(/chart\/([^?]+)/)[1]);await r.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:JSON.stringify(chart(sym))});});
await p.route(/query1\.finance\.yahoo\.com\/v1\/finance\/search/,r=>r.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:JSON.stringify({quotes:[]})}));
await p.route(/api\.bcb\.gov\.br/,async r=>{const u=r.request().url();const code=+u.match(/sgs\.(\d+)/)[1];let body;
 if(u.includes('/ultimos/')){const n=+u.match(/ultimos\/(\d+)/)[1];const v={432:'10.50',4389:'10.40',433:'0.40',226:'0.17'}[code]||'0.1';body=Array.from({length:n},(_,i)=>({data:`0${1+i%9}/11/2026`.slice(-10),valor:v}));body[n-1].data='28/11/2026';}
 else{const m=u.match(/dataInicial=(\d+)\/(\d+)\/(\d+)&dataFinal=(\d+)\/(\d+)\/(\d+)/);const a=Date.UTC(+m[3],+m[2]-1,+m[1]),z=Date.UTC(+m[6],+m[5]-1,+m[4]);body=[];for(let t=a;t<=z;t+=86400000){const d=new Date(t);if([0,6].includes(d.getUTCDay()))continue;const dd=String(d.getUTCDate()).padStart(2,'0'),mm=String(d.getUTCMonth()+1).padStart(2,'0');body.push({data:`${dd}/${mm}/${d.getUTCFullYear()}`,valor:code==433?'0.40':'0.0400'});}}
 await r.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:JSON.stringify(body)});});
await p.route(/tesourotransparente/,r=>r.fulfill({status:200,contentType:'text/csv',headers:{'access-control-allow-origin':'*'},body:'Tipo Titulo;Data Vencimento;Data Base;Taxa Compra Manha;Taxa Venda Manha;PU Compra Manha;PU Venda Manha;PU Base Manha\nTesouro Selic;01/03/2029;28/11/2026;0,10;0,16;16500,00;16480,00;16490,00\nTesouro IPCA+;15/05/2035;28/11/2026;7,45;7,57;2100,00;2090,00;2095,00\nTesouro Prefixado;01/01/2031;28/11/2026;13,10;13,22;660,00;655,00;657,00\n'}));
p.on('pageerror',e=>console.log('pageerror',e.message.slice(0,120)));
await p.goto('http://localhost:8099/',{waitUntil:'load'});await p.waitForTimeout(6000);
const pos=[['Tesouro','Tesouro Selic 2029','','8000,00','8940,00','15/03/2025'],['CDB/RDB','CDB Banco Demo 110% CDI','','5000,00','5610,00','10/06/2025'],['FIIs','KNRI11','KNRI11.SA','4000,00','4380,00','02/02/2025'],['Ações','PETR4','PETR4.SA','3500,00','3950,00','20/01/2025'],['Ações','WEGE3','WEGE3.SA','2500,00','2710,00','11/04/2025'],['Exterior','VOO','VOO','3000,00','3540,00','05/03/2025'],['Cripto','Bitcoin','BTC-USD','1200,00','1640,00','18/08/2025']];
for(const [t,n,s,i,v,d] of pos){
 await p.getByText('Nova posição',{exact:true}).click();await p.waitForTimeout(300);
 await p.getByText(t,{exact:true}).first().click();
 await p.getByPlaceholder('Tesouro Selic 2029').fill(n);
 if(s)await p.getByPlaceholder('PETR4.SA').fill(s);
 await p.getByPlaceholder('1.000,00').fill(i);await p.getByPlaceholder('1.050,00').fill(v);await p.getByPlaceholder('dd/mm/aaaa').fill(d);
 await p.getByText('Adicionar',{exact:true}).click();await p.waitForTimeout(1200);}
await p.waitForTimeout(6000);
await p.mouse.move(200,400);await p.mouse.wheel(0,-6000);await p.waitForTimeout(1200);
await p.screenshot({path:'constela-1.png'});
await p.mouse.wheel(0,700);await p.waitForTimeout(1000);await p.screenshot({path:'constela-2.png'});
await p.getByText('Companheiro',{exact:true}).last().click({force:true});await p.waitForTimeout(2500);
await p.getByText('Ajustar simulação',{exact:false}).first().click({force:true});await p.waitForTimeout(800);await p.getByPlaceholder('0,00').fill('5000');await p.keyboard.press('Tab');await p.waitForTimeout(3000);await p.mouse.wheel(0,-6000);await p.waitForTimeout(500);await p.screenshot({path:'constela-3.png'});
await p.getByText('Pesquisar',{exact:true}).last().click({force:true});await p.waitForTimeout(2500);
await b.close();})();
