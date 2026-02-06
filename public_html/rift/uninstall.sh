#!/bin/bash
################################################################################
# RIFT Programming Language - Enterprise Uninstaller
# Version: 2.0.0
# Website: https://rift.astroyds.com
# Repository: https://github.com/FoundationINCCorporateTeam/RIFT
# 
# Usage:
#   curl -sSL https://rift.astroyds.com/rift/uninstall.sh | bash
#   curl -sSL https://rift.astroyds.com/rift/uninstall.sh | bash -s -- --force
#   or: rift uninstall
#
# Features:
#   - Interactive confirmation (skippable with --force)
#   - Automatic backup creation before uninstall
#   - Comprehensive cleanup of all RIFT components
#   - Detailed logging and reporting
#   - Graceful error handling
#   - Shell configuration cleanup
################################################################################

set -eo pipefail

# Colors and formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'
BOLD='\033[1m'
DIM='\033[2m'
UNDERLINE='\033[4m'

# Configuration
UNINSTALL_VERSION="2.0.0"
INSTALL_DIR="${RIFT_HOME:-$HOME/.rift}"
BIN_DIR="${RIFT_BIN_DIR:-$HOME/.local/bin}"
BACKUP_DIR="${HOME}/.rift_backup_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="/tmp/rift_uninstall_$(date +%Y%m%d_%H%M%S).log"
FORCE_UNINSTALL=false
CREATE_BACKUP=true
VERBOSE=false

# Statistics
FILES_REMOVED=0
SPACE_FREED=0

################################################################################
# Utility Functions
################################################################################

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Log to file
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    
    # Display to console
    case $level in
        INFO)
            echo -e "${BLUE}${BOLD}[ℹ]${NC} $message"
            ;;
        SUCCESS)
            echo -e "${GREEN}${BOLD}[✓]${NC} ${GREEN}$message${NC}"
            ;;
        WARNING)
            echo -e "${YELLOW}${BOLD}[⚠]${NC} ${YELLOW}$message${NC}"
            ;;
        ERROR)
            echo -e "${RED}${BOLD}[✗]${NC} ${RED}$message${NC}" >&2
            ;;
        STEP)
            echo -e "${MAGENTA}${BOLD}[→]${NC} ${BOLD}$message${NC}"
            ;;
        DEBUG)
            if [ "$VERBOSE" = true ]; then
                echo -e "${DIM}${CYAN}[DEBUG]${NC} ${DIM}$message${NC}"
            fi
            ;;
    esac
}

print_header() {
    clear 2>/dev/null || true
    echo -e "${RED}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                                                              ║"
    echo "║   ${WHITE}██████╗ ██╗███████╗████████╗${RED}    Uninstaller v${UNINSTALL_VERSION}                            ║"
    echo "║   ${WHITE}██╔══██╗██║██╔════╝╚══██╔══╝${RED}    Rapid Integrated Framework Technology                        ║"
    echo "║   ${WHITE}██████╔╝██║█████╗     ██║${RED}       https://rift.astroyds.com                                    ║"
    echo "║   ${WHITE}██╔══██╗██║██╔══╝     ██║${RED}                                                                    ║"
    echo "║   ${WHITE}██║  ██║██║██║        ██║${RED}       Enterprise-Grade Removal Tool                                ║"
    echo "║   ${WHITE}╚═╝  ╚═╝╚═╝╚═╝        ╚═╝${RED}                                                                    ║"
    echo "║                                                                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo -e "${DIM}Safe, thorough, and reversible uninstallation${NC}"
    echo ""
}

print_progress_bar() {
    local current=$1
    local total=$2
    local width=50
    local percentage=$((current * 100 / total))
    local filled=$((width * current / total))
    local empty=$((width - filled))
    
    printf "\r${CYAN}["
    printf "%${filled}s" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '░'
    printf "] ${BOLD}%3d%%${NC}" "$percentage"
    
    if [ $current -eq $total ]; then
        echo ""
    fi
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

confirm_uninstall() {
    if [ "$FORCE_UNINSTALL" = true ]; then
        log INFO "Force mode enabled - skipping confirmation"
        return 0
    fi
    
    echo -e "${YELLOW}${BOLD}⚠  Warning: This will remove RIFT from your system${NC}"
    echo ""
    echo -e "${WHITE}Removal Plan:${NC}"
    echo -e "  ${CYAN}├─${NC} Installation directory: ${BOLD}$INSTALL_DIR${NC}"
    echo -e "  ${CYAN}├─${NC} CLI commands: ${BOLD}rift, riftserver${NC}"
    echo -e "  ${CYAN}├─${NC} Shell configurations: ${BOLD}~/.bashrc, ~/.zshrc${NC}"
    echo -e "  ${CYAN}└─${NC} Environment variables: ${BOLD}RIFT_HOME, PATH${NC}"
    echo ""
    
    # Calculate size
    local size=$(get_directory_size "$INSTALL_DIR")
    local formatted_size=$(format_bytes $size)
    echo -e "${WHITE}Disk space to be freed:${NC} ${GREEN}${formatted_size}${NC}"
    echo ""
    
    # Fix for stdin issue when piped through curl
    # Reopen stdin from the terminal
    if [ ! -t 0 ]; then
        log DEBUG "Stdin not a terminal, attempting to reopen from /dev/tty"
        exec < /dev/tty
    fi
    
    echo -e "${YELLOW}${BOLD}Do you want to continue?${NC} (yes/no): "
    read -r response
    
    case "$response" in
        yes|YES|y|Y)
            log INFO "User confirmed uninstallation"
            return 0
            ;;
        *)
            echo ""
            log WARNING "Uninstallation cancelled by user"
            echo -e "${CYAN}No changes were made to your system.${NC}"
            echo -e "${DIM}To force uninstall without confirmation, use: --force${NC}"
            exit 0
            ;;
    esac
}

create_backup() {
    if [ "$CREATE_BACKUP" = false ]; then
        log INFO "Backup disabled, skipping..."
        return 0
    fi
    
    log STEP "Creating safety backup before removal..."
    
    if [ ! -d "$INSTALL_DIR" ]; then
        log WARNING "Installation directory not found, skipping backup"
        return 0
    fi
    
    mkdir -p "$BACKUP_DIR" 2>/dev/null || {
        log WARNING "Could not create backup directory, continuing without backup"
        return 0
    }
    
    # Backup installation directory
    if [ -d "$INSTALL_DIR" ]; then
        log DEBUG "Backing up $INSTALL_DIR to $BACKUP_DIR"
        cp -r "$INSTALL_DIR" "$BACKUP_DIR/rift" 2>/dev/null || {
            log WARNING "Could not backup installation directory"
        }
    fi
    
    # Backup CLI scripts
    if [ -f "$BIN_DIR/rift" ]; then
        cp "$BIN_DIR/rift" "$BACKUP_DIR/rift_command" 2>/dev/null || true
    fi
    if [ -f "$BIN_DIR/riftserver" ]; then
        cp "$BIN_DIR/riftserver" "$BACKUP_DIR/riftserver_command" 2>/dev/null || true
    fi
    
    # Create restoration script
    cat > "$BACKUP_DIR/RESTORE.sh" << 'EOFBACKUP'
#!/bin/bash
# RIFT Restoration Script
# This script will restore your RIFT installation from this backup

set -e

echo "Restoring RIFT from backup..."

BACKUP_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="${RIFT_HOME:-$HOME/.rift}"
BIN_DIR="${RIFT_BIN_DIR:-$HOME/.local/bin}"

if [ -d "$BACKUP_DIR/rift" ]; then
    echo "Restoring installation directory..."
    rm -rf "$INSTALL_DIR"
    cp -r "$BACKUP_DIR/rift" "$INSTALL_DIR"
    echo "✓ Restored $INSTALL_DIR"
fi

if [ -f "$BACKUP_DIR/rift_command" ]; then
    echo "Restoring rift command..."
    mkdir -p "$BIN_DIR"
    cp "$BACKUP_DIR/rift_command" "$BIN_DIR/rift"
    chmod +x "$BIN_DIR/rift"
    echo "✓ Restored rift command"
fi

if [ -f "$BACKUP_DIR/riftserver_command" ]; then
    echo "Restoring riftserver command..."
    cp "$BACKUP_DIR/riftserver_command" "$BIN_DIR/riftserver"
    chmod +x "$BIN_DIR/riftserver"
    echo "✓ Restored riftserver command"
fi

echo ""
echo "RIFT has been restored from backup!"
echo "You may need to restart your shell for changes to take effect."
EOFBACKUP
    
    chmod +x "$BACKUP_DIR/RESTORE.sh"
    
    local backup_size=$(get_directory_size "$BACKUP_DIR")
    log SUCCESS "Backup created: $BACKUP_DIR ($(format_bytes $backup_size))"
}

remove_files() {
    log STEP "Removing RIFT installation files..."
    echo ""
    
    local total_steps=4
    local current_step=0
    local errors=0
    
    # Remove installation directory
    current_step=$((current_step + 1))
    print_progress_bar $current_step $total_steps
    if [ -d "$INSTALL_DIR" ]; then
        local dir_size=$(get_directory_size "$INSTALL_DIR")
        log DEBUG "Removing directory: $INSTALL_DIR ($(format_bytes $dir_size))"
        
        if rm -rf "$INSTALL_DIR" 2>/dev/null; then
            SPACE_FREED=$((SPACE_FREED + dir_size))
            FILES_REMOVED=$((FILES_REMOVED + 1))
            log SUCCESS "Removed installation directory: $INSTALL_DIR"
        else
            log ERROR "Failed to remove: $INSTALL_DIR"
            errors=$((errors + 1))
        fi
    else
        log WARNING "Installation directory not found: $INSTALL_DIR"
    fi
    
    # Remove rift command
    current_step=$((current_step + 1))
    print_progress_bar $current_step $total_steps
    if [ -f "$BIN_DIR/rift" ]; then
        if rm -f "$BIN_DIR/rift" 2>/dev/null; then
            FILES_REMOVED=$((FILES_REMOVED + 1))
            log SUCCESS "Removed command: rift"
        else
            log ERROR "Failed to remove: $BIN_DIR/rift"
            errors=$((errors + 1))
        fi
    else
        log INFO "Command not found: rift (already removed)"
    fi
    
    # Remove riftserver command
    current_step=$((current_step + 1))
    print_progress_bar $current_step $total_steps
    if [ -f "$BIN_DIR/riftserver" ]; then
        if rm -f "$BIN_DIR/riftserver" 2>/dev/null; then
            FILES_REMOVED=$((FILES_REMOVED + 1))
            log SUCCESS "Removed command: riftserver"
        else
            log ERROR "Failed to remove: $BIN_DIR/riftserver"
            errors=$((errors + 1))
        fi
    else
        log INFO "Command not found: riftserver (already removed)"
    fi
    
    # Clean up empty bin directory if it's empty
    current_step=$((current_step + 1))
    print_progress_bar $current_step $total_steps
    if [ -d "$BIN_DIR" ] && [ -z "$(ls -A "$BIN_DIR" 2>/dev/null)" ]; then
        log DEBUG "Removing empty bin directory: $BIN_DIR"
        rmdir "$BIN_DIR" 2>/dev/null || true
    fi
    
    echo ""
    
    if [ $errors -gt 0 ]; then
        log WARNING "Completed with $errors error(s)"
        return 1
    fi
    
    return 0
}

clean_environment() {
    log STEP "Cleaning shell configuration files..."
    echo ""
    
    local shell_configs=(
        "$HOME/.bashrc"
        "$HOME/.bash_profile"
        "$HOME/.profile"
        "$HOME/.zshrc"
        "$HOME/.zprofile"
        "$HOME/.config/fish/config.fish"
    )
    
    local cleaned=0
    local backed_up=0
    
    for config in "${shell_configs[@]}"; do
        if [ ! -f "$config" ]; then
            log DEBUG "Config file not found: $config"
            continue
        fi
        
        # Check if config contains RIFT entries
        if grep -q "RIFT Programming Language" "$config" 2>/dev/null || 
           grep -q "RIFT_HOME" "$config" 2>/dev/null || 
           grep -q ".rift" "$config" 2>/dev/null; then
            
            # Create backup before modification
            local backup_name="${config}.rift_backup_$(date +%Y%m%d_%H%M%S)"
            if cp "$config" "$backup_name" 2>/dev/null; then
                log DEBUG "Created backup: $backup_name"
                backed_up=$((backed_up + 1))
            else
                log WARNING "Could not backup $config, skipping cleanup"
                continue
            fi
            
            # Remove RIFT entries (more comprehensive pattern)
            if sed -i.bak \
                -e '/# RIFT Programming Language/,+3d' \
                -e '/export RIFT_HOME/d' \
                -e '/export.*\.rift/d' \
                -e '/PATH=.*\.rift/d' \
                -e '/PATH=.*\.local\/bin.*rift/d' \
                "$config" 2>/dev/null; then
                
                # Remove the .bak file created by sed
                rm -f "${config}.bak" 2>/dev/null || true
                
                cleaned=$((cleaned + 1))
                log SUCCESS "Cleaned configuration: $(basename $config)"
            else
                log ERROR "Failed to clean: $config"
                # Restore from backup
                if [ -f "$backup_name" ]; then
                    cp "$backup_name" "$config" 2>/dev/null || true
                    log INFO "Restored from backup"
                fi
            fi
        else
            log DEBUG "No RIFT entries found in: $config"
        fi
    done
    
    echo ""
    
    if [ $cleaned -gt 0 ]; then
        log SUCCESS "Cleaned $cleaned configuration file(s)"
        log INFO "Backups created: $backed_up file(s)"
    else
        log INFO "No shell configuration changes needed"
    fi
}

verify_removal() {
    log STEP "Verifying complete removal..."
    
    local issues=0
    
    if [ -d "$INSTALL_DIR" ]; then
        log WARNING "Installation directory still exists: $INSTALL_DIR"
        issues=$((issues + 1))
    fi
    
    if [ -f "$BIN_DIR/rift" ]; then
        log WARNING "rift command still exists"
        issues=$((issues + 1))
    fi
    
    if [ -f "$BIN_DIR/riftserver" ]; then
        log WARNING "riftserver command still exists"
        issues=$((issues + 1))
    fi
    
    if [ $issues -eq 0 ]; then
        log SUCCESS "All RIFT components successfully removed"
        return 0
    else
        log WARNING "$issues component(s) may not have been removed completely"
        return 1
    fi
}

print_statistics() {
    echo ""
    echo -e "${CYAN}${BOLD}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}${BOLD}║                    Uninstall Statistics                       ║${NC}"
    echo -e "${CYAN}${BOLD}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${WHITE}Files removed:${NC}       ${GREEN}${FILES_REMOVED}${NC}"
    echo -e "  ${WHITE}Disk space freed:${NC}    ${GREEN}$(format_bytes $SPACE_FREED)${NC}"
    echo -e "  ${WHITE}Backup location:${NC}     ${CYAN}${BACKUP_DIR}${NC}"
    echo -e "  ${WHITE}Log file:${NC}            ${CYAN}${LOG_FILE}${NC}"
    echo ""
}

print_completion() {
    echo ""
    echo -e "${GREEN}${BOLD}╔═══════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}${BOLD}║                                                                           ║${NC}"
    echo -e "${GREEN}${BOLD}║                    ✓ Uninstallation Completed Successfully                ║${NC}"
    echo -e "${GREEN}${BOLD}║                                                                           ║${NC}"
    echo -e "${GREEN}${BOLD}╚═══════════════════════════════════════════════════════════════════════════╝${NC}"
    
    print_statistics
    
    echo -e "${CYAN}${BOLD}Next Steps:${NC}"
    echo ""
    echo -e "  ${WHITE}1.${NC} Restart your shell for all changes to take effect:"
    echo -e "     ${DIM}source ~/.bashrc${NC}  ${DIM}(or ~/.zshrc for zsh)${NC}"
    echo ""
    echo -e "  ${WHITE}2.${NC} To restore from backup (if needed):"
    echo -e "     ${CYAN}bash $BACKUP_DIR/RESTORE.sh${NC}"
    echo ""
    echo -e "  ${WHITE}3.${NC} To reinstall RIFT in the future:"
    echo -e "     ${CYAN}curl -sSL https://rift.astroyds.com/rift/install.sh | bash${NC}"
    echo ""
    echo -e "${DIM}Thank you for trying RIFT! We'd love to hear your feedback.${NC}"
    echo -e "${DIM}GitHub: https://github.com/FoundationINCCorporateTeam/RIFT${NC}"
    echo ""
}

print_usage() {
    echo -e "${BOLD}RIFT Uninstaller v${UNINSTALL_VERSION}${NC}"
    echo ""
    echo "Usage: ./uninstall.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo -e "  ${BOLD}--force, -f${NC}         Skip confirmation prompt"
    echo -e "  ${BOLD}--no-backup${NC}         Don't create backup before uninstalling"
    echo -e "  ${BOLD}--verbose, -v${NC}       Enable verbose output"
    echo -e "  ${BOLD}--help, -h${NC}          Show this help message"
    echo ""
    echo "Environment Variables:"
    echo -e "  ${BOLD}RIFT_HOME${NC}           RIFT installation directory (default: ~/.rift)"
    echo -e "  ${BOLD}RIFT_BIN_DIR${NC}        Binary directory (default: ~/.local/bin)"
    echo ""
    echo "Examples:"
    echo -e "  ${DIM}# Interactive uninstall with backup${NC}"
    echo "  curl -sSL https://rift.astroyds.com/rift/uninstall.sh | bash"
    echo ""
    echo -e "  ${DIM}# Force uninstall without confirmation${NC}"
    echo "  curl -sSL https://rift.astroyds.com/rift/uninstall.sh | bash -s -- --force"
    echo ""
    echo -e "  ${DIM}# Uninstall without creating backup${NC}"
    echo "  curl -sSL https://rift.astroyds.com/rift/uninstall.sh | bash -s -- --no-backup"
    echo ""
    echo -e "For more information, visit: ${CYAN}https://rift.astroyds.com${NC}"
}

handle_error() {
    local exit_code=$?
    echo ""
    log ERROR "Uninstallation failed with exit code: $exit_code"
    echo ""
    echo -e "${YELLOW}Partial uninstallation may have occurred.${NC}"
    echo -e "${CYAN}Log file saved to: ${BOLD}$LOG_FILE${NC}"
    echo ""
    
    if [ -d "$BACKUP_DIR" ]; then
        echo -e "${CYAN}A backup was created at: ${BOLD}$BACKUP_DIR${NC}"
        echo -e "${CYAN}You can restore using: ${BOLD}bash $BACKUP_DIR/RESTORE.sh${NC}"
        echo ""
    fi
    
    echo -e "For help, visit: ${CYAN}https://rift.astroyds.com/docs/troubleshooting${NC}"
    exit $exit_code
}

################################################################################
# Main Execution
################################################################################

main() {
    # Parse command-line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force|-f)
                FORCE_UNINSTALL=true
                shift
                ;;
            --no-backup)
                CREATE_BACKUP=false
                shift
                ;;
            --verbose|-v)
                VERBOSE=true
                shift
                ;;
            --help|-h)
                print_usage
                exit 0
                ;;
            *)
                log ERROR "Unknown option: $1"
                print_usage
                exit 1
                ;;
        esac
    done
    
    # Set up error handling
    trap handle_error ERR
    
    # Start uninstallation process
    print_header
    
    log INFO "Starting RIFT uninstallation process..."
    log DEBUG "Install directory: $INSTALL_DIR"
    log DEBUG "Bin directory: $BIN_DIR"
    log DEBUG "Backup directory: $BACKUP_DIR"
    log DEBUG "Log file: $LOG_FILE"
    echo ""
    
    # Confirm uninstallation
    confirm_uninstall
    echo ""
    
    # Create backup
    create_backup
    echo ""
    
    # Remove files
    remove_files
    echo ""
    
    # Clean environment
    clean_environment
    echo ""
    
    # Verify removal
    verify_removal
    
    # Print completion message
    print_completion
    
    log INFO "Uninstallation completed successfully"
}

# Run main function
main "$@"
