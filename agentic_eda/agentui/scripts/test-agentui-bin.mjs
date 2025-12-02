#!/usr/bin/env node
import { mkdtempSync, rmSync, realpathSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const binPath = path.resolve('bin/agentui.cjs');
const tmpDir = mkdtempSync(path.join(os.tmpdir(), 'agentui-bin-'));

try {
  const result = spawnSync(binPath, [], {
    cwd: tmpDir,
    env: { ...process.env, AGENTUI_BIN_SELFTEST: '1' },
    encoding: 'utf8'
  });

  if (result.error) {
    throw result.error;
  }
  if (result.status !== 0) {
    throw new Error(`agentui bin exited with status ${result.status}: ${result.stderr}`);
  }

  const reported = result.stdout.trim().split('\n').filter(Boolean).pop();
  const expectedReal = realpathSync(tmpDir);
  const reportedReal = reported ? realpathSync(reported) : '';
  if (reportedReal !== expectedReal) {
    throw new Error(`Expected cwd "${expectedReal}" but launcher reported "${reportedReal}"`);
  }

  console.log(`agentui launcher OK (cwd=${reportedReal})`);
} finally {
  rmSync(tmpDir, { recursive: true, force: true });
}
