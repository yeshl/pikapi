#!/usr/bin/env python
# -*- coding:utf-8 _*-
"""
@author:Administrator
@file: test_validateManager.py
@time: 2019/07/{DAY}
"""
from unittest import TestCase

from pikapi.database import ProxyIP
from pikapi.validators.validate_manager import ValidateManager


class TestValidateManager(TestCase):
    def setUp(self) -> None:
        pass

    def test_validate(self):
        p = ProxyIP(ip='159.203.186.40', port='8080')
        if ValidateManager.should_validate(p):
            v = ValidateManager(p)
            v.validate()
            # s = '\n'.join(['%s:%s' % item for item in p.__dict__.items()])
            s = '\n'.join(['%s:%s' % item for item in p.__data__.items()])
            print("\n")
            print("\033[;35m\t{}\033[0m".format(s))
            p.merge()


