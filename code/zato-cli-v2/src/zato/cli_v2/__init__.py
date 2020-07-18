# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

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
    from sys import executable, stdout

    # Distro
    from distro import LinuxDistribution

    # sh
    import sh

    # Texttable
    from texttable import Texttable

    # Get a distribution object describing the current system ..
    distro = LinuxDistribution()

    # .. build a system version object.
    system_version = '%s %s' % (distro._os_release_info['name'], distro._os_release_info['version'])

    # Get path to source code to be able to check the latest commit and any local changes.
    bin_dir = dirname(executable)
    git_dir = abspath(path_join(bin_dir, '..', '..'))

    with sh.pushd(git_dir):

        # Details of the last commit
        last_commit = sh.git('log', '-1', '--pretty=* %H%n* %ad%n* %s', '--date=iso', _tty_out=False).strip()

        # A list of local updates that have no been committed locally
        local_updates = sh.git('status', '--porcelain').rstrip() or '---'

        # A list of local commits that have not been pushed
        local_commits = sh.git('cherry', '-v').rstrip() or '---'

    # Key/value
    len_columns = 2

    table = Texttable()
    table.set_cols_width([17, 60])
    table.set_cols_dtype(['t'] * len_columns)
    table.set_cols_align(['t'] * len_columns)
    table.set_cols_valign(['m'] * len_columns)

    # Headers
    rows = [['Key', 'Value']]

    # Data rows
    rows += [
        ['Zato version',      zato_version],
        ['System version',    system_version],
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
        zato_version = get_version()

        # This is --version --verbose with all the details
        if '--verbose' in sys.argv:
            handle_version_verbose(zato_version)
        else:
            handle_version_only(zato_version)

# ################################################################################################################################
