// Captures a battle in the GM panel of virtualJRPG (vj-combat.png, 1440x660): creates an enemy group from the catalog,
// starts the battle and switches to the 3/4 camera ("v" key cycles the cameras: shoulder, follow, side, 3/4).
// Start the game first, in the virtualJRPG repo:  GM_KEY=demo VJ_TUNNEL=0 PORT=3100 VJ_DATA=/tmp/vjdata node server.js
// Then, from this folder: NODE_PATH=$(npm root -g) node virtualjrpg.js
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1440, height: 660 } });
  const click = (sel, text) => p.evaluate(([s, t]) => {
    const e = [...document.querySelectorAll(s)].find((x) => x.innerText.trim().startsWith(t));
    if (e) e.click();
    return !!e;
  }, [sel, text]);
  await p.goto('http://localhost:3100/gm', { waitUntil: 'load' });
  await p.fill('input[type=password]', 'demo');
  await p.click('text=ENTRAR');
  await p.waitForTimeout(3000);
  await click('button', 'Catálogo');
  await p.waitForTimeout(1500);
  await p.evaluate(() => document.querySelector('button[data-a="foeEnc"][data-diff="normal"]').click());   // automatic encounter, "Normal"
  await p.waitForTimeout(1500);
  await click('button', 'Combate');
  await p.waitForTimeout(1500);
  await click('button', 'Iniciar batalha');
  await p.waitForTimeout(3000);
  for (let i = 0; i < 3; i++) { await p.keyboard.press('v'); await p.waitForTimeout(3000); }
  await p.screenshot({ path: 'vj-combat.png' });
  await b.close();
})();
