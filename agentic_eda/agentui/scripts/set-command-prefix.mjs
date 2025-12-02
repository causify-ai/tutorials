#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const TARGET_PATH = './bin/agentui.cjs';

const pkgPath = path.resolve('package.json');
const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
const desiredName = process.argv[2] || process.env.AGENTUI_PREFIX;

if (!desiredName) {
  console.error('Usage: AGENTUI_PREFIX=<name> npm run bin:set  (or pass name as an argument)');
  process.exit(1);
}

if (!pkg.bin) {
  pkg.bin = {};
}

for (const key of Object.keys(pkg.bin)) {
  if (pkg.bin[key] === TARGET_PATH) {
    delete pkg.bin[key];
  }
}

pkg.bin[desiredName] = TARGET_PATH;

fs.writeFileSync(pkgPath, `${JSON.stringify(pkg, null, 2)}\n`);
console.log(`Updated package.json bin entry: ${desiredName} -> ${TARGET_PATH}`);
