import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const sharp = require('<OWNER_HOME>/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root = process.cwd();
const source = path.join(root, 'evidence/p19/gallery/previews/type-treemap.svg');
const out = path.join(root, 'evidence/p19/review32-checks');
fs.mkdirSync(out, { recursive: true });
const svg = fs.readFileSync(source, 'utf8');
fs.writeFileSync(path.join(out, 'type-treemap.svg'), svg);
const palette = {
  'var(--paper)': '#eeece7', 'var(--canvas)': '#f7f6f2', 'var(--surface)': '#ffffff',
  'var(--surface-alt)': '#eeece7', 'var(--text)': '#252b3c', 'var(--muted)': '#687286',
  'var(--border)': '#c7ccd2', 'var(--accent)': '#f26a32', 'var(--accent-soft)': '#f8e7dd',
  'var(--accent-text)': '#df5522', 'var(--on-accent)': '#ffffff', 'var(--connector)': '#4f5e76',
  'var(--grid)': '#d9d7d2'
};
let proof = svg;
for (const [token, value] of Object.entries(palette)) proof = proof.split(token).join(value);
proof = proof
  .replaceAll('color-mix(in srgb,#4f5e76 24%,#ffffff)', '#d5d8dd')
  .replaceAll('color-mix(in srgb,#4f5e76 17%,#ffffff)', '#e1e3e6')
  .replaceAll('color-mix(in srgb,#4f5e76 12%,#ffffff)', '#e9eaec')
  .replaceAll('color-mix(in srgb,#4f5e76 9%,#ffffff)', '#eef0f1')
  .replaceAll('color-mix(in srgb,#4f5e76 6%,#ffffff)', '#f4f4f5')
  .replaceAll('color-mix(in srgb,#4f5e76 18%,#ffffff)', '#dfe1e4');
fs.writeFileSync(path.join(out, 'type-treemap--visual-proof.svg'), proof);
await sharp(Buffer.from(proof)).png().toFile(path.join(out, 'type-treemap.svg.png'));
console.log(JSON.stringify({ width: 2000, height: 1040, proof: 'evidence/p19/review32-checks/type-treemap.svg.png' }));
