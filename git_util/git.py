#!/usr/bin/env python3
#
# This script fetch all git repo and checkout to master (expected login by ssh)
#
# Expected soft: git

import os
import sys
import getopt
import subprocess
from shlex import split
from termcolor import colored


class Options:
    def __init__(self, path=None):
        self.path = path
        self.offline = False
        self.branch = {}
        self.ignore = set()
        self.branch_default = 'master'

    def get_path(self):
        return self.path

    def set_path(self, arg):
        self.path = arg

    def is_ignore(self, arg):
        return arg in self.ignore

    def add_ignore(self, arg):
        self.ignore.add(arg)

    def is_offline(self):
        return self.offline

    def set_offline(self, arg):
        self.offline = arg

    def set_branch_default(self, arg):
        self.branch_default = arg

    def set_branch(self, service_name, branch):
        self.branch[service_name] = branch

    def get_branch(self, service_name):
        return self.branch[service_name] if service_name in self.branch else self.branch_default


class GitError(Exception):
    pass


def process_all(options):
    path = options.get_path()
    filenames = next(os.walk(path), (None, None, []))
    directories = filenames[1]
    directories.sort()
    for directory in directories:
        try:
            branch_name_new = options.get_branch(directory)
            service = {'path': path + '/' + directory, 'name': directory, 'branch_name_new': branch_name_new}
            print_service_name(service)
            if options.is_ignore(directory):
                print(' skipped')
            else:
                print(' in progress')
                process(options, service)
        except GitError:
            pass


def process(options, service):
    path = service['path'] if 'path' in service else "../../{0}".format(service['name'])
    branch_name_old = get_current_branch_name(path)
    is_branch_modified = is_current_branch_modified(service, path, branch_name_old)
    if is_branch_modified:
        return

    branch_new = service['branch_name_new']
    checkout(service, path, branch_new)
    if options.is_offline():
        print_status(service, 'checkout: ' + branch_new + '. ', get_old_branch_msg(branch_name_old, branch_new))
    else:
        pull(service, path, branch_name_old)
        print_status(service, 'checkout+pull: ' + branch_new + '. ', get_old_branch_msg(branch_name_old, branch_new))


def get_current_branch_name(path):
    output = subprocess.check_output(split("git branch"), cwd=path, universal_newlines=True)
    branch = [a for a in output.split('\n') if a.find('*') == 0][0]
    return branch[2:]


def is_current_branch_modified(service, path, branch_name_old):
    output = subprocess.check_output(split("git status -s"), cwd=path, universal_newlines=True)
    if len(output):
        print_status(service, '.', get_old_branch_msg(branch_name_old, service['branch_name_new']))
        print(output)
        return True
    return False


def get_old_branch_msg(branch_name_old, branch_name_new):
    return '' if branch_name_old == branch_name_new else 'Old branch: ' + branch_name_old


def print_service_name(service):
    print(colored(service['name'], 'white', 'on_grey', ['dark', 'bold']), end=' ')


def remove_previous_console_line():
    print('\033[A      \033[A')


def print_status(service, operation, suffix='', is_operation_success=True):
    operation_color = 'green' if is_operation_success else 'red'
    remove_previous_console_line()
    print_service_name(service)
    print(colored(operation, operation_color) + suffix)


def checkout(service, path, branch='master'):
    oc_result = subprocess.run(split("git checkout " + branch), capture_output=True, cwd=path)
    if oc_result.returncode != 0:
        print_status(service, 'checkout stopped.', is_operation_success=False)
        print(oc_result.stderr.decode('utf-8', 'strict'))
        raise GitError('checkout: return code is ' + str(oc_result.returncode))


def pull(service, path, branch_name_old):
    oc_result = subprocess.run(split("git pull"), capture_output=True, cwd=path)
    if oc_result.returncode != 0:
        old_branch_msg = get_old_branch_msg(branch_name_old, service['branch_name_new'])
        print_status(service, 'pull stopped', '. ' + old_branch_msg, is_operation_success=False)
        print(oc_result.stderr.decode('utf-8', 'strict'))
        raise GitError('pull: return code is ' + str(oc_result.returncode))


def load_options():
    result = Options()
    arguments = sys.argv[1:]
    opts, args = getopt.getopt(arguments, "op:i:b:", ["path=", "offline", "ignore=", "branch=", "branch_default"])
    for opt, arg in opts:
        if opt in ("-p", "--path"):
            result.set_path(arg)
        elif opt in ("-i", "--ignore"):
            result.add_ignore(arg)
        elif opt in ("-o", "--offline"):
            result.set_offline(True)
        elif opt in ("-b", "--branch"):
            result.set_branch(*arg.split('='))
        elif opt == "--branch_default":
            result.set_branch_default(arg)
    if result.get_path() is None:
        raise 'argument "path" is required'
    return result


if __name__ == "__main__":
    try:
        if sys.platform == "win32":
            os.system('color')
        loaded_options = load_options()
        process_all(loaded_options)
    except getopt.GetoptError as e:
        print('git.py -i <ignore_dirs_csv> -p <path_to_parent_directory_with_repos> [--offline]')
        print(e)
