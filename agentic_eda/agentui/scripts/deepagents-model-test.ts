#!/usr/bin/env tsx
/**
 * Lightweight DeepAgents smoke-test script.
 * Usage:
 *   OPENAI_API_KEY=... npx tsx scripts/deepagents-model-test.ts --model gpt-5-nano --prompt "Say hi"
 */
import { createDeepAgent } from 'deepagents';
import { ChatOpenAI } from '@langchain/openai';

type CliArgs = {
  model: string;
  prompt: string;
  system?: string;
};

const parseArgs = (): CliArgs => {
  const args = process.argv.slice(2);
  const result: Partial<CliArgs> = {};
  for (let i = 0; i < args.length; i += 1) {
    const arg = args[i];
    if (!arg.startsWith('--')) continue;
    const key = arg.slice(2) as keyof CliArgs;
    const value = args[i + 1];
    if (!value || value.startsWith('--')) {
      throw new Error(`Missing value for flag "${arg}"`);
    }
    result[key] = value;
    i += 1;
  }
  if (!result.model) {
    throw new Error('Missing --model');
  }
  if (!result.prompt) {
    throw new Error('Missing --prompt');
  }
  return result as CliArgs;
};

const run = async () => {
  const { model, prompt, system } = parseArgs();
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new Error('OPENAI_API_KEY must be set');
  }

  const llm = new ChatOpenAI({ apiKey, model });
  const agent = createDeepAgent({
    model: llm,
    systemPrompt: system ?? 'You are a concise terminal assistant.'
  });

  const result = await agent.invoke({
    messages: [
      ...(system ? [{ role: 'system' as const, content: system }] : []),
      { role: 'user' as const, content: prompt }
    ]
  });

  const finalMessage = result.messages[result.messages.length - 1];
  const metadata = finalMessage?.response_metadata ?? {};

  console.log('=== DeepAgents Test ===');
  console.log(`Requested model: ${model}`);
  console.log(`Resolved model: ${metadata.model ?? metadata.model_name ?? 'unknown'}`);
  console.log('Response:');
  console.log(typeof finalMessage?.content === 'string' ? finalMessage?.content : JSON.stringify(finalMessage?.content, null, 2));
  console.log('Raw response_metadata:', JSON.stringify(metadata, null, 2));
};

run().catch((err) => {
  console.error('Error running DeepAgents test:', err);
  process.exitCode = 1;
});
