import React from 'react';
import { describe, expect, it } from 'vitest';
import { render } from 'ink-testing-library';
import { Transcript } from './App.js';
import type { Message } from '../state/session.js';

const stripAnsi = (value: string) => value.replace(/\u001b\[[0-9;]*m/g, '');

describe('Transcript rendering', () => {
  it('renders reasoning in grey area before actions and keeps answers clean', () => {
    const message: Message = {
      id: 'agent-1',
      speaker: 'agent',
      status: 'complete',
      content: '',
      reasoning: 'Update: marked todo\nUpdate: listed files',
      actions: [
        { id: 'a1', name: 'list_path', status: 'success', detail: 'Listed /tmp (0 entries)' }
      ],
      answer: 'Found no files in /tmp',
      showReasoning: true,
      timestamp: 'now'
    };

    const { lastFrame } = render(<Transcript messages={[message]} />);
    const frame = stripAnsi(lastFrame());

    expect(frame).toContain('Update: marked todo');
    expect(frame).toContain('Actions Taken');
    expect(frame).toContain('Listed /tmp (0 entries)');
    expect(frame).toContain('Found no files in /tmp');

    expect(frame.indexOf('Update: marked todo')).toBeLessThan(frame.indexOf('Actions Taken'));
    expect(frame.indexOf('Actions Taken')).toBeLessThan(frame.lastIndexOf('Found no files in /tmp'));
    expect(frame).not.toMatch(/Completed actions/i);
  });

  it('omits the actions section when no actions exist and still renders answers', () => {
    const message: Message = {
      id: 'agent-2',
      speaker: 'agent',
      status: 'complete',
      content: '',
      reasoning: '',
      actions: [],
      answer: '42',
      showReasoning: false,
      timestamp: 'now'
    };

    const { lastFrame } = render(<Transcript messages={[message]} />);
    const frame = stripAnsi(lastFrame());

    expect(frame).not.toContain('Actions Taken');
    expect(frame).toContain('42');
  });
});
