// Captures the live sites used by the website and eco-fruta cards (1440x900): website.png (Projetos page) and ecofruta.png (home).
// Run it from this folder: NODE_PATH=$(npm root -g) node sites.js
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  await p.goto('https://alexjsz.vercel.app/', { waitUntil: 'networkidle' });
  await p.getByText('Projetos', { exact: true }).first().click();
  await p.waitForTimeout(3500);
  await p.screenshot({ path: 'website.png' });
  await p.goto('https://eco-fruta.vercel.app', { waitUntil: 'networkidle' });
  await p.waitForTimeout(3500);
  await p.screenshot({ path: 'ecofruta.png' });
  await b.close();
})();
