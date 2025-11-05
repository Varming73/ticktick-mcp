#!/usr/bin/env node
import { spawn } from 'child_process';

console.log('🧪 Testing TickTick MCP Server installation...\n');

function checkPython() {
  return new Promise((resolve, reject) => {
    const python3 = spawn('python3', ['--version']);
    python3.on('error', () => {
      const python = spawn('python', ['--version']);
      python.on('error', () => reject(new Error('Python not found')));
      python.on('close', (code) => {
        if (code === 0) resolve('python');
        else reject(new Error('Python not found'));
      });
    });
    python3.on('close', (code) => {
      if (code === 0) resolve('python3');
    });
  });
}

function testImport(python) {
  return new Promise((resolve, reject) => {
    const child = spawn(python, ['-c', 'import ticktick_mcp; print("OK")']);
    let output = '';
    child.stdout.on('data', (data) => { output += data.toString(); });
    child.on('close', (code) => {
      if (code === 0 && output.includes('OK')) resolve();
      else reject(new Error('Failed to import ticktick_mcp module'));
    });
  });
}

async function main() {
  try {
    console.log('🔍 Checking Python...');
    const python = await checkPython();
    console.log(`✅ Found ${python}\n`);

    console.log('🔍 Testing ticktick_mcp module...');
    await testImport(python);
    console.log('✅ Module import successful\n');

    console.log('✅ All tests passed!\n');
    process.exit(0);

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  }
}

main();
