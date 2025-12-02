import { spawnSync } from 'node:child_process';

const prompts = [
  'hello',
  'how many cleanup* docs are there in level 0 of this workspace?',
  'list the files in @src/',
  'create a notebook at @tmp/agent-smoke.ipynb with a single markdown cell titled "Smoke Test".',
  'summarize @notebooks/cosine_wave_plot.ipynb using notebook tools and mention the plots.',
  'In @notebooks/cosine_wave_plot.ipynb add a code cell plotting y = x**2 + 1, run it, and list the generated images.'
];

const npmCmd = process.platform === 'win32' ? 'npm.cmd' : 'npm';
const MAX_ATTEMPTS = 2;

prompts.forEach((prompt, index) => {
  console.log(`\n=== Prompt ${index + 1}: ${prompt} ===\n`);
  let attempt = 0;
  let status = 0;
  do {
    const result = spawnSync(npmCmd, ['run', 'agent', '--', prompt], {
      stdio: 'inherit',
      env: process.env
    });
    status = result.status ?? 0;
    attempt += 1;
    if (status === 0) break;
    console.warn(`Prompt ${index + 1} failed (attempt ${attempt}/${MAX_ATTEMPTS}). Retrying...`);
  } while (attempt < MAX_ATTEMPTS);
  if (status !== 0) {
    console.error(`Prompt ${index + 1} failed after ${MAX_ATTEMPTS} attempts.`);
    process.exit(status);
  }
});

console.log('\nAll agent smoke prompts completed.\n');
