// Static server for an `expo export --platform web` folder, with the COOP/COEP headers expo-sqlite needs on the web.
// node serve.js <folder> [port]
const http=require('http'),fs=require('fs'),path=require('path');
const root=process.argv[2]||'dist';const port=+process.argv[3]||8099;const types={'.html':'text/html','.js':'text/javascript','.wasm':'application/wasm','.css':'text/css','.png':'image/png','.ttf':'font/ttf','.json':'application/json','.svg':'image/svg+xml'};
http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]);let f=path.join(root,p);
 if(!fs.existsSync(f)||fs.statSync(f).isDirectory())f=path.join(root,'index.html');
 r.setHeader('Cross-Origin-Embedder-Policy','credentialless');r.setHeader('Cross-Origin-Opener-Policy','same-origin');
 r.setHeader('Content-Type',types[path.extname(f)]||'application/octet-stream');fs.createReadStream(f).pipe(r);}).listen(port);
