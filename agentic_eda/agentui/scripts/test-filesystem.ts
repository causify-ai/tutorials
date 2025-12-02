import { spawnSync } from 'node:child_process';
import fs from 'fs/promises';
import path from 'path';

const workspace = process.cwd();
const fixtureRoot = path.join(workspace, 'tmp', 'fs-spec');

const runPrompt = (prompt: string, timeout = 120_000) => {
  const result = spawnSync('npm', ['run', 'agent', '--', prompt], {
    cwd: workspace,
    encoding: 'utf8',
    stdio: 'pipe',
    timeout
  });
  if (result.status !== 0) {
    console.error(result.stdout);
    console.error(result.stderr);
    throw new Error(`Prompt "${prompt}" failed with status ${result.status}`);
  }
  return result.stdout;
};

const assertIncludes = (output: string, needle: string) => {
  if (!output.includes(needle)) {
    throw new Error(`Missing "${needle}". Output:\n${output}`);
  }
};

const fileExists = async (relativePath: string) => {
  await fs.access(path.join(workspace, relativePath));
};

const fileMissing = async (relativePath: string) => {
  try {
    await fs.access(path.join(workspace, relativePath));
    throw new Error(`Expected ${relativePath} to be missing`);
  } catch {
    // expected
  }
};

const setupFixture = async () => {
  await fs.rm(fixtureRoot, { recursive: true, force: true });
  await fs.mkdir(fixtureRoot, { recursive: true });
  await fs.writeFile(path.join(fixtureRoot, 'alpha.txt'), 'Alpha line\nSecond line\n');
  await fs.writeFile(path.join(fixtureRoot, 'beta.md'), 'Beta file\n');
};

const main = async () => {
  await setupFixture();

  const listOutput = runPrompt('list the files in @tmp/fs-spec/');
  assertIncludes(listOutput, 'alpha.txt');
  assertIncludes(listOutput, 'beta.md');

  const copyOutput = runPrompt('copy @tmp/fs-spec/alpha.txt to @tmp/fs-spec/copied-alpha.txt');
  assertIncludes(copyOutput, 'Copied');
  await fileExists('tmp/fs-spec/copied-alpha.txt');

  const searchOutput = runPrompt('search for "Alpha" in @tmp/fs-spec/');
  assertIncludes(searchOutput, 'Alpha line');

  const globOutput = runPrompt('glob "*.txt" @tmp/fs-spec/');
  assertIncludes(globOutput, 'alpha.txt');
  assertIncludes(globOutput, 'copied-alpha.txt');

  const readOutput = runPrompt('show the first 2 lines of @tmp/fs-spec/copied-alpha.txt');
  assertIncludes(readOutput, 'Alpha line');

  const deleteOutput = runPrompt('delete @tmp/fs-spec/copied-alpha.txt');
  assertIncludes(deleteOutput, 'Deleted');
  await fileMissing('tmp/fs-spec/copied-alpha.txt');

  const questionOutput = runPrompt('what are the files in @tmp/fs-spec/?');
  assertIncludes(questionOutput, 'alpha.txt');
  assertIncludes(questionOutput, 'beta.md');

  console.log('\nFilesystem regression prompts completed successfully.');
};

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});
