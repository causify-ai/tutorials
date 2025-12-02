#!/usr/bin/env node
import 'dotenv/config';
import { render } from 'ink';
import { App } from './ui/App.js';
import { ConfigError, loadConfig } from './config/index.js';
import { createAgentRunner } from './agent/index.js';

const main = () => {
  try {
    const config = loadConfig();
    const agent = createAgentRunner(config);
    render(<App agent={agent} config={config} />);
  } catch (error) {
    if (error instanceof ConfigError) {
      console.error('Configuration error:', error.message);
      process.exit(1);
    }
    console.error('Unexpected error bootstrapping AgenTUI:', error);
    process.exit(1);
  }
};

main();
