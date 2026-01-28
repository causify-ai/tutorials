import { describe, expect, it } from 'vitest';
import { streamAgentEvents, type AgentStructuredEvent } from './events.js';

class MockRunner {
  constructor(private readonly events: any[]) {}
  async *stream() {
    for (const ev of this.events) {
      yield ev;
    }
  }
}

const chunk = (content: string) => ({ content });

describe('streamAgentEvents visibility gating', () => {
  const collect = async (events: any[]) => {
    const seen: AgentStructuredEvent[] = [];
    await streamAgentEvents(new MockRunner(events) as any, [], (ev) => seen.push(ev));
    return seen;
  };

  it('flushes buffered reasoning only after the visibility flag arrives (flag mid-stream)', async () => {
    const seen = await collect([
      { event: 'on_chat_model_stream', data: { chunk: chunk('Step 1 ') } },
      { event: 'on_chat_model_stream', data: { chunk: chunk('ReasoningVisible: yes then more') } },
      { event: 'on_chat_model_end', data: { output: chunk(' done') } }
    ]);

    const visibility = seen.find((e) => e.kind === 'reasoning_visibility');
    const plans = seen.filter((e) => e.kind === 'plan') as Array<{ text: string }>;

    expect(visibility).toEqual({ kind: 'reasoning_visibility', visible: true });
    expect(plans.length).toBeGreaterThan(0);
    expect(plans[0].text).toBe('Step 1 then more');
  });

  it('suppresses reasoning when flag is no, even if text is present', async () => {
    const seen = await collect([
      { event: 'on_chat_model_stream', data: { chunk: chunk('ReasoningVisible: no hidden steps') } },
      { event: 'on_chat_model_end', data: { output: chunk('final') } }
    ]);
    const visibility = seen.find((e) => e.kind === 'reasoning_visibility');
    const plans = seen.filter((e) => e.kind === 'plan');
    expect(visibility).toEqual({ kind: 'reasoning_visibility', visible: false });
    expect(plans.length).toBe(0);
  });

  it('defaults to hiding reasoning when no visibility flag is emitted', async () => {
    const seen = await collect([
      { event: 'on_chat_model_stream', data: { chunk: chunk('Some reasoning that should stay hidden') } },
      { event: 'on_chat_model_end', data: { output: chunk('Final answer') } }
    ]);
    const visibility = seen.find((e) => e.kind === 'reasoning_visibility');
    const plans = seen.filter((e) => e.kind === 'plan');
    expect(visibility).toEqual({ kind: 'reasoning_visibility', visible: false });
    expect(plans.length).toBe(0);
  });

  it('keeps updates in reasoning but not in the final answer', async () => {
    const final = await streamAgentEvents(
      new MockRunner([
        { event: 'on_chat_model_stream', data: { chunk: chunk('ReasoningVisible: yes\nUpdate: scanning files\n') } },
        { event: 'on_chat_model_end', data: { output: chunk('Answer: Found 2 files') } }
      ]) as any,
      [],
      () => {}
    );
    expect(final.reasoning).toContain('Update: scanning files');
    expect(final.answer).toBe('Found 2 files');
  });

  it('keeps direct answers for non-tool turns without placeholder text', async () => {
    const final = await streamAgentEvents(
      new MockRunner([
        { event: 'on_chat_model_end', data: { output: chunk('ReasoningVisible: no\nAnswer: 42') } }
      ]) as any,
      [],
      () => {}
    );
    expect(final.answer).toBe('42');
    expect(final.showReasoning).toBe(false);
  });

  it('does not leak the final answer into the reasoning block', async () => {
    const final = await streamAgentEvents(
      new MockRunner([
        { event: 'on_chat_model_stream', data: { chunk: chunk('ReasoningVisible: yes\nPlan: Step 1\nThe notebook saves the PNG to /tmp/foo.png') } },
        { event: 'on_chat_model_end', data: { output: chunk('The notebook saves the PNG to /tmp/foo.png\nAnswer: Done') } }
      ]) as any,
      [],
      () => {}
    );
    expect(final.answer).toBe('Done');
    expect(final.reasoning).not.toContain('Done');
    expect(final.reasoning).not.toContain('The notebook saves the PNG to /tmp/foo.png\nAnswer');
  });

  it('records listing actions with entry counts', async () => {
    const final = await streamAgentEvents(
      new MockRunner([
        { event: 'on_tool_start', name: 'list_path', run_id: '1', data: { input: { dir_path: '/tmp' } } },
        {
          event: 'on_tool_end',
          name: 'list_path',
          run_id: '1',
          data: { output: 'Listing for /tmp:\ndir /tmp/a\nfile /tmp/b.txt' }
        },
        { event: 'on_chat_model_end', data: { output: chunk('Answer: done') } }
      ]) as any,
      [],
      () => {}
    );
    expect(final.actions[0].detail).toContain('(2 entries)');
  });

  it('keeps long streamed answers out of reasoning even with duplicates', async () => {
    const final = await streamAgentEvents(
      new MockRunner([
        { event: 'on_chat_model_stream', data: { chunk: chunk('ReasoningVisible: yes\nPlan: reading notebook\n') } },
        { event: 'on_chat_model_stream', data: { chunk: chunk('Notebook summary incoming ') } },
        { event: 'on_chat_model_end', data: { output: chunk('Notebook summary incoming Answer: The plot shows three sine waves') } }
      ]) as any,
      [],
      () => {}
    );
    expect(final.answer).toBe('The plot shows three sine waves');
    expect(final.reasoning).not.toMatch(/The plot shows three sine waves/);
  });

  it('drops reasoning when it fully mirrors the answer', async () => {
    const final = await streamAgentEvents(
      new MockRunner([
        { event: 'on_chat_model_stream', data: { chunk: chunk('ReasoningVisible: yes\nPlan: describing image\nThe cat is on the mat') } },
        { event: 'on_chat_model_end', data: { output: chunk('The cat is on the mat') } }
      ]) as any,
      [],
      () => {}
    );
    expect(final.answer).toBe('The cat is on the mat');
    expect(final.reasoning).toBe('');
  });
});
