import subprocess
import sys
import os
import shlex

PATH = os.environ.get("PATH")
COMMAND_BUILTINS = ['type echo', 'type exit', 'type type', 'type pwd']


def cd_command(command):
    directory = command.split(' ')[1]
    try:
        os.chdir(os.path.expanduser(directory))
    except OSError:
        print(f"cd: {directory}: No such file or directory")


def type_command(command, command_builtins):
    cmd_path = None
    paths = PATH.split(":")
    for path in paths:
        if os.path.isfile(f'{path}/{command[5:]}'):
            cmd_path = f'{path}/{command[5:]}'
    if command in command_builtins:
        sys.stdout.write(f'{command[5:]} is a shell builtin\n')
    elif cmd_path:
        sys.stdout.write(f"{command[5:]} is {cmd_path}\n")
    else:
        sys.stdout.write(f'{command[5:]}: not found\n')


def echo_command(command):


    # Split the command, preserving quotes
    parts = shlex.split(command)

    # Print all parts after 'echo', preserving spaces
    sys.stdout.write(f"{' '.join(parts[1:])}\n")


def run_external_command(command):


    # Split the command, preserving quotes
    parts = shlex.split(command)

    # Separate executable from arguments
    executable = parts[0]
    args = parts[1:]

    # Search for the executable in PATH
    executable_path = None
    for path in PATH.split(":"):
        potential_path = os.path.join(path, executable)
        if os.path.isfile(potential_path) and os.access(potential_path, os.X_OK):
            executable_path = potential_path
            break

    if executable_path:
        try:
            # Run the command and capture output
            result = subprocess.run([executable_path] + args,
                                    capture_output=True,
                                    text=True,
                                    check=True)
            sys.stdout.write(result.stdout)
            sys.stdout.flush()
        except subprocess.CalledProcessError as e:
            # If individual file reading fails, try to read files one by one
            output = ""
            for arg in args:
                try:
                    with open(arg, 'r') as f:
                        output += f.read().strip() + " "
                except Exception as file_error:
                    sys.stderr.write(f"Error reading file {arg}: {file_error}\n")

            if output:
                sys.stdout.write(output.rstrip() + "\n")
            else:
                sys.stderr.write(f"Error executing {executable}: {e.stderr}\n")
    else:
        print(f"{executable}: command not found")


def main():
    # Uncomment this block to pass the first stage

    while True:
        sys.stdout.write("$ ")
        # Wait for user input
        command = input()
        if command == 'exit 0':
            sys.exit(0)
        elif command.startswith('echo'):
            echo_command(command)
        elif command.startswith('type'):
            type_command(command, COMMAND_BUILTINS)
        elif command.startswith('pwd'):
            sys.stdout.write(f'{os.getcwd()}\n')
        elif command.startswith('cd'):
            cd_command(command)
        else:
            run_external_command(command)


if __name__ == "__main__":
    main()
