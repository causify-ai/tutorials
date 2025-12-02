import React, { useState } from 'react';
import { describe, expect, it } from 'vitest';
import { render } from 'ink-testing-library';
import { Text } from 'ink';
import { sanitizeComposerText } from './composer-renderer.js';
import { __private__ } from './App.js';

const ComposerHarness = ({ initialValue = '' }: { initialValue?: string }) => {
  const [val, setVal] = useState(initialValue);
  const [cursor, setCursor] = useState(initialValue.length);
  return (
    <>
      <__private__.ComposerInput
        value={val}
        cursor={cursor}
        onChange={setVal}
        onCursorChange={setCursor}
        onSubmit={() => {}}
        focus
        disabled={false}
        submitDisabled={false}
        width={30}
        placeholder="type"
        highlightMentions
      />
      <Text>{`STATE:${val}|${cursor}`}</Text>
    </>
  );
};

const tick = () => new Promise((resolve) => setTimeout(resolve, 25));

describe('ComposerInput cursor', () => {
  it('keeps cursor at the end during rapid typing', async () => {
    const { stdin, lastFrame } = render(<ComposerHarness initialValue="" />);
    stdin.write('abc');
    stdin.write('def');
    await tick();
    const frame = lastFrame();
    expect(frame).toMatch(/STATE:abcdef\|6/);
  });

  it('sanitizes control characters without breaking cursor length', async () => {
    const dirty = 'hi\u0007there';
    const clean = sanitizeComposerText(dirty);
    const { stdin, lastFrame } = render(<ComposerHarness initialValue={clean} />);
    stdin.write('!');
    await tick();
    const frame = lastFrame();
    expect(frame).toMatch(/STATE:hithere!\|8/);
  });
});
