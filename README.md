# MiniShell - Cross-Platform Command Shell

## Overview

MiniShell is a lightweight, cross-platform command shell that provides a unified interface for both Windows and Linux/macOS systems. It translates common Unix commands to their Windows equivalents and offers a set of built-in commands with consistent behavior across platforms.

## Features

- **Cross-platform compatibility**: Works on Windows, Linux, and macOS
- **Command translation**: Automatically converts Unix commands to Windows equivalents
- **Built-in utilities**: Custom commands for common operations (`my_ls`, `my_cd`, etc.)
- **Wildcard expansion**: Supports `*` and `?` in file operations
- **Command history**: Persistent history across sessions
- **Colorized output**: Easy-to-read colored prompts and messages
- **Environment variable management**: Set and get environment variables
- **Unified syntax**: Run commands the same way regardless of OS

### Prerequisites

- Python 3.6 or higher
- On Linux/macOS: `/bin/bash` (for shell command execution)

# MiniShell - Supported Commands

## File System Operations
- `my_ls [path]` - List directory contents (default: current directory)
  Example: `my_ls ~/Documents` or `my_ls`

- `my_cd [directory]` - Change directory (default: home directory)
  Example: `my_cd ..` or `my_cd /path/to/folder`

- `my_pwd` - Print current working directory
  Example: `my_pwd`

- `my_mkdir <directory>` - Create new directory
  Example: `my_mkdir new_folder`

- `my_touch <filename>` - Create empty file or update timestamp
  Example: `my_touch file.txt`

- `my_rm <target>` - Remove file or empty directory
  Example: `my_rm old_file.txt`

- `my_rm -r <directory>` - Recursively remove directory and contents
  Example: `my_rm -r old_folder`

## System Operations
- `my_run <command>` - Execute any system command with cross-platform translation
  Example: `my_run ls -la *.py` or `my_run dir /Q`

- `my_clear` - Clear terminal screen
  Example: `my_clear`

- `history` - Show command history
  Example: `history`

## Environment Variables
- `my_set VAR=value` - Set environment variable
  Example: `my_set TEMP_DIR=/tmp`

- `my_get <VAR>` - Get environment variable value
  Example: `my_get PATH`

## Shell Control
- `help` - Show help menu with all commands
  Example: `help`

- `exit` - Exit the MiniShell
  Example: `exit`

## Special Features
- Wildcard support (*, ?) in all file operations
  Example: `my_run cp *.txt backup/`

- Command history (persistent across sessions)
- Colorized output and prompts
- Cross-platform command translation (Unix ↔ Windows)
