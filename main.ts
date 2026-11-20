import { copyFileSync, existsSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const source = new URL('./entry.png', import.meta.url);
if (!existsSync(source)) {
  throw new Error(`entry.png not found next to main.ts (${source.pathname})`);
}
mkdirSync(outputDir, { recursive: true });
copyFileSync(source, join(outputDir, 'entry.png'));
console.log(`entry.png copied to ${join(outputDir, 'entry.png')}`);
