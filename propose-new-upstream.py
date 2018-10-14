#!/usr/bin/python
# Copyright (C) 2018 Jelmer Vernooij <jelmer@jelmer.uk>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import silver_platter
from silver_platter.debian import (
    build,
    get_source_package,
    source_package_vcs_url,
    )
from silver_platter.proposal import (
    propose_or_push,
    BranchChanger,
    )

from breezy.branch import Branch
from breezy.plugins.debian.cmds import cmd_merge_upstream

import argparse
parser = argparse.ArgumentParser(prog='propose-new-upstream')
parser.add_argument("packages", nargs='+')
parser.add_argument('--no-build-verify', help='Do not build package to verify it.', action='store_true')
parser.add_argument('--pre-check', help='Command to run to check whether to process package.', type=str)
args = parser.parse_args()


class NewUpstreamMerger(BranchChanger):

    def make_changes(self, local_tree):
        cmd_merge_upstream().run(directory=local_tree.basedir)
        if not args.no_build_verify:
            build(local_tree.basedir)

    def get_proposal_description(self, existing_proposal):
        return "Merge new upstream release %s" % self._upstream_version

    def should_create_proposal(self):
        # There are no upstream merges too small.
        return True


for package in args.packages:
    pkg_source = get_source_package(package)
    vcs_url = source_package_vcs_url(pkg_source)
    main_branch = Branch.open(vcs_url)
    propose_or_push(main_branch, "new-upstream", NewUpstreamMerger(), mode='propose', dry_run=True)
