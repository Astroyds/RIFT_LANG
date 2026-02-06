# RIFT Programming Language - Installation Guide

Welcome to RIFT! This guide will help you install the RIFT programming language on your system.

## Quick Installation

### One-Line Install (Recommended)

Install RIFT with a single command using curl:

```bash
curl -sSL https://rift.astroyds.com/rift/install.sh | bash
```

Or using wget:

```bash
wget -qO- https://rift.astroyds.com/rift/install.sh | bash
```

### Manual Installation

1. Download the installer:
```bash
curl -O https://rift.astroyds.com/rift/install.sh
```

2. Make it executable:
```bash
chmod +x install.sh
```

3. Run the installer:
```bash
./install.sh
```

## Installation Options

The installer supports several options:

```bash
./install.sh [OPTIONS]

Options:
  --help              Show help message
  --version           Show installer version
  --verbose, -v       Enable verbose output
  --force, -f         Force reinstall (overwrite existing)
  --no-deps           Skip Python dependency installation
  --install-dir DIR   Custom installation directory
  --bin-dir DIR       Custom bin directory
```

### Examples

Install with verbose output:
```bash
curl -sSL https://rift.astroyds.com/rift/install.sh | bash -s -- --verbose
```

Install to custom directory:
```bash
RIFT_INSTALL_DIR=/opt/rift curl -sSL https://rift.astroyds.com/rift/install.sh | bash
```

Force reinstall:
```bash
curl -sSL https://rift.astroyds.com/rift/install.sh | bash -s -- --force
```

Skip Python dependencies:
```bash
curl -sSL https://rift.astroyds.com/rift/install.sh | bash -s -- --no-deps
```

## What Gets Installed

The installer will:

1. **Install RIFT** to `~/.rift/` (or custom directory)
2. **Create CLI commands** in `~/.local/bin/`:
   - `rift` - Main RIFT interpreter and REPL
   - `riftserver` - RIFT server runtime
3. **Install Python dependencies** (optional):
   - Database drivers (PostgreSQL, MySQL, MongoDB)
   - Cryptography libraries
   - HTTP and async libraries
4. **Configure environment** by adding to your shell config:
   - `RIFT_HOME` environment variable
   - Updates `PATH` to include RIFT commands

## Requirements

- **Python 3.8+** (required)
- **pip** (optional, for dependency installation)
- **curl** or **wget** (for downloading)
- **tar** (for extraction)

### Installing Python

#### Linux (Debian/Ubuntu)
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip
```

#### Linux (Fedora/RHEL)
```bash
sudo dnf install python3 python3-pip
```

#### macOS
```bash
brew install python3
```

Or download from [python.org](https://www.python.org/downloads/)

## Post-Installation

After installation, you may need to restart your shell or run:

```bash
source ~/.bashrc  # or ~/.zshrc for zsh
```

Or simply open a new terminal window.

## Verify Installation

Check that RIFT is installed correctly:

```bash
rift --version
rift doctor
```

## Quick Start

### Interactive REPL
```bash
rift
```

### Run a Script
```bash
rift script.rift
```

### Start a Server
```bash
riftserver app.rift
```

## Available Commands

### `rift` - Main CLI

- `rift` - Start interactive REPL
- `rift script.rift` - Run a RIFT script
- `rift --version` - Show version
- `rift --help` - Show help
- `rift doctor` - Check installation
- `rift update` - Update to latest version
- `rift uninstall` - Uninstall RIFT

### `riftserver` - Server Runtime

- `riftserver app.rift` - Start server
- `riftserver app.rift --port 3000` - Custom port
- `riftserver app.rift --watch` - Hot reload
- `riftserver app.rift --workers 4` - Multi-process

## Updating RIFT

Update to the latest version:

```bash
rift update
```

Or manually:

```bash
curl -sSL https://rift.astroyds.com/rift/install.sh | bash -s -- --force
```

## Uninstalling

Uninstall RIFT from your system:

```bash
rift uninstall
```

Or manually:

```bash
curl -sSL https://rift.astroyds.com/rift/uninstall.sh | bash
```

## Installation Directories

Default directories:
- **Installation**: `~/.rift/`
- **Commands**: `~/.local/bin/`
- **Logs**: `/tmp/rift_install_*.log`

### Custom Directories

Use environment variables to customize:

```bash
export RIFT_INSTALL_DIR=/opt/rift
export RIFT_BIN_DIR=/usr/local/bin
curl -sSL https://rift.astroyds.com/rift/install.sh | bash
```

Or use command-line options:

```bash
./install.sh --install-dir /opt/rift --bin-dir /usr/local/bin
```

## Troubleshooting

### Command not found: rift

Make sure `~/.local/bin` is in your PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Python not found

Install Python 3.8 or later. See [Requirements](#requirements) section.

### Permission denied

The installer uses `~/.rift` and `~/.local/bin` by default, which don't require sudo.
If you need system-wide installation:

```bash
sudo RIFT_INSTALL_DIR=/opt/rift RIFT_BIN_DIR=/usr/local/bin ./install.sh
```

### Dependencies failed to install

Dependencies are optional. You can install them manually later:

```bash
pip3 install -r ~/.rift/requirements.txt
```

Or skip them during installation:

```bash
curl -sSL https://rift.astroyds.com/rift/install.sh | bash -s -- --no-deps
```

### Check Installation Health

Run the doctor command:

```bash
rift doctor
```

This will show:
- RIFT_HOME location
- Python version
- Installation status
- PATH configuration

## Advanced Configuration

### Environment Variables

- `RIFT_HOME` - Installation directory (default: `~/.rift`)
- `RIFT_BIN_DIR` - Binary directory (default: `~/.local/bin`)
- `RIFT_INSTALL_DIR` - Alias for RIFT_HOME
- `PYTHON_CMD` - Python command to use (default: `python3`)

### Shell Integration

The installer automatically adds RIFT to your PATH by modifying:
- `~/.bashrc` (Bash)
- `~/.zshrc` (Zsh)
- `~/.config/fish/config.fish` (Fish)

## Platform Support

RIFT is tested on:
- ✅ Linux (Ubuntu, Debian, Fedora, Arch, etc.)
- ✅ macOS (Intel and Apple Silicon)
- ✅ WSL (Windows Subsystem for Linux)
- ⚠️ Windows (via WSL recommended)

## Getting Help

- **Documentation**: https://rift.astroyds.com/docs
- **GitHub**: https://github.com/FoundationINCCorporateTeam/RIFT
- **Examples**: https://github.com/FoundationINCCorporateTeam/RIFT/tree/main/tests/examples
- **Issues**: https://github.com/FoundationINCCorporateTeam/RIFT/issues

## Examples

After installation, try these examples:

### Hello World
```rift
# hello.rift
let name = "World"
print(`Hello, $@name#!`)
```

Run it:
```bash
rift hello.rift
```

### Web Server
```rift
# server.rift
grab http

let server = http.createServer((req, res) =! @
    res.send("Hello from RIFT!")
#)

server.listen(8080)
print("Server running on http://localhost:8080")
```

Run it:
```bash
riftserver server.rift
```

## License

RIFT is open source software. See LICENSE file for details.

---

**Ready to start coding?** 🚀

```bash
rift
```

Welcome to RIFT!
