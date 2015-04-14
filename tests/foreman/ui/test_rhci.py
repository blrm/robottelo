# -*- encoding: utf-8 -*-
# vim: ts=4 sw=4 expandtab ai

# from robottelo.common.decorators import run_only_on, stubbed
from robottelo.test import UITestCase
from time import sleep
from conf import rhci


class RHCI(UITestCase):

    def test_create_new_deployment(self):
        """@Test: Create a new RHCI deployment

        @Feature: RHCI - Positive Create

        @Assert: Deployment is completed.
        """
        self.login.login(self.katello_user, self.katello_passwd)
        self.navigator.go_to_rhci_deployments()
        self.rhci.create(sat_name=rhci['wizard']['sat_name'],
                         sat_desc=rhci['wizard']['sat_desc'],
                         deploy_org=None,
                         env_path=rhci['wizard']['env_path'],
                         rhevh_macs=rhci['wizard']['rhevh_macs'],
                         rhevm_mac=rhci['wizard']['rhevm_mac'],
                         rhevh_hostname=rhci['wizard']['rhevh_hostname'],
                         rhevm_hostname=rhci['wizard']['rhevm_hostname'],
                         rhevm_adminpass=rhci['wizard']['rhevm_adminpass'],
                         rhsm_username=rhci['wizard']['rhsm_username'],
                         rhsm_password=rhci['wizard']['rhsm_password'],
                         rhsm_subs=rhci['wizard']['rhsm_subs'])
        sleep(15)
