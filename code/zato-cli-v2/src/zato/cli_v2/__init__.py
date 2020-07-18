# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################

def main():

    import sys

    # Anything else than --version is handled by Click
    if '--version' not in sys.argv:
        handle_click()

    # To show --version, we can just output it directly, without Click.
    else:

        # Zato
        from zato.cli_v2.zato_version import get_version

        # Needed no matter if are --verbose or not
        zato_version = get_version()['version']

        # This is --version --verbose with all the details
        if '--verbose' in sys.argv:
            handle_version_verbose(zato_version)
        else:
            handle_version_only(zato_version)

# ################################################################################################################################

def handle_click():
    pass

# ################################################################################################################################

def handle_version_only(zato_version):
    # type: (str)

    # stdlib
    from os import _exit
    from sys import stdout

    stdout.write('%s\n' % (zato_version),)
    _exit(0)

# ################################################################################################################################

def handle_version_verbose(zato_version):
    # type: (str)

    # stdlib
    from os import _exit
    from os.path import abspath, dirname, join as path_join
    from sys import executable, stdout, version as sys_version

    # Distro
    from distro import LinuxDistribution

    # sh
    import sh

    # Texttable
    from texttable import Texttable

    # ############################################################################################################################

    # Needed to find out how wide the 'Value' column should be, the default one usually suffices but not with long lines
    value_length = 60

    # This is where the 'zato' command comes from
    bin_dir = dirname(executable) # type: str

    # Build a zato_version full with its installation path
    zato_version = ['* %s' % zato_version]
    zato_version.append('* %s' % abspath(path_join(bin_dir, '..', '..')))
    zato_version.append('* %s' % path_join(bin_dir, 'zato'))
    zato_version = '\n'.join(zato_version)

    # Get a distribution object describing the current system ..
    distro = LinuxDistribution()

    # .. build a system version object.
    system_version = '* %s %s' % (distro._os_release_info['name'], distro._os_release_info['version'])

    # Get path to source code to be able to check the latest commit and any local changes.
    git_dir = abspath(path_join(bin_dir, '..', '..'))

    # Details of the Python version used
    python_details = []
    python_details.append('* %s ' % sys_version.replace('\n', ''))
    python_details.append('* %s ' % executable)
    python_details = '\n'.join(python_details)

    # A common pattern for git output details
    git_pretty = """--pretty=* %H%n* %aN <%aE>%n* %s  %n* %ad %n* %ar"""

    with sh.pushd(git_dir):

        # Details of the last commit
        last_commit = sh.git('log', '-1', git_pretty, '--date=iso', _tty_out=False).strip() # type: str
        value_length = max(value_length, max(len(elem) for elem in last_commit.splitlines()))

        # A list of local updates that have no been committed locally
        local_updates = sh.git('status', '--porcelain').rstrip() or '---'
        value_length = max(value_length, max(len(elem) for elem in local_updates.splitlines()))

        #
        # Local commits that have not been pushed are found by comparing two lists:
        #
        # * Commits between the initial installation commit and installation remote
        # * Commits between the initial installation commit and HEAD
        #
        # If something is in the second list but is not in the first one,
        # it means that it was added locally because otherwise it would have been in remote already.
        #

        release_dir = abspath(path_join(git_dir, 'code', 'release-info'))

        local_branch = sh.git('name-rev', '--name-only', 'HEAD').strip() # type: str

        initial_commit = open(path_join(release_dir, 'revision.txt')).read().strip()    # type: str
        initial_remote = open(path_join(release_dir, 'initial-remote.txt')).read().strip() # type: str

        between_initial_and_remote = sh.git(
            'rev-list', '--ancestry-path', '{}..{}'.format(initial_commit, initial_remote)).strip().splitlines()

        # Convert it to a set to make lookups faster
        between_initial_and_remote = set(between_initial_and_remote)

        between_initial_and_head = sh.git(
            'rev-list', '--ancestry-path', '{}..HEAD'.format(initial_commit)).strip().splitlines() # type: list

        # A list of local commits, sorted from newest to oldest
        local_commits   = []
        local_commit_id = []

        for commit_id in between_initial_and_head: # type: str
            if commit_id not in between_initial_and_remote:
                local_commit_id.append(commit_id)

        for commit_id in local_commit_id: # type: str
            commit_data = sh.git('show', git_pretty, commit_id, '--no-patch', '--no-color', _tty_out=False).strip()
            local_commits.append(commit_data)

        local_commits = local_commits or '---'

        for local_commit in local_commits:
            value_length = max(value_length, max(len(elem) for elem in local_commit.splitlines()))

        local_commits = '\n\n'.join(local_commits)

    # Key/value
    len_columns = 2

    table = Texttable()
    table.set_cols_width([20, value_length])
    table.set_cols_dtype(['t'] * len_columns)
    table.set_cols_align(['c', 't'])
    table.set_cols_valign(['m'] * len_columns)

    # Headers
    rows = [['Key', 'Value']]

    # Data rows
    rows += [
        ['Zato',   zato_version],
        ['System', system_version],
        ['Python', python_details],

        ['Git branch', '* %s' % local_branch],
        ['Git remote', '* %s' % 'ZZZ'],
        ['Git initial remote',         '* %s' % initial_remote],
        ['Git initial commit', '* %s' % initial_commit],

        ['Git last commit',   last_commit],
        ['Git local updates', local_updates],
        ['Git local commits', local_commits],
    ]

    # Add all rows to the table ..
    table.add_rows(rows)

    # .. and print it out.
    stdout.write(table.draw() + '\n')
    stdout.flush()

    _exit(0)

# ################################################################################################################################
