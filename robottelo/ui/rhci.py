# -*- encoding: utf-8 -*-
# vim: ts=4 sw=4 expandtab ai

"""
Implements RHCI UI
"""

from robottelo.ui.base import Base
from robottelo.ui.locators import locators


class RHCI(Base):
    """
    Implements functions for RHCI deployments
    """

    def create(self, name):
        """
        Creates a new RHCI deployment with the provided details.
        """
        self.wait_until_element(locators["rhci.next"]).click()
        self.wait_for_ajax()
