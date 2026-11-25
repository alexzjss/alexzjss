# pacman

Generates `output/pacman.svg`, the Pac-Man that eats the contribution graph in the README.

Vendored from [pencilrebel/pacman-contribution-graph](https://github.com/pencilrebel/pacman-contribution-graph) (MIT), `src/` copied as is. Run daily by `.github/workflows/pacman.yml`.

```bash
node scripts/pacman/generate.mjs --demo --out output                       # random data, no token
GITHUB_TOKEN=... node scripts/pacman/generate.mjs --user alexzjss --out output
```

Look and feel (speed, mouth, size, colors) are the constants at the top of `svg.mjs`.
