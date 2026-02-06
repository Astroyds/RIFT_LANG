#!/bin/bash
################################################################################
# RIFT Programming Language - Universal Installer
# Version: 1.0.0
# Website: https://rift.astroyds.com
# 
# Installation Methods:
#   curl -sSL https://rift.astroyds.com/rift/install.sh | bash
#   wget -qO- https://rift.astroyds.com/rift/install.sh | bash
#
# This installer will:
#   - Install the RIFT programming language
#   - Set up the 'rift' and 'riftserver' CLI commands
#   - Install Python dependencies (optional)
#   - Configure environment variables
#   - Provide comprehensive error handling and logging
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Installation configuration
RIFT_VERSION="0.1.0"
INSTALLER_VERSION="2.0.0"
INSTALL_DIR="${RIFT_INSTALL_DIR:-$HOME/.rift}"
BIN_DIR="${RIFT_BIN_DIR:-$HOME/.local/bin}"
RIFT_REPO_URL="https://rift.astroyds.com/rift/source"
RIFT_TAR_URL="https://github.com/FoundationINCCorporateTeam/RIFT/archive/refs/heads/main.tar.gz"
LOG_FILE="/tmp/rift_install_$(date +%Y%m%d_%H%M%S).log"
INSTALL_DEPS=true
VERBOSE=false
FORCE_INSTALL=false
DRY_RUN=false

# Additional formatting
DIM='\033[2m'
UNDERLINE='\033[4m'
WHITE='\033[1;37m'

# System detection
OS_TYPE=$(uname -s)
ARCH_TYPE=$(uname -m)

################################################################################
# Helper Functions
################################################################################

print_header() {
    clear 2>/dev/null || true
    echo -e "${CYAN}${BOLD}"
    echo "╔═══════════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                           ║"
    echo "║              RIFT Programming Language - Installer                        ║"
    echo "║              Enterprise Installation Wizard                               ║"
    echo "║                                                                           ║"
    echo "║              Version: ${GREEN}${RIFT_VERSION}${CYAN}  |  Installer: ${GREEN}v${INSTALLER_VERSION}${CYAN}                      ║"
    echo "║              https://rift.astroyds.com                                    ║"
    echo "║                                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo -e "${DIM}One command to rule them all - Zero setup, infinite possibilities${NC}"
    echo ""
}

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    
    case $level in
        INFO)
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
        SUCCESS)
            echo -e "${GREEN}[✓]${NC} $message"
            ;;
        WARNING)
            echo -e "${YELLOW}[⚠]${NC} $message"
            ;;
        ERROR)
            echo -e "${RED}[✗]${NC} $message"
            ;;
        STEP)
            echo -e "${MAGENTA}[→]${NC} ${BOLD}$message${NC}"
            ;;
    esac
    
    if [ "$VERBOSE" = true ]; then
        echo -e "${CYAN}    Details: $message${NC}" >&2
    fi
}

print_progress() {
    local current=$1
    local total=$2
    local task=$3
    local percent=$((current * 100 / total))
    local filled=$((percent / 2))
    local empty=$((50 - filled))
    
    printf "\r${CYAN}["
    printf "%${filled}s" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '░'
    printf "] ${BOLD}%3d%%${NC} - ${WHITE}%s${NC}" "$percent" "$task"
    
    if [ $current -eq $total ]; then
        echo ""
    fi
}

check_command() {
    command -v "$1" >/dev/null 2>&1
}

get_directory_size() {
    local dir=$1
    if [ -d "$dir" ]; then
        du -sb "$dir" 2>/dev/null | awk '{print $1}' || echo "0"
    else
        echo "0"
    fi
}

format_bytes() {
    local bytes=$1
    if [ $bytes -lt 1024 ]; then
        echo "${bytes}B"
    elif [ $bytes -lt 1048576 ]; then
        echo "$((bytes / 1024))KB"
    elif [ $bytes -lt 1073741824 ]; then
        echo "$((bytes / 1048576))MB"
    else
        echo "$((bytes / 1073741824))GB"
    fi
}

check_python() {
    log STEP "Checking Python installation..."
    
    if check_command python3; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        log SUCCESS "Found Python $PYTHON_VERSION"
        return 0
    elif check_command python; then
        PYTHON_CMD="python"
        PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
        
        # Check if it's Python 3
        if echo "$PYTHON_VERSION" | grep -q "^3\."; then
            log SUCCESS "Found Python $PYTHON_VERSION"
            return 0
        else
            log ERROR "Python 3 is required, but found Python $PYTHON_VERSION"
            return 1
        fi
    else
        log ERROR "Python 3 is not installed"
        return 1
    fi
}

install_python_hint() {
    echo -e "\n${YELLOW}Python 3 is required to run RIFT.${NC}"
    echo -e "Please install Python 3.8 or later:\n"
    
    case $OS_TYPE in
        Linux)
            if check_command apt-get; then
                echo -e "  ${CYAN}sudo apt-get update && sudo apt-get install python3 python3-pip${NC}"
            elif check_command yum; then
                echo -e "  ${CYAN}sudo yum install python3 python3-pip${NC}"
            elif check_command dnf; then
                echo -e "  ${CYAN}sudo dnf install python3 python3-pip${NC}"
            elif check_command pacman; then
                echo -e "  ${CYAN}sudo pacman -S python python-pip${NC}"
            fi
            ;;
        Darwin)
            echo -e "  ${CYAN}brew install python3${NC}"
            echo -e "  or download from: https://www.python.org/downloads/"
            ;;
        *)
            echo -e "  Visit: https://www.python.org/downloads/"
            ;;
    esac
    echo ""
}

check_dependencies() {
    log STEP "Checking system dependencies..."
    
    local missing_deps=()
    
    # Check for essential tools
    if ! check_command curl && ! check_command wget; then
        missing_deps+=("curl or wget")
    fi
    
    if ! check_command tar; then
        missing_deps+=("tar")
    fi
    
    if ! check_command git; then
        log WARNING "git is not installed (optional, but recommended)"
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log ERROR "Missing dependencies: ${missing_deps[*]}"
        return 1
    fi
    
    log SUCCESS "All required dependencies found"
    return 0
}

create_directories() {
    log STEP "Creating installation directories..."
    
    mkdir -p "$INSTALL_DIR" 2>/dev/null || {
        log ERROR "Failed to create directory: $INSTALL_DIR"
        return 1
    }
    
    mkdir -p "$BIN_DIR" 2>/dev/null || {
        log ERROR "Failed to create directory: $BIN_DIR"
        return 1
    }
    
    log SUCCESS "Directories created successfully"
    return 0
}

download_rift() {
    log STEP "Downloading RIFT source code..."
    
    local temp_dir=$(mktemp -d)
    cd "$temp_dir"
    
    # Try multiple download methods
    if check_command curl; then
        log INFO "Using curl to download..."
        if curl -fsSL "$RIFT_TAR_URL" -o rift.tar.gz; then
            log SUCCESS "Downloaded successfully"
        else
            log ERROR "Failed to download using curl"
            return 1
        fi
    elif check_command wget; then
        log INFO "Using wget to download..."
        if wget -q "$RIFT_TAR_URL" -O rift.tar.gz; then
            log SUCCESS "Downloaded successfully"
        else
            log ERROR "Failed to download using wget"
            return 1
        fi
    else
        log ERROR "No download tool available"
        return 1
    fi
    
    # Extract archive
    log STEP "Extracting archive..."
    tar -xzf rift.tar.gz || {
        log ERROR "Failed to extract archive"
        return 1
    }
    
    # Find the extracted directory (GitHub adds -main or -master suffix)
    local extracted_dir=$(find . -maxdepth 1 -type d -name "RIFT-*" -o -name "rift-*" | head -n 1)
    if [ -z "$extracted_dir" ]; then
        log ERROR "Could not find extracted directory"
        log ERROR "Available directories:"
        ls -la
        return 1
    fi
    
    log INFO "Found extracted directory: $extracted_dir"
    
    # Copy files to installation directory (exclude tests)
    log STEP "Installing RIFT to $INSTALL_DIR..."
    
    # Remove old installation if exists and force flag is set
    if [ "$FORCE_INSTALL" = true ] && [ -d "$INSTALL_DIR/src" ]; then
        log INFO "Removing previous installation..."
        rm -rf "$INSTALL_DIR"/{src,*.py,*.md,*.txt}
    fi
    
    # Copy main files
    cp "$extracted_dir"/RIFT/*.py "$INSTALL_DIR/" 2>/dev/null || cp "$extracted_dir"/*.py "$INSTALL_DIR/" 2>/dev/null || true
    cp "$extracted_dir"/RIFT/*.md "$INSTALL_DIR/" 2>/dev/null || cp "$extracted_dir"/*.md "$INSTALL_DIR/" 2>/dev/null || true
    cp "$extracted_dir"/RIFT/*.txt "$INSTALL_DIR/" 2>/dev/null || cp "$extracted_dir"/*.txt "$INSTALL_DIR/" 2>/dev/null || true
    
    # Copy source directory - try multiple possible locations
    if [ -d "$extracted_dir/RIFT/src" ]; then
        cp -r "$extracted_dir/RIFT/src" "$INSTALL_DIR/"
        log SUCCESS "Copied source from RIFT/src"
    elif [ -d "$extracted_dir/src" ]; then
        cp -r "$extracted_dir/src" "$INSTALL_DIR/"
        log SUCCESS "Copied source from src"
    else
        log ERROR "Source directory not found in:"
        log ERROR "  - $extracted_dir/RIFT/src"
        log ERROR "  - $extracted_dir/src"
        log ERROR "Directory contents:"
        ls -la "$extracted_dir/"
        return 1
    fi
    
    # Clean up
    cd /tmp
    rm -rf "$temp_dir"
    
    log SUCCESS "RIFT installed to $INSTALL_DIR"
    return 0
}

create_cli_wrapper() {
    log STEP "Creating CLI wrapper scripts..."
    
    # Create 'rift' command
    cat > "$BIN_DIR/rift" << 'EOFRIFT'
#!/bin/bash
# RIFT Programming Language CLI
# Auto-generated by installer

RIFT_HOME="${RIFT_HOME:-$HOME/.rift}"
PYTHON_CMD="${PYTHON_CMD:-python3}"

# Check if RIFT is installed
if [ ! -f "$RIFT_HOME/rift.py" ]; then
    echo "Error: RIFT is not installed in $RIFT_HOME"
    echo "Please run: curl -sSL https://rift.astroyds.com/rift/install.sh | bash"
    exit 1
fi

# Check for subcommands
case "$1" in
    version|--version|-v)
        exec "$PYTHON_CMD" "$RIFT_HOME/rift.py" --version
        ;;
    help|--help|-h)
        exec "$PYTHON_CMD" "$RIFT_HOME/rift.py" --help
        ;;
    repl)
        exec "$PYTHON_CMD" "$RIFT_HOME/rift.py" repl
        ;;
    update)
        echo "Updating RIFT..."
        curl -sSL https://rift.astroyds.com/rift/install.sh | bash -s -- --force
        ;;
    uninstall)
        echo "Uninstalling RIFT..."
        curl -sSL https://rift.astroyds.com/rift/uninstall.sh | bash
        ;;
    doctor)
        echo "RIFT Environment Check"
        echo "======================"
        echo "RIFT_HOME: $RIFT_HOME"
        echo "Python: $($PYTHON_CMD --version 2>&1)"
        echo "Installation: $([ -d "$RIFT_HOME/src" ] && echo "OK" || echo "MISSING")"
        echo "PATH: $(echo $PATH | tr ':' '\n' | grep -E "rift|\.local/bin" || echo "Not in PATH")"
        ;;
    *)
        # Run script or REPL
        exec "$PYTHON_CMD" "$RIFT_HOME/rift.py" "$@"
        ;;
esac
EOFRIFT
    
    chmod +x "$BIN_DIR/rift"
    log SUCCESS "Created 'rift' command"
    
    # Create 'riftserver' command
    cat > "$BIN_DIR/riftserver" << 'EOFSERVER'
#!/bin/bash
# RIFT Server Runtime CLI
# Auto-generated by installer

RIFT_HOME="${RIFT_HOME:-$HOME/.rift}"
PYTHON_CMD="${PYTHON_CMD:-python3}"

# Check if RIFT is installed
if [ ! -f "$RIFT_HOME/riftserver.py" ]; then
    echo "Error: RIFT is not installed in $RIFT_HOME"
    echo "Please run: curl -sSL https://rift.astroyds.com/rift/install.sh | bash"
    exit 1
fi

# Run riftserver
exec "$PYTHON_CMD" "$RIFT_HOME/riftserver.py" "$@"
EOFSERVER
    
    chmod +x "$BIN_DIR/riftserver"
    log SUCCESS "Created 'riftserver' command"
    
    return 0
}

install_python_dependencies() {
    if [ "$INSTALL_DEPS" = false ]; then
        log INFO "Skipping Python dependencies (use --deps to install)"
        return 0
    fi
    
    log STEP "Installing Python dependencies..."
    
    if [ ! -f "$INSTALL_DIR/requirements.txt" ]; then
        log WARNING "requirements.txt not found, skipping dependency installation"
        return 0
    fi
    
    # Check if pip is available
    if ! check_command pip3 && ! check_command pip; then
        log WARNING "pip is not installed. Dependencies will not be installed."
        log INFO "Install pip with: $PYTHON_CMD -m ensurepip --upgrade"
        return 0
    fi
    
    local PIP_CMD=$(check_command pip3 && echo "pip3" || echo "pip")
    
    log INFO "Installing dependencies with $PIP_CMD..."
    
    if $PIP_CMD install -r "$INSTALL_DIR/requirements.txt" --user -q 2>&1 | tee -a "$LOG_FILE"; then
        log SUCCESS "Python dependencies installed"
    else
        log WARNING "Some dependencies failed to install (this is optional)"
        log INFO "You can install them manually later with:"
        log INFO "  $PIP_CMD install -r $INSTALL_DIR/requirements.txt"
    fi
    
    return 0
}

configure_environment() {
    log STEP "Configuring environment..."
    
    # Detect shell configuration file
    local shell_config=""
    local shell_name=$(basename "$SHELL")
    
    case $shell_name in
        bash)
            if [ -f "$HOME/.bashrc" ]; then
                shell_config="$HOME/.bashrc"
            elif [ -f "$HOME/.bash_profile" ]; then
                shell_config="$HOME/.bash_profile"
            fi
            ;;
        zsh)
            shell_config="$HOME/.zshrc"
            ;;
        fish)
            shell_config="$HOME/.config/fish/config.fish"
            ;;
        *)
            log WARNING "Unknown shell: $shell_name"
            ;;
    esac
    
    if [ -n "$shell_config" ] && [ -f "$shell_config" ]; then
        # Check if PATH already contains BIN_DIR
        if ! grep -q "$BIN_DIR" "$shell_config" 2>/dev/null; then
            log INFO "Adding $BIN_DIR to PATH in $shell_config"
            
            echo "" >> "$shell_config"
            echo "# RIFT Programming Language" >> "$shell_config"
            echo "export RIFT_HOME=\"$INSTALL_DIR\"" >> "$shell_config"
            echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$shell_config"
            
            log SUCCESS "Environment configured"
        else
            log INFO "PATH already configured"
        fi
    fi
    
    # Export for current session
    export RIFT_HOME="$INSTALL_DIR"
    export PATH="$BIN_DIR:$PATH"
    
    return 0
}

verify_installation() {
    log STEP "Verifying installation..."
    
    local errors=0
    
    # Check if rift command exists
    if [ -x "$BIN_DIR/rift" ]; then
        log SUCCESS "rift command installed"
    else
        log ERROR "rift command not found"
        errors=$((errors + 1))
    fi
    
    # Check if riftserver command exists
    if [ -x "$BIN_DIR/riftserver" ]; then
        log SUCCESS "riftserver command installed"
    else
        log ERROR "riftserver command not found"
        errors=$((errors + 1))
    fi
    
    # Check if source files exist
    if [ -d "$INSTALL_DIR/src" ]; then
        log SUCCESS "Source files installed"
    else
        log ERROR "Source files not found"
        errors=$((errors + 1))
    fi
    
    # Check if main scripts exist
    if [ -f "$INSTALL_DIR/rift.py" ] && [ -f "$INSTALL_DIR/riftserver.py" ]; then
        log SUCCESS "Main scripts installed"
    else
        log ERROR "Main scripts not found"
        errors=$((errors + 1))
    fi
    
    return $errors
}

print_completion_message() {
    echo ""
    echo -e "${GREEN}${BOLD}╔═══════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}${BOLD}║                                                                           ║${NC}"
    echo -e "${GREEN}${BOLD}║              ✓ RIFT Installation Completed Successfully!                  ║${NC}"
    echo -e "${GREEN}${BOLD}║                                                                           ║${NC}"
    echo -e "${GREEN}${BOLD}╚═══════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -e "${CYAN}${BOLD}Installation Summary:${NC}"
    echo -e "${DIM}───────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "  ${WHITE}Location:${NC}        ${BOLD}$INSTALL_DIR${NC}"
    echo -e "  ${WHITE}Commands:${NC}        ${BOLD}$BIN_DIR${NC}"
    echo -e "  ${WHITE}Version:${NC}         ${BOLD}$RIFT_VERSION${NC}"
    echo -e "  ${WHITE}Log file:${NC}        ${BOLD}$LOG_FILE${NC}"
    
    # Show installation size
    local install_size=$(get_directory_size "$INSTALL_DIR")
    echo -e "  ${WHITE}Size:${NC}            ${BOLD}$(format_bytes $install_size)${NC}"
    echo ""
    
    echo -e "${CYAN}${BOLD}🚀 Quick Start Commands:${NC}"
    echo -e "${DIM}───────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "  ${GREEN}rift${NC}                     ${DIM}# Start interactive REPL${NC}"
    echo -e "  ${GREEN}rift script.rift${NC}         ${DIM}# Run a RIFT script${NC}"
    echo -e "  ${GREEN}riftserver app.rift${NC}      ${DIM}# Start a RIFT web server${NC}"
    echo -e "  ${GREEN}rift --help${NC}              ${DIM}# Show help message${NC}"
    echo -e "  ${GREEN}rift doctor${NC}              ${DIM}# Verify installation${NC}"
    echo ""
    
    echo -e "${CYAN}${BOLD}🔧 Utility Commands:${NC}"
    echo -e "${DIM}───────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "  ${GREEN}rift update${NC}              ${DIM}# Update to latest version${NC}"
    echo -e "  ${GREEN}rift uninstall${NC}           ${DIM}# Remove RIFT from system${NC}"
    echo -e "  ${GREEN}rift version${NC}             ${DIM}# Show version info${NC}"
    echo ""
    
    echo -e "${YELLOW}${BOLD}⚡ Important:${NC}"
    echo -e "${DIM}───────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "  Restart your shell or run:  ${CYAN}source ~/.bashrc${NC}  ${DIM}(or ~/.zshrc)${NC}"
    echo -e "  Or simply open a new terminal window."
    echo ""
    
    echo -e "${CYAN}${BOLD}📚 Resources:${NC}"
    echo -e "${DIM}───────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "  ${WHITE}Documentation:${NC}   ${CYAN}https://rift.astroyds.com/docs${NC}"
    echo -e "  ${WHITE}Examples:${NC}        ${CYAN}https://github.com/FoundationINCCorporateTeam/RIFT/tree/main/tests/examples${NC}"
    echo -e "  ${WHITE}GitHub:${NC}          ${CYAN}https://github.com/FoundationINCCorporateTeam/RIFT${NC}"
    echo ""
    
    echo -e "${GREEN}${BOLD}Welcome to RIFT! Happy coding! 🎉${NC}"
    echo ""
}

print_usage() {
    cat << 'EOF'
RIFT Installer - Enterprise Edition

Usage: ./install.sh [OPTIONS]

Options:
  --help, -h            Show this help message
  --version             Show installer version
  --verbose, -v         Enable verbose output and debugging
  --force, -f           Force reinstall (overwrite existing installation)
  --no-deps             Skip Python dependency installation
  --dry-run             Simulate installation without making changes
  --install-dir DIR     Set custom installation directory
  --bin-dir DIR         Set custom binary directory

Environment Variables:
  RIFT_INSTALL_DIR      Installation directory (default: ~/.rift)
  RIFT_BIN_DIR          Binary directory (default: ~/.local/bin)

Examples:
  # Standard installation
  curl -sSL https://rift.astroyds.com/rift/install.sh | bash

  # Force reinstall with verbose output
  ./install.sh --verbose --force

  # Custom installation directory
  RIFT_INSTALL_DIR=/opt/rift ./install.sh

  # Install without dependencies
  curl -sSL https://rift.astroyds.com/rift/install.sh | bash -s -- --no-deps

For more information:
  Website:     https://rift.astroyds.com
  Docs:        https://rift.astroyds.com/docs/installation
  GitHub:      https://github.com/FoundationINCCorporateTeam/RIFT

EOF
}

cleanup_on_error() {
    local exit_code=$?
    log ERROR "Installation failed with exit code: $exit_code"
    echo ""
    echo -e "${RED}${BOLD}╔═══════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}${BOLD}║                                                                           ║${NC}"
    echo -e "${RED}${BOLD}║                      ✗ Installation Failed                                ║${NC}"
    echo -e "${RED}${BOLD}║                                                                           ║${NC}"
    echo -e "${RED}${BOLD}╚═══════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}${BOLD}Troubleshooting Information:${NC}"
    echo -e "${DIM}───────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "  ${WHITE}Log file:${NC}        ${CYAN}$LOG_FILE${NC}"
    echo -e "  ${WHITE}OS:${NC}              ${BOLD}$OS_TYPE${NC}"
    echo -e "  ${WHITE}Architecture:${NC}    ${BOLD}$ARCH_TYPE${NC}"
    echo ""
    
    echo -e "${YELLOW}${BOLD}Common Issues & Solutions:${NC}"
    echo -e "${DIM}───────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "  ${RED}1.${NC} ${WHITE}Python 3 not found${NC}"
    echo -e "     ${DIM}→${NC} Check: ${CYAN}python3 --version${NC}"
    echo -e "     ${DIM}→${NC} Install: ${CYAN}sudo apt install python3${NC} (Ubuntu/Debian)"
    echo ""
    echo -e "  ${RED}2.${NC} ${WHITE}Permission denied${NC}"
    echo -e "     ${DIM}→${NC} Try installing to user directory (default)"
    echo -e "     ${DIM}→${NC} Or use: ${CYAN}sudo ./install.sh${NC} (not recommended)"
    echo ""
    echo -e "  ${RED}3.${NC} ${WHITE}Network connection issues${NC}"
    echo -e "     ${DIM}→${NC} Check internet: ${CYAN}ping github.com${NC}"
    echo -e "     ${DIM}→${NC} Try again in a few moments"
    echo ""
    echo -e "  ${RED}4.${NC} ${WHITE}Previous installation exists${NC}"
    echo -e "     ${DIM}→${NC} Use force install: ${CYAN}--force${NC} flag"
    echo -e "     ${DIM}→${NC} Or uninstall first: ${CYAN}rift uninstall${NC}"
    echo ""
    
    echo -e "${CYAN}${BOLD}Need Help?${NC}"
    echo -e "${DIM}───────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "  ${WHITE}Documentation:${NC}   ${CYAN}https://rift.astroyds.com/docs/installation${NC}"
    echo -e "  ${WHITE}GitHub Issues:${NC}   ${CYAN}https://github.com/FoundationINCCorporateTeam/RIFT/issues${NC}"
    echo -e "  ${WHITE}Discord:${NC}         ${CYAN}https://discord.gg/rift${NC} ${DIM}(coming soon)${NC}"
    echo ""
    
    exit $exit_code
}

################################################################################
# Main Installation Process
################################################################################

main() {
    # Parse command-line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                print_usage
                exit 0
                ;;
            --version)
                echo -e "${BOLD}RIFT Installer v${INSTALLER_VERSION}${NC}"
                echo -e "${DIM}RIFT Language Version: ${RIFT_VERSION}${NC}"
                exit 0
                ;;
            --verbose|-v)
                VERBOSE=true
                shift
                ;;
            --force|-f)
                FORCE_INSTALL=true
                shift
                ;;
            --no-deps)
                INSTALL_DEPS=false
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --install-dir)
                INSTALL_DIR="$2"
                shift 2
                ;;
            --bin-dir)
                BIN_DIR="$2"
                shift 2
                ;;
            *)
                log ERROR "Unknown option: $1"
                echo ""
                print_usage
                exit 1
                ;;
        esac
    done
    
    # Set up error handling
    trap cleanup_on_error ERR
    
    # Start installation
    print_header
    
    if [ "$DRY_RUN" = true ]; then
        log WARNING "DRY RUN MODE - No changes will be made"
        echo ""
    fi
    
    log INFO "Initializing RIFT installation..."
    log DEBUG "Operating System: $OS_TYPE"
    log DEBUG "Architecture: $ARCH_TYPE"
    log DEBUG "Install Directory: $INSTALL_DIR"
    log DEBUG "Binary Directory: $BIN_DIR"
    log DEBUG "Force Install: $FORCE_INSTALL"
    log DEBUG "Install Dependencies: $INSTALL_DEPS"
    echo ""
    
    # Pre-installation checks
    echo -e "${CYAN}${BOLD}Pre-Installation Checks${NC}"
    echo -e "${DIM}───────────────────────────────────────────────────────────────────────────${NC}"
    
    # Installation steps with progress tracking
    local total_steps=8
    local current_step=0
    
    # Step 1: Check Python
    current_step=$((current_step + 1))
    print_progress $current_step $total_steps "Checking Python installation"
    if ! check_python; then
        echo ""
        install_python_hint
        cleanup_on_error
    fi
    
    # Step 2: Check Dependencies
    current_step=$((current_step + 1))
    print_progress $current_step $total_steps "Verifying system dependencies"
    check_dependencies || cleanup_on_error
    
    # Step 3: Create Directories
    current_step=$((current_step + 1))
    print_progress $current_step $total_steps "Creating installation directories"
    if [ "$DRY_RUN" = false ]; then
        create_directories || cleanup_on_error
    else
        log INFO "Would create: $INSTALL_DIR and $BIN_DIR"
    fi
    
    # Step 4: Download RIFT
    current_step=$((current_step + 1))
    print_progress $current_step $total_steps "Downloading RIFT from GitHub"
    if [ "$DRY_RUN" = false ]; then
        download_rift || cleanup_on_error
    else
        log INFO "Would download from: $RIFT_TAR_URL"
    fi
    
    # Step 5: Create CLI Wrapper
    current_step=$((current_step + 1))
    print_progress $current_step $total_steps "Installing CLI commands"
    if [ "$DRY_RUN" = false ]; then
        create_cli_wrapper || cleanup_on_error
    else
        log INFO "Would create: rift and riftserver commands"
    fi
    
    # Step 6: Install Dependencies
    current_step=$((current_step + 1))
    print_progress $current_step $total_steps "Installing Python dependencies"
    if [ "$DRY_RUN" = false ]; then
        install_python_dependencies
    else
        log INFO "Would install Python packages from requirements.txt"
    fi
    
    # Step 7: Configure Environment
    current_step=$((current_step + 1))
    print_progress $current_step $total_steps "Configuring shell environment"
    if [ "$DRY_RUN" = false ]; then
        configure_environment || cleanup_on_error
    else
        log INFO "Would update shell configuration files"
    fi
    
    # Step 8: Verify Installation
    current_step=$((current_step + 1))
    print_progress $current_step $total_steps "Verifying installation integrity"
    if [ "$DRY_RUN" = false ]; then
        if ! verify_installation; then
            cleanup_on_error
        fi
    else
        log INFO "Would verify installation completeness"
    fi
    
    echo ""
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}${BOLD}Dry run completed - no changes were made${NC}"
        echo -e "${DIM}Run without --dry-run to perform actual installation${NC}"
        exit 0
    fi
    
    # Success!
    print_completion_message
    
    log INFO "Installation completed successfully at $(date)"
}

# Handle interrupts gracefully
trap 'echo ""; log ERROR "Installation interrupted"; exit 1' INT TERM

# Run main installation
main "$@"
