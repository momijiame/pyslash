#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import nose
from nose.tools.trivial import ok_
from nose.tools.trivial import eq_

from pyslash.cmd.slash import _parse_args


class Test_slash(object):

    def test_tap_list_default(self):
        sys.argv = ['pyslash', 'tap-list']
        args = _parse_args()
        eq_(args.format, 'table')
        eq_(args.connect, 'qemu:///system')

    def test_format_json(self):
        sys.argv = ['pyslash', '-f', 'json', 'tap-list']
        args = _parse_args()
        eq_(args.format, 'json')

    def test_connect(self):
        sys.argv = ['pyslash', '-c', 'qemu+ssh://remote/system', 'tap-list']
        args = _parse_args()
        eq_(args.connect, 'qemu+ssh://remote/system')


if __name__ == "__main__":
    nose.main(argv=['nosetests', '-s', '-v'], defaultTest=__file__)
