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

    def create(self, sat_name, sat_desc, deploy_org, env_path, rhevh_macs, rhevm_mac,
               rhevh_hostname, rhevm_hostname, rhevm_adminpass, rhsm_username, rhsm_password,
               rhsm_subs,
               datacenter_name=None, cluster_name=None, storage_name=None, cpu_type=None,
               storage_type=None, storage_address=None, share_path=None, cfme_install_loc="onRhev",
               ):
        """
        Creates a new RHCI deployment with the provided details.
        """
        self.wait_until_element(locators["rhci.new"]).click()
        # RHCI: software selection page
        self.wait_until_element(locators["rhci.next"]).click()
        # RHCI: Satellite Configuration
        if self.wait_until_element(locators["rhci.satellite_name"]):
            self.find_element(locators["rhci.satellite_name"]).send_keys(sat_name)
            self.find_element(locators["rhci.satellite_description"]).send_keys(sat_desc)
            self.wait_until_element(locators["rhci.next"]).click()
        # RHCI: Configure organization page
        if self.wait_until_element(locators["rhci.deployment_org"]):
            self.find_element(locators["rhci.deployment_org"]).click()
            self.wait_until_element(locators["rhci.next"]).click()
        # RHCI: Lifecycle environment page
        if self.wait_until_element((locators["rhci.env_path"][0],
                                    locators["rhci.env_path"][1] % env_path)):
            self.find_element((locators["rhci.env_path"][0],
                               locators["rhci.env_path"][1] % env_path)).click()
            self.wait_until_element(locators["rhci.next"]).click()
        else:
            print "Can't find env_path: %s" % env_path
        # RHCI: RHEV Hypervisor selection page.
        for mac_address in rhevh_macs:
            if self.wait_until_element((locators["rhci.hypervisor_mac_check"][0],
                                        locators["rhci.hypervisor_mac_check"][1] % mac_address)):
                self.find_element((locators["rhci.hypervisor_mac_check"][0],
                                   locators["rhci.hypervisor_mac_check"][1] % mac_address)).click()
        self.wait_until_element(locators["rhci.rhevtab_engine"]).click()
        # RHCI: RHEV Engine selection page.
        if self.wait_until_element((locators["rhci.engine_mac_radio"][0],
                                    locators["rhci.engine_mac_radio"][1] % rhevm_mac)):
            self.find_element((locators["rhci.hypervisor_mac_check"][0],
                               locators["rhci.hypervisor_mac_check"][1] % rhevm_mac)).click()
        self.wait_until_element(locators["rhci.rhevtab_configuration"]).click()
        # RHCI: RHEV Configuration page.
        if self.wait_until_element(locators["rhci.rhevh_hostname"]):
            self.find_element(locators["rhci.rhevh_hostname"]).send_keys(rhevh_hostname)
            self.find_element(locators["rhci.rhevm_hostname"]).send_keys(rhevm_hostname)
            self.find_element(locators["rhci.rhevm_adminpass"]).send_keys(rhevm_adminpass)
            if datacenter_name is not None:
                self.find_element(locators["rhci.datacenter_name"]).send_keys(datacenter_name)
            if cluster_name is not None:
                self.find_element(locators["rhci.cluster_name"]).send_keys(cluster_name)
            if storage_name is not None:
                self.find_element(locators["rhci.storage_name"]).send_keys(storage_name)
            if cpu_type is not None:
                self.find_element(locators["rhci.cpu_type"]).send_keys(cpu_type)
        self.wait_until_element(locators["rhci.rhevtab_storage"]).click()
        # RHCI: RHEV Storage page.
        if self.wait_until_element(locators["rhci.storage_address"]):
            if storage_type is not None:
                self.find_element((locators["rhci.storage_type"][0],
                                   locators["rhci.storage_type"][1] % storage_type)).click()
            if storage_address is not None:
                self.find_element(locators["storage_address"]).send_keys(storage_address)
            if share_path is not None:
                self.find_element(locators["share_path"]).send_keys(share_path)
        self.wait_until_element(locators["rhci.bc_cloudforms"]).click()
        # RHCI: Cloudforms configuration page.
        if self.wait_until_element((locators['rhci.cfme_install_on'][0],
                                    locators['rhci.cfme_install_on'][1] % cfme_install_loc)):
            self.find_element((locators['rhci.cfme_install_on'][0],
                               locators['rhci.cfme_install_on'][1] % cfme_install_loc)).click()
        self.wait_until_element(locators['rhci.bc_subscriptions']).click()
        # RHCI: Subscription Credentials page.
        if self.wait_until_element(locators['rhci.rhsm_username']):
            self.find_element(locators['rhci.rhsm_username']).send_keys(rhsm_username)
            self.find_element(locators['rhci.rhsm_password']).send_keys(rhsm_password)
        self.wait_until_element(locators["rhci.next"]).click()
        # RHCI: Select Subscriptions
        for sub in rhsm_subs:
            if self.wait_until_element((locators["rhci.subscription_check"][0],
                                        locators["rhci.subscription_check"][1] % sub)):
                self.wait_until_element((locators["rhci.subscription_check"][0],
                                         locators["rhci.subscription_check"][1] % sub)).click()
        self.wait_until_element(locators["rhci.subscription_attach"]).click()
        self.wait_until_element(locators["rhci.next"]).click()
        # RCHI: Review Installation page.
        self.wait_until_element(locators["rhci.deploy"]).click()
