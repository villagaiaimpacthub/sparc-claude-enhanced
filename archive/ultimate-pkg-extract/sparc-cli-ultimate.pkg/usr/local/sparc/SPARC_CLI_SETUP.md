# 🚀 SPARC CLI Global Package - Team Setup Guide

Your complete autonomous software development system is now available as a global package!

## 📦 Repository

**GitHub:** https://github.com/villagaiaimpacthub/claude-cli

## 🎯 Quick Team Installation

### For Team Members

```bash
# 1. Install the global package
pip install git+https://github.com/villagaiaimpacthub/claude-cli.git

# 2. Run the interactive installer
sparc-install

# 3. Initialize in any project
cd your-project
sparc init

# 4. Use in Claude Code CLI
/sparc "build my application"
```

### Alternative Installation (Development)

```bash
# Clone and install locally
git clone https://github.com/villagaiaimpacthub/claude-cli.git
cd claude-cli
pip install -e .
sparc-install
```

## 🛠 What Each Team Member Gets

### **Global Installation**
- 36 AI agents system
- Cross-platform support (macOS, Windows, Linux)
- Docker container management
- Supabase cloud integration
- Interactive installer

### **Per-Project Setup**
Projects only need minimal files:
```
your-project/
├── .sparc/
│   ├── project.json          # Just project config
│   └── session_state.json    # Session state
└── .claude/commands/         # Lightweight command wrappers
    ├── sparc.md
    ├── status.md
    └── ...
```

### **Claude Code Integration**
Familiar slash commands:
- `/sparc "your development goal"`
- `/stopsparc` - Exit SPARC mode
- `/status` - Project status
- `/phase` - Current development phase
- `/agents` - Show agent activity

## 📋 Installation Steps Details

### 1. System Requirements Check
- Python 3.11+
- Docker Desktop
- Claude Code CLI

### 2. Database Setup
**Important:** Set up your databases before using SPARC:

#### Supabase Setup (Required)
1. Create account at [supabase.com](https://supabase.com)
2. Create new project and get API credentials
3. Run the SQL schema in your Supabase SQL Editor
4. **Full guide:** `docs/SUPABASE_SETUP.md`

#### Qdrant Setup (Automated)
- Docker container auto-managed by `sparc-init`
- No manual configuration needed

### 3. Interactive Installer (`sparc-install`)
- Automated Docker setup
- Supabase configuration wizard
- Database schema verification
- System verification

### 4. Project Initialization (`sparc init`)
- Creates minimal project files
- Sets up Claude Code commands
- Configures session management

## 🔧 Management Commands

```bash
# System status
sparc status

# Docker management
sparc docker start|stop|restart|status

# Configuration
sparc config show|set|get

# Project management
sparc run "development goal"
```

## 🌟 Key Benefits

✅ **Install Once, Use Everywhere** - No more copying complex folders  
✅ **Automated Setup** - Interactive installer handles everything  
✅ **Minimal Project Files** - Clean project directories  
✅ **Cross-Platform** - Works on all development environments  
✅ **Easy Updates** - Global package updates  
✅ **Team Consistency** - Same setup for everyone  

## 📚 Documentation

- **Supabase Setup:** `docs/SUPABASE_SETUP.md` ⭐ **Essential**
- **Installation Guide:** `docs/INSTALLATION.md`
- **User Guide:** `docs/USER_GUIDE.md`
- **Examples:** `docs/EXAMPLES.md`
- **Troubleshooting:** `docs/TROUBLESHOOTING.md`

## 🚨 Migration from Existing Setup

If team members have the old project-specific setup:

```bash
# 1. Install global package
pip install git+https://github.com/villagaiaimpacthub/claude-cli.git

# 2. Run installer
sparc-install

# 3. In existing projects, reinitialize
cd existing-project
rm -rf .sparc .claude  # Remove old setup
sparc init             # Create new minimal setup

# 4. Continue using familiar /sparc commands
```

## 🔄 Publishing to PyPI (Future)

When ready for public release:

```bash
# Build package
python scripts/build.py

# Upload to PyPI
python -m twine upload dist/*

# Then team can install with:
pip install sparc-cli
```

## 💬 Team Communication

**Share with your team:**

> 🚀 **SPARC CLI is now available as a global package!**
> 
> **Quick setup:**
> 1. **Setup Supabase:** Follow `docs/SUPABASE_SETUP.md` ⭐
> 2. `pip install git+https://github.com/villagaiaimpacthub/claude-cli.git`
> 3. `sparc-install`
> 4. `cd your-project && sparc init`
> 5. Use `/sparc` in Claude Code as usual
> 
> **⚠️ Important:** Set up Supabase database first - it's required for the 36-agent system!
> 
> **Docs:** https://github.com/villagaiaimpacthub/claude-cli

---

**🎉 Your team now has professional, scalable SPARC CLI deployment!**

The complex setup process is eliminated while maintaining the familiar Claude Code workflow.