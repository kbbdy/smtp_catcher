#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function
import os
import sys


COMMANDS = {
    'start':  ('python', ['/app/smtp_catcher/start.py']),
    'shell':   '/bin/sh',
}


def default_action():
    """
    Executed when no arguments are passed or argument is not recognized
    """
    print("Available commands:")
    for c in COMMANDS.keys():
        print(">", c)


def prepare_command(command):
    if command not in COMMANDS:
        print("Unknown command:", command)
        return None, None
    cmd = COMMANDS[command]
    if type(cmd) == str:
        return cmd, []
    return cmd[0], cmd[1]


def main():
    sys_args = sys.argv
    if sys_args[0] == 'python':
        sys_args = sys_args[1:]
    if sys_args[0] == __file__:
        sys_args = sys_args[1:]

    if len(sys_args) == 0:
        default_action()
        return
    else:
        command, args = prepare_command(sys_args[0])
        if command is None:
            default_action()
            return

    args += sys_args[1:]
    print("Executing:\n>", command, ' '.join(args))
    os.execvp(command, [command] + args)


if __name__ == '__main__':
    main()
