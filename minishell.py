import os
import platform
import subprocess
import shlex
import sys
import glob
from typing import List, Optional, Dict

# Detect OS
OS_TYPE = platform.system()
COMMAND_HISTORY: List[str] = []
HISTORY_FILE = os.path.expanduser("~/.minishell_history")
MAX_HISTORY = 100

# Color codes
COLORS = {
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'cyan': '\033[96m',
    'white': '\033[97m',
    'reset': '\033[0m',
    'bold': '\033[1m'
}

# Command translations (Unix -> Windows)
COMMAND_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'ls': {'Windows': 'dir', 'Linux': 'ls -F', 'Darwin': 'ls -G'},
    'clear': {'Windows': 'cls', 'Linux': 'clear', 'Darwin': 'clear'},
    'rm': {'Windows': 'del /Q', 'Linux': 'rm -f', 'Darwin': 'rm -f'},
    'cp': {'Windows': 'copy', 'Linux': 'cp', 'Darwin': 'cp'},
    'mv': {'Windows': 'move', 'Linux': 'mv', 'Darwin': 'mv'},
    'grep': {'Windows': 'findstr', 'Linux': 'grep', 'Darwin': 'grep'},
    'cat': {'Windows': 'type', 'Linux': 'cat', 'Darwin': 'cat'},
    'pwd': {'Windows': 'cd', 'Linux': 'pwd', 'Darwin': 'pwd'}
}

def color_text(text: str, color: str) -> str:
    """Colorize text with ANSI codes."""
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"

def load_history():
    """Load command history from file."""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                COMMAND_HISTORY.extend(line.strip() for line in f.readlines()[-MAX_HISTORY:])
    except Exception as e:
        print(color_text(f"[WARNING] Could not load history: {e}", "yellow"))

def save_history():
    """Save command history to file."""
    try:
        with open(HISTORY_FILE, 'w') as f:
            f.write("\n".join(COMMAND_HISTORY[-MAX_HISTORY:]))
    except Exception as e:
        print(color_text(f"[WARNING] Could not save history: {e}", "yellow"))

def translate_command(cmd: str) -> str:
    """Convert Unix-style commands to system-specific equivalents."""
    parts = shlex.split(cmd)
    if not parts:
        return cmd
    
    # Handle special cases first
    if parts[0] == 'ls' and '-l' in parts:
        return 'dir /Q' if OS_TYPE == "Windows" else cmd
    if parts[0] == 'ls' and '-R' in parts:
        return 'dir /S' if OS_TYPE == "Windows" else cmd
    
    # Standard translation
    if parts[0] in COMMAND_TRANSLATIONS:
        base_cmd = COMMAND_TRANSLATIONS[parts[0]].get(OS_TYPE, parts[0])
        return f"{base_cmd} {' '.join(parts[1:])}"
    return cmd

def expand_wildcards(cmd: str) -> str:
    """Expand wildcards (*, ?) in command arguments."""
    parts = []
    for part in shlex.split(cmd):
        if '*' in part or '?' in part:
            expanded = glob.glob(part)
            if expanded:
                parts.extend(expanded)
            else:
                parts.append(part)
        else:
            parts.append(part)
    return ' '.join(parts)

def run_command(cmd: str) -> bool:
    """Run a command with translation and wildcard support."""
    try:
        translated_cmd = translate_command(cmd)
        expanded_cmd = expand_wildcards(translated_cmd)
        
        if OS_TYPE == "Windows":
            subprocess.run(expanded_cmd, shell=True, check=True)
        else:
            subprocess.run(expanded_cmd, shell=True, executable='/bin/bash', check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(color_text(f"[ERROR] Command failed (Code {e.returncode})", "red"))
    except Exception as e:
        print(color_text(f"[ERROR] {e}", "red"))
    return False

def get_prompt() -> str:
    """Generate colored prompt with current directory."""
    cwd = os.getcwd()
    home = os.path.expanduser("~")
    if cwd.startswith(home):
        cwd = cwd.replace(home, "~", 1)
    prompt = color_text(cwd, "green") + color_text(" >>> ", "green")
    return prompt

def my_set(args: List[str]) -> None:
    """Set environment variable: my_set VAR=value"""
    if not args:
        print(color_text("[ERROR] Usage: my_set VAR=value", "red"))
        return
    
    for arg in args:
        if '=' in arg:
            var, value = arg.split('=', 1)
            os.environ[var] = value
            print(f"[INFO] Set {var}={value}")
        else:
            print(color_text(f"[ERROR] Invalid format: {arg}. Use VAR=value", "red"))

def my_get(var: str) -> None:
    """Get environment variable: my_get VAR"""
    if not var:
        print(color_text("[ERROR] Usage: my_get VAR", "red"))
        return
    
    value = os.environ.get(var)
    if value is not None:
        print(f"{var}={value}")
    else:
        print(color_text(f"[ERROR] Variable {var} not set", "red"))

def my_ls(path: Optional[str] = None) -> None:
    """List directory contents."""
    path = path or os.getcwd()
    run_command(f"ls -la {path}" if path else "ls -la")

def my_cd(path: str) -> None:
    """Change working directory."""
    try:
        if not path:
            path = os.environ.get('HOME', os.path.expanduser("~"))
        os.chdir(os.path.expanduser(path))
        print(color_text(f"[INFO] Changed directory to {os.getcwd()}", "blue"))
    except FileNotFoundError:
        print(color_text(f"[ERROR] Directory not found: {path}", "red"))
    except Exception as e:
        print(color_text(f"[ERROR] {e}", "red"))

def my_pwd() -> None:
    """Print current working directory."""
    print(color_text(f"[INFO] Current Directory: {os.getcwd()}", "blue"))

def my_mkdir(name: str) -> None:
    """Create a new directory."""
    try:
        os.makedirs(name, exist_ok=True)
        print(color_text(f"[INFO] Directory '{name}' created.", "blue"))
    except Exception as e:
        print(color_text(f"[ERROR] {e}", "red"))

def my_touch(filename: str) -> None:
    """Create an empty file or update timestamp."""
    try:
        with open(filename, 'a'):
            os.utime(filename, None)
        print(color_text(f"[INFO] File '{filename}' created or updated.", "blue"))
    except Exception as e:
        print(color_text(f"[ERROR] {e}", "red"))

def my_rm(name: str, recursive: bool = False) -> None:
    """Remove a file or directory."""
    try:
        if os.path.isdir(name):
            if recursive:
                run_command(f"rm -rf {name}")
            else:
                os.rmdir(name)
            print(color_text(f"[INFO] Directory '{name}' removed.", "blue"))
        elif os.path.isfile(name):
            os.remove(name)
            print(color_text(f"[INFO] File '{name}' removed.", "blue"))
        else:
            print(color_text("[ERROR] File or directory not found.", "red"))
    except Exception as e:
        print(color_text(f"[ERROR] {e}", "red"))

def my_echo(*args: str) -> None:
    """Print arguments to console."""
    print(' '.join(args))

def my_clear() -> None:
    """Clear the console screen."""
    run_command("clear")

def my_run(cmd: str) -> None:
    """Run any OS command with unified syntax."""
    if not cmd:
        print(color_text("[ERROR] Usage: my_run <command>", "red"))
        return
    run_command(cmd)

def show_help() -> None:
    """Display colored help menu."""
    help_text = f"""
{color_text("MiniShell Help (Unified Commands)", "bold")}

{color_text("Core Commands:", "bold")}
  {color_text("my_ls [path]", "green")}          - List directory
  {color_text("my_cd <dir>", "green")}           - Change directory
  {color_text("my_pwd", "green")}                - Show current directory
  {color_text("my_mkdir <name>", "green")}       - Create directory
  {color_text("my_touch <file>", "green")}       - Create file
  {color_text("my_rm <target>", "green")}        - Remove file/directory
  {color_text("my_rm -r <dir>", "green")}        - Recursive remove
  {color_text("my_echo <text>", "green")}        - Print text
  {color_text("my_clear", "green")}              - Clear screen

{color_text("Advanced:", "bold")}
  {color_text("my_run <command>", "green")}      - Run any command (unified syntax)
  {color_text("my_set VAR=value", "green")}      - Set environment variable
  {color_text("my_get VAR", "green")}            - Get environment variable

{color_text("System:", "bold")}
  {color_text("history", "green")}               - Command history
  {color_text("help", "green")}                  - Show this help
  {color_text("exit", "green")}                  - Exit shell

{color_text("Examples:", "bold")}
  {color_text("my_run ls -l *.py", "cyan")}      # Works on all OSes
  {color_text("my_run grep 'error' logs/*", "cyan")}
  {color_text("my_set TEMP=~/temp", "cyan")}
  {color_text("my_run cp $TEMP/*.txt .", "cyan")}
"""
    print(help_text)

def show_history() -> None:
    """Display command history."""
    if not COMMAND_HISTORY:
        print(color_text("[INFO] No history yet.", "blue"))
    else:
        for i, cmd in enumerate(COMMAND_HISTORY[-MAX_HISTORY:], 1):
            print(f"{i}: {cmd}")

def parse_input(user_input: str) -> tuple:
    """Parse user input into command and arguments."""
    try:
        tokens = shlex.split(user_input)
        return tokens[0], tokens[1:]
    except ValueError:
        return user_input.strip(), []

def shell_loop() -> None:
    """Main shell loop."""
    load_history()
    print(color_text(f"MiniShell v3.0 (Unified {OS_TYPE})", "bold"))
    print(color_text("Type 'help' for commands, 'exit' to quit", "blue"))

    while True:
        try:
            user_input = input(get_prompt()).strip()
            if not user_input:
                continue

            COMMAND_HISTORY.append(user_input)
            command, args = parse_input(user_input)

            if command == "exit":
                print(color_text("Goodbye!", "blue"))
                save_history()
                sys.exit(0)
            elif command == "my_ls":
                my_ls(args[0] if args else None)
            elif command == "my_cd":
                my_cd(args[0] if args else "")
            elif command == "my_pwd":
                my_pwd()
            elif command == "my_mkdir":
                if args:
                    my_mkdir(args[0])
                else:
                    print(color_text("[ERROR] Usage: my_mkdir <name>", "red"))
            elif command == "my_touch":
                if args:
                    my_touch(args[0])
                else:
                    print(color_text("[ERROR] Usage: my_touch <file>", "red"))
            elif command == "my_rm":
                if args:
                    if args[0] == "-r" and len(args) > 1:
                        my_rm(args[1], recursive=True)
                    else:
                        my_rm(args[0])
                else:
                    print(color_text("[ERROR] Usage: my_rm <target>", "red"))
            elif command == "my_echo":
                my_echo(*args)
            elif command == "my_clear":
                my_clear()
            elif command == "my_run":
                if args:
                    my_run(" ".join(args))
                else:
                    print(color_text("[ERROR] Usage: my_run <command>", "red"))
            elif command == "my_set":
                my_set(args)
            elif command == "my_get":
                if args:
                    my_get(args[0])
                else:
                    print(color_text("[ERROR] Usage: my_get <VAR>", "red"))
            elif command == "help":
                show_help()
            elif command == "history":
                show_history()
            else:
                print(color_text(f"[ERROR] Unknown command: {command}", "red"))
        except KeyboardInterrupt:
            print(color_text("\n[INFO] Use 'exit' to quit", "yellow"))
        except Exception as e:
            print(color_text(f"[ERROR] {e}", "red"))

if __name__ == "__main__":
    shell_loop()
