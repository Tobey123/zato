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

    # Get a distribution object describing the current system ..
    distro = LinuxDistribution()

    # .. and print out basic distro information.
    stdout.write('%s %s\n' % (distro._os_release_info['name'], distro._os_release_info['version']),)

    # Get path to source code to be able to check the latest commit and any local changes.
    bin_dir = dirname(executable)
    git_dir = abspath(path_join(bin_dir, '..', '..'))

    with sh.pushd(git_dir):

        # This is the local last git commit
        last_commit = sh.git('rev-parse', 'HEAD').strip()

        # A list of local updates that have no been committed locally
        local_updates = sh.git('status', '-s').strip().splitlines()

        if local_updates:
            local_updates = [' ' + elem for elem in local_updates]
            local_updates = '\n' + '\n'.join(local_updates)
        else:
            local_updates = ' <none>'

        # A list of local commits that have not been pushed
        local_commits = sh.git('cherry', '-v').strip()

        if local_commits:
            local_commits = [' ' + elem for elem in local_commits]
            local_commits = '\n' + '\n'.join(local_commits)
        else:
            local_commits = ' <none>'

    stdout.write('Zato version:   %s\n' % (last_commit))
    stdout.write('System version: %s\n' % (last_commit))
    stdout.write('Git commit ID:  %s\n' % (last_commit))
    stdout.write('Git timestamp:  %s\n' % (local_commits),)
    stdout.write('Local updates:  %s\n' % (local_updates),)
    stdout.write('Local commits:  %s\n' % (local_commits),)

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

        zato_version = get_version()

        # This is --version --verbose with all the details
        if '--verbose' in sys.argv:
            handle_version_verbose(zato_version)
        else:
            handle_version_only(zato_version)

# ################################################################################################################################
