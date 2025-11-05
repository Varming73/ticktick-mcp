#!/usr/bin/env node
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = join(__dirname, '..');

// Find Python executable (python3 or python)
function findPython() {
  return new Promise((resolve) => {
    const python3 = spawn('python3', ['--version']);
    python3.on('error', () => {
      const python = spawn('python', ['--version']);
      python.on('error', () => {
        console.error('Error: Python 3.10+ is required but not found.');
        console.error('Please install Python from https://www.python.org/');
        process.exit(1);
      });
      python.on('close', (code) => {
        if (code === 0) resolve('python');
        else {
          console.error('Error: Python 3.10+ is required.');
          process.exit(1);
        }
      });
    });
    python3.on('close', (code) => {
      if (code === 0) resolve('python3');
    });
  });
}

// Run the MCP server
async function main() {
  const python = await findPython();
  
  // Run using python -m ticktick_mcp.cli run
  const args = ['-m', 'ticktick_mcp.cli', 'run'];
  
  const child = spawn(python, args, {
    cwd: projectRoot,
    stdio: 'inherit',
    env: {
      ...process.env,
      PYTHONPATH: projectRoot
    }
  });

  child.on('error', (error) => {
    console.error('Error running TickTick MCP server:', error.message);
    process.exit(1);
  });

  child.on('close', (code) => {
    process.exit(code || 0);
  });

  // Handle signals
  process.on('SIGINT', () => {
    child.kill('SIGINT');
  });
  process.on('SIGTERM', () => {
    child.kill('SIGTERM');
  });
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
