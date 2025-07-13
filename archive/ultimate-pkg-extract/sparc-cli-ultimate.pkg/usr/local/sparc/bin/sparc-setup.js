#!/usr/bin/env node

/**
 * SPARC Setup Wizard for Claude Code Integration
 * Installs SPARC commands, hooks, and configures databases
 */

import { program } from 'commander';
import inquirer from 'inquirer';
import chalk from 'chalk';
import ora from 'ora';
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import os from 'os';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const packageRoot = path.resolve(__dirname, '..');

class SPARCSetup {
  constructor() {
    this.claudeDir = path.join(os.homedir(), '.claude');
    this.commandsDir = path.join(this.claudeDir, 'commands');
    this.userConfig = path.join(this.claudeDir, 'settings.json');
  }

  async run() {
    console.log(chalk.blue.bold('🚀 SPARC Claude Code Integration Setup'));
    console.log(chalk.dim('Installing 36-agent autonomous development system\n'));

    try {
      await this.checkPrerequisites();
      await this.setupDirectories();
      await this.installCommands();
      await this.configureHooks();
      await this.setupDatabases();
      await this.finalizeSetup();
      
      console.log(chalk.green.bold('\n✅ SPARC installation completed successfully!'));
      console.log(chalk.cyan('\nTo get started:'));
      console.log(chalk.white('1. Open any project directory'));
      console.log(chalk.white('2. Run: claude'));
      console.log(chalk.white('3. Type: /sparc "your development goal"'));
      
    } catch (error) {
      console.error(chalk.red('\n❌ Setup failed:'), error.message);
      process.exit(1);
    }
  }

  async checkPrerequisites() {
    const spinner = ora('Checking prerequisites...').start();
    
    // Check if Claude Code CLI is installed
    try {
      const { execSync } = await import('child_process');
      execSync('claude --version', { stdio: 'pipe' });
      spinner.succeed('Claude Code CLI found');
    } catch (error) {
      spinner.fail('Claude Code CLI not found');
      throw new Error('Please install Claude Code CLI first: https://docs.anthropic.com/en/docs/claude-code');
    }

    // Check Node.js version
    const nodeVersion = process.version;
    if (parseInt(nodeVersion.slice(1)) < 18) {
      spinner.fail('Node.js version too old');
      throw new Error('Node.js 18+ required');
    }
    
    spinner.succeed('Prerequisites check passed');
  }

  async setupDirectories() {
    const spinner = ora('Setting up directories...').start();
    
    await fs.ensureDir(this.claudeDir);
    await fs.ensureDir(this.commandsDir);
    await fs.ensureDir(path.join(this.commandsDir, 'sparc'));
    
    spinner.succeed('Directories created');
  }

  async installCommands() {
    const spinner = ora('Installing SPARC commands...').start();
    
    const commands = ['sparc.md', 'agents.md', 'phase.md', 'status.md', 'stopsparc.md'];
    const sourceDir = path.join(packageRoot, 'claude-commands');
    const targetDir = path.join(this.commandsDir, 'sparc');
    
    for (const command of commands) {
      await fs.copy(
        path.join(sourceDir, command),
        path.join(targetDir, command)
      );
    }
    
    spinner.succeed(`Installed ${commands.length} SPARC commands`);
  }

  async configureHooks() {
    const spinner = ora('Configuring hooks...').start();
    
    try {
      let settings = {};
      if (await fs.pathExists(this.userConfig)) {
        settings = await fs.readJson(this.userConfig);
      }

      // Add SPARC hooks
      if (!settings.hooks) settings.hooks = {};
      
      settings.hooks.PostToolUse = settings.hooks.PostToolUse || [];
      settings.hooks.PostToolUse.push({
        pattern: "Edit|Write|MultiEdit",
        command: "sparc-cli update-memory --file \"$FILE_PATH\" --namespace \"$(sparc-cli get-namespace)\"",
        description: "SPARC memory update"
      });

      await fs.writeJson(this.userConfig, settings, { spaces: 2 });
      spinner.succeed('Hooks configured');
      
    } catch (error) {
      spinner.warn('Hooks configuration failed - can be configured manually later');
    }
  }

  async setupDatabases() {
    console.log(chalk.yellow('\n🗄️  Database Configuration'));
    
    const { setupSupabase } = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'setupSupabase',
        message: 'Set up Supabase for context memory?',
        default: true
      }
    ]);

    if (setupSupabase) {
      await this.configureSupabase();
    }

    const { setupQdrant } = await inquirer.prompt([
      {
        type: 'confirm', 
        name: 'setupQdrant',
        message: 'Set up Qdrant for vector storage?',
        default: true
      }
    ]);

    if (setupQdrant) {
      await this.configureQdrant();
    }
  }

  async configureSupabase() {
    console.log(chalk.cyan('\n📊 Supabase Configuration'));
    console.log('Get your Supabase credentials from: https://supabase.com/dashboard');
    
    const supabaseConfig = await inquirer.prompt([
      {
        type: 'input',
        name: 'url',
        message: 'Supabase Project URL:',
        validate: (input) => input.includes('supabase.co') || 'Please enter a valid Supabase URL'
      },
      {
        type: 'password',
        name: 'anonKey',
        message: 'Supabase Anon Key:',
        validate: (input) => input.length > 10 || 'Please enter a valid key'
      },
      {
        type: 'password',
        name: 'serviceKey',
        message: 'Supabase Service Role Key (optional):',
      }
    ]);

    // Save to environment file
    const envPath = path.join(os.homedir(), '.sparc.env');
    const envContent = `
SUPABASE_URL=${supabaseConfig.url}
SUPABASE_ANON_KEY=${supabaseConfig.anonKey}
${supabaseConfig.serviceKey ? `SUPABASE_SERVICE_KEY=${supabaseConfig.serviceKey}` : ''}
`;
    
    await fs.writeFile(envPath, envContent.trim());
    
    console.log(chalk.green('✅ Supabase configuration saved'));
  }

  async configureQdrant() {
    console.log(chalk.cyan('\n🔍 Qdrant Configuration'));
    
    const qdrantType = await inquirer.prompt([
      {
        type: 'list',
        name: 'type',
        message: 'Qdrant setup type:',
        choices: [
          { name: 'Local Docker (Recommended)', value: 'docker' },
          { name: 'Qdrant Cloud', value: 'cloud' },
          { name: 'Custom URL', value: 'custom' }
        ]
      }
    ]);

    if (qdrantType.type === 'docker') {
      await this.setupQdrantDocker();
    } else if (qdrantType.type === 'cloud') {
      await this.configureQdrantCloud();
    } else {
      await this.configureQdrantCustom();
    }
  }

  async setupQdrantDocker() {
    const spinner = ora('Setting up Qdrant Docker container...').start();
    
    try {
      const { execSync } = await import('child_process');
      
      // Check if Docker is running
      execSync('docker info', { stdio: 'pipe' });
      
      // Start Qdrant container
      execSync(`
        docker run -d --name sparc-qdrant \\
          -p 6333:6333 \\
          -v qdrant_storage:/qdrant/storage \\
          qdrant/qdrant:latest
      `, { stdio: 'pipe' });
      
      // Add to env
      const envPath = path.join(os.homedir(), '.sparc.env');
      const envAddition = '\nQDRANT_HOST=localhost\nQDRANT_PORT=6333\n';
      await fs.appendFile(envPath, envAddition);
      
      spinner.succeed('Qdrant Docker container started');
      
    } catch (error) {
      spinner.fail('Docker setup failed');
      console.log(chalk.yellow('You can manually start Qdrant with:'));
      console.log(chalk.white('docker run -d --name sparc-qdrant -p 6333:6333 qdrant/qdrant:latest'));
    }
  }

  async configureQdrantCloud() {
    const qdrantConfig = await inquirer.prompt([
      {
        type: 'input',
        name: 'url',
        message: 'Qdrant Cloud URL:',
        validate: (input) => input.includes('qdrant') || 'Please enter a valid Qdrant URL'
      },
      {
        type: 'password',
        name: 'apiKey',
        message: 'Qdrant API Key:',
      }
    ]);

    const envPath = path.join(os.homedir(), '.sparc.env');
    const envAddition = `\nQDRANT_URL=${qdrantConfig.url}\nQDRANT_API_KEY=${qdrantConfig.apiKey}\n`;
    await fs.appendFile(envPath, envAddition);
    
    console.log(chalk.green('✅ Qdrant Cloud configuration saved'));
  }

  async configureQdrantCustom() {
    const qdrantConfig = await inquirer.prompt([
      {
        type: 'input',
        name: 'host',
        message: 'Qdrant Host:',
        default: 'localhost'
      },
      {
        type: 'input',
        name: 'port',
        message: 'Qdrant Port:',
        default: '6333'
      }
    ]);

    const envPath = path.join(os.homedir(), '.sparc.env');
    const envAddition = `\nQDRANT_HOST=${qdrantConfig.host}\nQDRANT_PORT=${qdrantConfig.port}\n`;
    await fs.appendFile(envPath, envAddition);
    
    console.log(chalk.green('✅ Qdrant configuration saved'));
  }

  async finalizeSetup() {
    const spinner = ora('Finalizing setup...').start();
    
    // Create SPARC CLI symlink for global access
    const sparcCliPath = path.join(packageRoot, 'bin', 'sparc-cli.js');
    
    try {
      const { execSync } = await import('child_process');
      execSync(`chmod +x "${sparcCliPath}"`);
      
      // Add to PATH via shell profile
      const shell = process.env.SHELL;
      if (shell && shell.includes('zsh')) {
        const zshrc = path.join(os.homedir(), '.zshrc');
        const pathAddition = `\n# SPARC CLI\nexport PATH="${path.dirname(sparcCliPath)}:$PATH"\n`;
        await fs.appendFile(zshrc, pathAddition);
      }
      
    } catch (error) {
      // Non-critical error
    }
    
    spinner.succeed('Setup finalized');
  }
}

// CLI Interface
program
  .name('sparc-setup')
  .description('SPARC Claude Code Integration Setup')
  .version('1.0.0')
  .action(async () => {
    const setup = new SPARCSetup();
    await setup.run();
  });

program.parse();