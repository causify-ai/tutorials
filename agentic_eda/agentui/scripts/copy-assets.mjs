#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const copyDir = (source, dest) => {
  if (!fs.existsSync(source)) return;
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.rmSync(dest, { recursive: true, force: true });
  fs.cpSync(source, dest, { recursive: true });
  console.log(`[copy-assets] copied ${source} -> ${dest}`);
};

const docsSrc = path.resolve('docs');
const docsDest = path.resolve('dist', 'docs');
copyDir(docsSrc, docsDest);

const runnerSrc = path.resolve('scripts', 'ipynb');
const runnerDest = path.resolve('dist', 'scripts', 'ipynb');
copyDir(runnerSrc, runnerDest);

const visionSrc = path.resolve('scripts', 'image_analyzer.py');
const visionDest = path.resolve('dist', 'scripts', 'image_analyzer.py');
copyDir(visionSrc, visionDest);
