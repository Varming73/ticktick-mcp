#!/usr/bin/env node
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { existsSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = join(__dirname, '..');

console.log('📦 Installing TickTick MCP Server...\n');

// Check for Python
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

// Check Python version
function checkPythonVersion(python) {
  return new Promise((resolve, reject) => {
    const child = spawn(python, ['-c', 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")']);
    let output = '';
    child.stdout.on('data', (data) => { output += data.toString(); });
    child.on('close', (code) => {
      if (code !== 0) return reject(new Error('Failed to check Python version'));
      const version = parseFloat(output.trim());
      if (version >= 3.10) resolve(true);
      else reject(new Error(`Python 3.10+ required, but found ${version}`));
    });
  });
}

// Install Python dependencies
function installDependencies(python) {
  return new Promise((resolve, reject) => {
    console.log('📥 Installing Python dependencies...');
    const child = spawn(python, ['-m', 'pip', 'install', '-e', '.'], {
      cwd: projectRoot,
      stdio: 'inherit'
    });
    child.on('close', (code) => {
      if (code === 0) resolve();
      else reject(new Error('Failed to install Python dependencies'));
    });
  });
}

async function main() {
  try {
    // Check Python
    console.log('🔍 Checking for Python...');
    const python = await checkPython();
    console.log(`✅ Found ${python}\n`);

    // Check Python version
    console.log('🔍 Checking Python version...');
    await checkPythonVersion(python);
    console.log('✅ Python version is compatible\n');

    // Install dependencies
    await installDependencies(python);
    console.log('\n✅ TickTick MCP Server installed successfully!\n');
    console.log('📝 Next steps:');
    console.log('   1. Set up authentication: npx ticktick-mcp auth');
    console.log('   2. Configure LibreChat with your credentials');
    console.log('   3. Start using TickTick with Claude!\n');

  } catch (error) {
    console.error('\n❌ Installation failed:', error.message);
    console.error('\n📋 Requirements:');
    console.error('   - Python 3.10 or higher');
    console.error('   - pip (Python package manager)');
    console.error('\n💡 Install Python from: https://www.python.org/');
    process.exit(1);
  }
}

main();
