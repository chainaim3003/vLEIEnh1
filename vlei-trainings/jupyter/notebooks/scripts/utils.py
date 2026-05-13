import subprocess
import os
import platform
import shlex 

class Ansi:
    # Text Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright/Light versions
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    # Bright Background colors
    BG_BRIGHT_BLACK = '\033[100m'
    BG_BRIGHT_RED = '\033[101m'
    BG_BRIGHT_GREEN = '\033[102m'
    BG_BRIGHT_YELLOW = '\033[103m'
    BG_BRIGHT_BLUE = '\033[104m'
    BG_BRIGHT_MAGENTA = '\033[105m'
    BG_BRIGHT_CYAN = '\033[106m'
    BG_BRIGHT_WHITE = '\033[107m'
    # Styles
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m' 


def pr_title(message):
    print(f"\n{Ansi.BOLD}{Ansi.UNDERLINE}{Ansi.BG_BLUE}{Ansi.BRIGHT_BLACK}  {message}  {Ansi.RESET}\n")

def pr_message(message):
    print(f"\n{Ansi.BOLD}{Ansi.BRIGHT_BLUE}{message}{Ansi.RESET}\n")

def pr_continue():
    message = "  You can continue ✅  "
    print(f"\n{Ansi.BOLD}{Ansi.BG_GREEN}{Ansi.BRIGHT_BLACK}{message}{Ansi.RESET}\n\n")

def clear_keri(prompt_confirmation=False):

    os_name = platform.system()

    path = "/usr/local/var/keri/"
    match os_name:
        case "Linux":
            path = "/usr/local/var/keri/"
        case "Darwin":  # macOS
            user_path = os.path.expanduser("~")
            path = os.path.join(user_path, ".keri")
        case "Windows":
            user_path = os.path.expanduser("~")
            path = os.path.join(user_path, "keri")  # Adjust as needed for Windows
        case _:
            print(f"❌ Unsupported OS: {os_name}. Cannot clear keystore.")
            return
    # check 
    proceed_with_deletion = False

    if prompt_confirmation:
        confirm = input(f"🚨 This will clear your keystore at '{path}'. Are you sure? (y/n): ")
        if confirm.lower() == "y":
            print("Proceeding with deletion...")
            proceed_with_deletion = True
        else:
            print("Operation cancelled by user.")
    else:
        proceed_with_deletion = True
        print(f"Proceeding with deletion of '{path}' without confirmation.")

    if proceed_with_deletion:
        try:
            if not os.path.exists(path):
                print(f"⚠️ Path not found: {path}. Nothing to remove.")
                return
            subprocess.run(["rm", "-rf", path], check=True)
            print(f"✅ Successfully removed: {path}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error removing {path}: {e}")
        except FileNotFoundError: # Should not happen with rm -rf, but good for other commands
            print(f"❌ Path not found during removal attempt (should have been caught earlier): {path}")
        except Exception as e: # Catch any other potential errors
            print(f"❌ An unexpected error occurred: {e}")

def exec(command_string: str, return_all_lines: bool = False):
    ipython = get_ipython()
    if ipython is None:
        print("Warning: Not running in IPython/Jupyter.")
        return [] if return_all_lines else None

    # This is the equivalent of output_lines = !{command_string}
    output_lines = ipython.getoutput(command_string, split=True)

    if not output_lines:
        # Handle no output
        return [] if return_all_lines else None

    # Process output if it exists
    stripped_lines = [line.strip() for line in output_lines]

    if return_all_lines:
        return stripped_lines
    else:
        # We already checked output_lines is not empty
        return stripped_lines[0]

def exec_bg(command_string):
    """
    Runs a shell command in the background.

    Args:
        command_string (str): The shell command to execute.

    Returns:
        subprocess.Popen: The Popen object for the started process.
                          This can be used to check status, wait, or terminate.
    """
    try:
        process = subprocess.Popen(
            command_string,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"Command {command_string} started with PID: {process.pid}")
        return process
    except Exception as e:
        print(f"Error starting command '{command_string}': {e}")
        return None