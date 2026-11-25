# Screenshot sources

`scripts/shots.py` cuts the pictures of the project cards from `assets/shots/src/`. This folder has what took (or where to find) each one.

| card | source in `assets/shots/src/` | where it came from |
|---|---|---|
| DaSIboard | `dasiboard.webp` | `docs/screenshots/disciplinas.png` in dasiboard-omg |
| Engrama | `engrama.webp` | `docs/images/ui-daynight.png` in engrama |
| Clawdesk | `clawdesk-*.webp` (8 frames) | `docs/clawds-*.png` in clawdesk |
| JFLP Studio | `jflp.webp` | `docs/img/painel-escuro.png` in jflp |
| vat | `vat.webp` | `docs/screenshots/02-cidade.png` in vat |
| ModaLoop | `modaloop.webp` | `modaloop.png` in modaloop |
| SampaNav | (none) | `assets/shots/sampanav.jpg` is used as is |
| virtualJRPG | `virtualjrpg.webp` | `virtualjrpg.js` (a battle in the running game) |
| Constela | `constela-1..3.webp` | `constela.js` (the app on the web, made-up demo data) |
| ICNDY | `icndy-setup.webp`, `icndy-home.webp` | `icndy.js` (the app on the web) |
| website, eco-fruta | `website.webp`, `ecofruta.webp` | `sites.js` (the live sites) |
| acha-promocoes | `acha-promocoes.webp` | `acha-promocoes.js` (an offer as the bot posts it; the offer is fictional) |

The scripts need Playwright (`NODE_PATH=$(npm root -g) node <script>`); each one writes PNGs next to itself. Convert them to
`assets/shots/src/*.webp` (`Image.open(png).convert("RGB").save(webp, quality=86)`) and run `python3 scripts/shots.py`
and `python3 scripts/cards.py`.

## Expo apps on the web (Constela, ICNDY)

```bash
git clone <the app repo> && cd <the app repo> && npm install
npm install --no-save react-native-web react-dom@<same version as react> @expo/metro-runtime
# metro.config.js needs: config.resolver.assetExts.push('wasm');   (expo-sqlite on the web)
npx expo export --platform web --output-dir /tmp/app-web
node serve.js /tmp/app-web 8099      # Constela;  8098 for ICNDY (what the scripts expect)
```

`react-dom` must match the `react` version exactly, or the page dies with React error 527.
