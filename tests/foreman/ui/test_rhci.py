# -*- encoding: utf-8 -*-
# vim: ts=4 sw=4 expandtab ai

# from robottelo.common.decorators import run_only_on, stubbed
from robottelo.test import UITestCase
# from robottelo.ui.locators import common_locators


class RHCI(UITestCase):

    def test_create_new_deployment(self):
        """@Test: Create a new RHCI deployment

        @Feature: RHCI - Positive Create

        @Assert: Deployment is completed.
        """
        # sleep(3)
        self.navigator.go_to_new_deployment()
        self.rhci.create("foo")
