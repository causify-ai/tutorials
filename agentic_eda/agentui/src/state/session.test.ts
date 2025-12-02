import { describe, expect, it } from 'vitest';
import { initialSessionState, sessionReducer, type SessionState } from './session.js';

describe('sessionReducer', () => {
  it('adds messages', () => {
    const next = sessionReducer(initialSessionState, {
      type: 'ADD_MESSAGE',
      message: { id: '1', speaker: 'user', content: 'hello' }
    });
    expect(next.messages).toHaveLength(1);
    expect(next.messages[0].content).toBe('hello');
  });

  it('updates a message', () => {
    const state: SessionState = {
      ...initialSessionState,
      messages: [{ id: '1', speaker: 'agent', content: '...', status: 'pending' }]
    };
    const next = sessionReducer(state, {
      type: 'UPDATE_MESSAGE',
      id: '1',
      patch: { content: 'done', status: 'complete' }
    });
    expect(next.messages[0].content).toBe('done');
    expect(next.messages[0].status).toBe('complete');
  });

  it('tracks status', () => {
    const thinking = sessionReducer(initialSessionState, {
      type: 'SET_STATUS',
      status: 'thinking'
    });
    expect(thinking.status).toBe('thinking');
    const idle = sessionReducer(thinking, { type: 'SET_STATUS', status: 'idle' });
    expect(idle.status).toBe('idle');
  });


  it('resets session state', () => {
    const dirty: SessionState = {
      ...initialSessionState,
      messages: [{ id: '1', speaker: 'user', content: 'hello' }],
      status: 'error',
      error: 'oops'
    };
    const next = sessionReducer(dirty, { type: 'RESET_SESSION' });
    expect(next.messages).toHaveLength(0);
    expect(next.status).toBe('idle');
    expect(next.contextPercent).toBeNull();
  });

  it('undoes last turn and clears usage history', () => {
    const state: SessionState = {
      ...initialSessionState,
      messages: [
        { id: '1', speaker: 'user', content: 'hi' },
        { id: '2', speaker: 'agent', content: 'hello' }
      ],
      tokenUsage: { inputTokens: 10, outputTokens: 5, totalTokens: 15 },
      usageHistory: [{ inputTokens: 10, outputTokens: 5, totalTokens: 15 }],
      contextPercent: 50
    };
    const next = sessionReducer(state, { type: 'UNDO_LAST_TURN', contextWindow: 100_000 });
    expect(next.messages).toHaveLength(0);
    expect(next.tokenUsage?.totalTokens ?? 0).toBe(0);
    expect(next.contextPercent).toBe(100);
  });

  it('tracks usage updates', () => {
    const next = sessionReducer(initialSessionState, {
      type: 'UPDATE_USAGE',
      delta: { inputTokens: 10, outputTokens: 5, totalTokens: 20 },
      contextWindow: 50_000
    });
    expect(next.tokenUsage?.totalTokens).toBe(20);
    expect(next.contextPercent).not.toBeNull();
  });
});
