#!/usr/bin/env node
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

const rootDir = path.resolve(__dirname, '..');
const distEntry = path.join(rootDir, 'dist', 'src', 'cli.js');
const srcEntry = path.join(rootDir, 'src', 'cli.tsx');

const entry = fs.existsSync(distEntry) ? distEntry : fs.existsSync(srcEntry) ? srcEntry : null;

if (process.env.AGENTUI_BIN_SELFTEST === '1') {
  console.log(process.cwd());
  process.exit(0);
}

if (!entry) {
  console.error(
    'agentui: no CLI entrypoint found. Run `npm run build` or ensure src/cli.tsx exists.'
  );
  process.exit(1);
}

const args = entry.endsWith('.tsx')
  ? ['--loader', 'tsx', entry, ...process.argv.slice(2)]
  : [entry, ...process.argv.slice(2)];

const child = spawn(process.execPath, args, {
  cwd: process.cwd(),
  env: process.env,
  stdio: 'inherit'
});

child.on('exit', (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exit(code ?? 0);
});
