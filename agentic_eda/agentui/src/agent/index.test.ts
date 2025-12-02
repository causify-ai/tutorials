import { describe, expect, it, vi } from 'vitest';
import type { AppConfig } from '../config/index.js';

const { createDeepAgentMock, invokeMock } = vi.hoisted(() => {
  const invoke = vi.fn().mockResolvedValue({
    messages: [{ content: 'Agent reply', usage_metadata: { input_tokens: 10, total_tokens: 20 } }]
  });
  const mock = vi.fn((options: Record<string, unknown>) => ({ invoke, options }));
  return {
    invokeMock: invoke,
    createDeepAgentMock: mock
  };
});
const FilesystemBackendMock = vi.hoisted(() => {
  return class FilesystemBackendStub {
    public options;
    constructor(options: Record<string, unknown>) {
      this.options = options;
    }
  };
});
const ChatOpenAIMock = vi.hoisted(() => {
  return class ChatOpenAIStub {
    public options;
    constructor(options: Record<string, unknown>) {
      this.options = options;
    }
  };
});

const buildToolsMock = vi.hoisted(() => vi.fn(() => ['fs-tool']));

vi.mock('deepagents', () => ({
  createDeepAgent: createDeepAgentMock,
  FilesystemBackend: FilesystemBackendMock
}));

vi.mock('@langchain/openai', () => ({
  ChatOpenAI: ChatOpenAIMock
}));

vi.mock('../tools/index.js', () => ({
  buildTools: buildToolsMock
}));

// ESM imports happen after mocks
import { createAgentRunner } from './index.js';

const baseConfig: AppConfig = {
  openAIApiKey: 'sk-test',
  openAIModel: 'gpt-4o-mini',
  systemPrompt: 'be kind'
};

describe('createAgentRunner', () => {
  it('constructs deep agent with ChatOpenAI model and filesystem backend', async () => {
    const runner = createAgentRunner(baseConfig);
    expect(createDeepAgentMock).toHaveBeenCalledTimes(1);
    const mockedCreate = vi.mocked(createDeepAgentMock);
    const agentArgs = mockedCreate.mock.calls[0]?.[0] as
      | { systemPrompt: string; model: InstanceType<typeof ChatOpenAIMock> }
      | undefined;
    expect(agentArgs).toBeDefined();
    expect(agentArgs?.systemPrompt).toBe('be kind');
    expect(agentArgs?.model).toBeInstanceOf(ChatOpenAIMock);
    expect(agentArgs && 'backend' in agentArgs).toBe(true);
    if (agentArgs && 'backend' in agentArgs) {
      const backendInstance = agentArgs.backend as InstanceType<typeof FilesystemBackendMock>;
      expect(backendInstance).toBeInstanceOf(FilesystemBackendMock);
      expect(backendInstance.options).toMatchObject({ rootDir: process.cwd(), virtualMode: false });
    }
    expect(buildToolsMock).toHaveBeenCalledWith(process.cwd());
    expect((agentArgs as { tools?: unknown[] }).tools).toEqual(['fs-tool']);

    const response = await runner.run([{ role: 'user', content: 'hi' }]);
    expect(invokeMock).toHaveBeenCalledWith(
      { messages: [{ role: 'user', content: 'hi' }] },
      expect.objectContaining({ recursionLimit: 100 })
    );
    expect(response.text).toBe('Agent reply');
    expect(response.usage).toEqual({ input_tokens: 10, total_tokens: 20 });
  });
});
