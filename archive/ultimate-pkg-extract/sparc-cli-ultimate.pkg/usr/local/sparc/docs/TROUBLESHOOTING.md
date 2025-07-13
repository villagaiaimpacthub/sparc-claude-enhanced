# SPARC CLI Troubleshooting Guide

This guide helps you diagnose and fix common issues with SPARC CLI.

## Quick Diagnostic Commands

Start troubleshooting with these commands:

```bash
# Check overall system status
sparc status

# Verify installation
sparc-install check

# Check Docker containers
sparc docker status

# View configuration
sparc config show
```

## Installation Issues

### Python Version Error

**Problem:** `Python 3.11+ required, found 3.10`

**Solution:**
```bash
# Check current version
python --version

# Install Python 3.11+ (macOS with Homebrew)
brew install python@3.11

# Install Python 3.11+ (Ubuntu/Debian)
sudo apt update
sudo apt install python3.11

# Update PATH if needed
export PATH="/usr/local/opt/python@3.11/bin:$PATH"
```

### Package Installation Fails

**Problem:** `pip install sparc-cli` fails

**Solutions:**

1. **Update pip:**
```bash
python -m pip install --upgrade pip
```

2. **Use virtual environment:**
```bash
python -m venv sparc-env
source sparc-env/bin/activate  # Windows: sparc-env\Scripts\activate
pip install sparc-cli
```

3. **Install from source:**
```bash
git clone https://github.com/your-org/sparc-cli
cd sparc-cli
pip install -e .
```

### Permission Errors (Linux/macOS)

**Problem:** Permission denied errors

**Solution:**
```bash
# Install with user flag
pip install --user sparc-cli

# Or fix permissions
sudo chown -R $USER:$USER ~/.local

# For Docker permissions
sudo usermod -aG docker $USER
# Log out and log back in
```

## Docker Issues

### Docker Not Found

**Problem:** `Docker is not available`

**Solution:**

**macOS:**
1. Download Docker Desktop from docker.com
2. Install and start Docker Desktop
3. Wait for whale icon in menu bar

**Windows:**
1. Download Docker Desktop from docker.com
2. Install and restart if prompted
3. Start Docker Desktop

**Linux:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Log out and log back in
```

### Container Start Failures

**Problem:** `Failed to start Docker containers`

**Diagnostic:**
```bash
# Check Docker status
docker --version
docker info

# Check container logs
docker logs sparc-qdrant
docker logs sparc-postgres

# Check port conflicts
netstat -tulpn | grep :6336
netstat -tulpn | grep :5432
```

**Solutions:**

1. **Port conflicts:**
```bash
# Edit docker-compose.yml to use different ports
# Or stop conflicting services
sudo lsof -ti:6336 | xargs sudo kill -9
```

2. **Memory issues:**
```bash
# Increase Docker memory limit in Docker Desktop settings
# Or reduce container memory:
sparc config set docker.qdrant_memory_limit "1G"
```

3. **Clean restart:**
```bash
# Stop all containers
sparc docker stop

# Remove containers
docker system prune -f

# Restart
sparc docker start
```

### Container Health Issues

**Problem:** Containers start but aren't healthy

**Diagnostic:**
```bash
# Check container health
docker ps -a

# Test Qdrant
curl http://localhost:6336/health

# Test PostgreSQL
pg_isready -h localhost -p 5432
```

**Solutions:**

1. **Wait for startup:**
```bash
# Containers may take 30-60 seconds to be ready
# Check logs for "ready to accept connections"
docker logs sparc-postgres
```

2. **Network issues:**
```bash
# Reset Docker networks
docker network prune -f
sparc docker restart
```

## Supabase Issues

### Connection Failures

**Problem:** `Supabase connection failed`

**Diagnostic:**
```bash
# Check configuration
sparc config get supabase.project_url
sparc config get supabase.anon_key

# Test connection manually
curl -H "apikey: your-anon-key" "https://your-project.supabase.co/rest/v1/"
```

**Solutions:**

1. **Invalid URL:**
```bash
# Fix URL format
sparc config set supabase.project_url "https://your-project.supabase.co"
```

2. **Invalid keys:**
```bash
# Get new keys from Supabase dashboard > Settings > API
sparc config set supabase.anon_key "new-anon-key"
```

3. **Network/firewall:**
```bash
# Test internet connection
ping supabase.co

# Check corporate firewall/proxy settings
```

### Database Schema Issues

**Problem:** Tables don't exist or have wrong structure

**Solution:**
```bash
# Get schema file
cat ~/.sparc/supabase_schema.sql

# Apply in Supabase dashboard:
# 1. Go to SQL Editor
# 2. Paste schema
# 3. Execute
```

## Agent System Issues

### Agents Not Responding

**Problem:** `/sparc` command hangs or agents don't work

**Diagnostic:**
```bash
# Check system status
sparc status

# Check agent configuration
sparc config show | grep agent_system

# Check logs
docker logs sparc-postgres
docker logs sparc-qdrant
```

**Solutions:**

1. **Restart system:**
```bash
/stopsparc
sparc docker restart
/sparc "continue with my project"
```

2. **Reduce agent load:**
```bash
sparc config set agent_system.max_concurrent_agents 2
sparc config set agent_system.agent_timeout_minutes 5
```

3. **Reset session:**
```bash
# Remove session state
rm .sparc/session_state.json
sparc init
```

### Memory Issues

**Problem:** System runs out of memory or slows down

**Solutions:**

1. **Reduce memory usage:**
```bash
# Limit concurrent agents
sparc config set agent_system.max_concurrent_agents 3

# Reduce Docker memory
# Edit Docker Desktop settings or docker-compose.yml
```

2. **Clear memory:**
```bash
# Restart containers
sparc docker restart

# Clear vector database
docker exec sparc-qdrant qdrant-cli collections delete --collection-name sparc
```

### Performance Issues

**Problem:** Agents are slow or timeout

**Solutions:**

1. **Optimize settings:**
```bash
# Increase timeouts
sparc config set agent_system.agent_timeout_minutes 15

# Reduce concurrent agents
sparc config set agent_system.max_concurrent_agents 2
```

2. **Check resources:**
```bash
# Monitor system resources
top
htop
docker stats

# Check disk space
df -h
```

## Claude Code Integration Issues

### Slash Commands Not Available

**Problem:** `/sparc` doesn't appear in Claude Code

**Solutions:**

1. **Verify project initialization:**
```bash
# Check files exist
ls .claude/commands/
cat .claude/commands/sparc.md
```

2. **Reinitialize project:**
```bash
sparc init --force
```

3. **Restart Claude Code:**
```bash
# Exit and restart Claude Code CLI
```

### Commands Execute But Don't Work

**Problem:** `/sparc` runs but doesn't do anything

**Diagnostic:**
```bash
# Test CLI directly
sparc run --project-id your-project-id "test goal"

# Check project configuration
cat .sparc/project.json
```

**Solutions:**

1. **Fix project configuration:**
```bash
# Regenerate project files
sparc init --force
```

2. **Check global installation:**
```bash
# Verify global installation
which sparc
sparc --version
```

## Configuration Issues

### Config File Corruption

**Problem:** `Could not load global config`

**Solution:**
```bash
# Backup and reset config
mv ~/.sparc/config.json ~/.sparc/config.json.backup
sparc-install
```

### Missing Configuration

**Problem:** SPARC says it's not configured

**Solution:**
```bash
# Run installer to reconfigure
sparc-install

# Or manually configure
sparc config set supabase.project_url "https://your-project.supabase.co"
sparc config set supabase.anon_key "your-key"
```

## Project Issues

### Project Initialization Fails

**Problem:** `sparc init` fails

**Solutions:**

1. **Check permissions:**
```bash
# Ensure write permissions
chmod 755 .
```

2. **Clean and retry:**
```bash
# Remove partial files
rm -rf .sparc .claude
sparc init
```

### Session State Issues

**Problem:** SPARC forgets previous work

**Solutions:**

1. **Check session file:**
```bash
cat .sparc/session_state.json
```

2. **Reset session:**
```bash
rm .sparc/session_state.json
/sparc "continue with my previous work on [describe project]"
```

## Performance Optimization

### System Running Slow

**Solutions:**

1. **Reduce resource usage:**
```bash
# Limit agents
sparc config set agent_system.max_concurrent_agents 2

# Reduce Docker memory
# Edit Docker Desktop settings
```

2. **Optimize Docker:**
```bash
# Clean unused resources
docker system prune -f

# Restart Docker Desktop
```

3. **Close other applications:**
```bash
# Free up system memory
# Close unnecessary browser tabs, applications
```

### Database Performance

**Solutions:**

1. **Restart databases:**
```bash
sparc docker restart
```

2. **Clear old data:**
```bash
# Connect to PostgreSQL and clean old records
# Be careful with this - backup first!
```

## Error Messages Reference

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `Docker is not available` | Docker not installed/running | Install Docker Desktop |
| `Python 3.11+ required` | Old Python version | Upgrade Python |
| `Supabase connection failed` | Invalid credentials | Check API keys |
| `Permission denied` | File/Docker permissions | Fix permissions |
| `Port already in use` | Port conflict | Change ports or stop conflicting service |
| `Could not load config` | Corrupted config file | Reset configuration |
| `Project not initialized` | Missing .sparc directory | Run `sparc init` |

## Getting More Help

### Collecting Debug Information

When reporting issues, include:

```bash
# System information
sparc --version
python --version
docker --version
uname -a  # Linux/macOS
systeminfo  # Windows

# Configuration
sparc config show

# Status
sparc status
sparc docker status

# Logs
docker logs sparc-qdrant
docker logs sparc-postgres
```

### Where to Get Help

1. **Documentation**
   - Check other docs in this directory
   - Read the README.md

2. **GitHub Issues**
   - Search existing issues
   - Create new issue with debug info
   - https://github.com/your-org/sparc-cli/issues

3. **Community**
   - GitHub Discussions
   - Discord/Slack (if available)

4. **Logs and Debug**
   - Enable verbose logging
   - Check container logs
   - Use diagnostic commands

### Reset Everything

**Last resort - complete reset:**

```bash
# Stop all services
sparc docker stop

# Remove all SPARC data
rm -rf ~/.sparc

# Remove Docker containers
docker rm -f sparc-qdrant sparc-postgres

# Reinstall
pip uninstall sparc-cli
pip install sparc-cli
sparc-install
```

**⚠️ Warning:** This removes all SPARC configuration and project data. Only use if nothing else works and you're okay losing your SPARC settings.

---

**Still having issues?** Please create a GitHub issue with:
1. Your operating system and version
2. Python and Docker versions
3. Complete error messages
4. Output from diagnostic commands
5. Steps to reproduce the problem