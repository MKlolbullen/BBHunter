# modules/execution.py

import subprocess

def execute_tool(tool_path, cmd_args, sudo=False, capture_output=False, stdout=None):
    """
    Executes an external tool with the provided command arguments.

    Parameters:
    - tool_path (str): Path to the tool executable.
    - cmd_args (list): List of command-line arguments.
    - sudo (bool): Whether to run the command with sudo.
    - capture_output (bool): Whether to capture the command's output.
    - stdout (file object): File object to write the output to.

    Returns:
    - str: Captured output if capture_output is True; otherwise, empty string.
    """
    command = []
    if sudo:
        command.append('sudo')
    command.append(tool_path)
    command.extend(cmd_args)

    try:
        if capture_output:
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.stdout
        elif stdout:
            with subprocess.Popen(command, stdout=stdout, stderr=subprocess.PIPE, text=True) as process:
                _, stderr = process.communicate()
                if process.returncode != 0:
                    print(f"Error executing {' '.join(command)}: {stderr}")
            return ""
        else:
            subprocess.run(command, check=True)
            return ""
    except subprocess.CalledProcessError as e:
        print(f"Error executing {' '.join(command)}: {e.stderr}")
        return ""
