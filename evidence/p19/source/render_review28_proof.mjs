import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const sharp = require('<OWNER_HOME>/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root = process.cwd();
const source = path.join(root, 'evidence/p19/gallery/previews/type-tree.svg');
const out = path.join(root, 'evidence/p19/review28-checks');
fs.mkdirSync(out, { recursive: true });
const svg = fs.readFileSync(source, 'utf8');
fs.writeFileSync(path.join(out, 'type-tree.svg'), svg);
const palette = {
  'var(--paper)': '#eeece7', 'var(--canvas)': '#f7f6f2', 'var(--surface)': '#ffffff',
  'var(--surface-alt)': '#eeece7', 'var(--text)': '#252b3c', 'var(--muted)': '#687286',
  'var(--border)': '#c7ccd2', 'var(--accent)': '#f26a32', 'var(--accent-soft)': '#f8e7dd',
  'var(--accent-text)': '#df5522', 'var(--on-accent)': '#ffffff', 'var(--connector)': '#4f5e76',
  'var(--grid)': '#d9d7d2'
};
let proof = svg;
for (const [token, value] of Object.entries(palette)) proof = proof.split(token).join(value);
fs.writeFileSync(path.join(out, 'type-tree--visual-proof.svg'), proof);
await sharp(Buffer.from(proof)).png().toFile(path.join(out, 'type-tree.svg.png'));
console.log(JSON.stringify({ width: 2000, height: 920, proof: 'evidence/p19/review28-checks/type-tree.svg.png' }));
