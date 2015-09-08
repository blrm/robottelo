# -*- encoding: utf-8 -*-
# vim: ts=4 sw=4 expandtab ai

"""
Implements RHCI UI
"""
from time import sleep

from robottelo.ui.base import Base
from robottelo.ui.locators import locators


class RHCI(Base):
    """
    Implements functions for RHCI deployments
    """

    def create(self, sat_name, sat_desc, deploy_org, env_path, rhevh_macs, rhevm_mac,
               rhevh_hostname, rhevm_hostname, rhevm_adminpass, rhsm_username, rhsm_password,
               rhsm_satellite_uuid, rhsm_subs, rhev_setup_type, use_default_org_view=False,
               datacenter_name=None, cluster_name=None, cpu_type=None, storage_type=None,
               data_domain_name=None, export_domain_name=None, data_domain_address=None,
               export_domain_address=None, data_domain_share_path=None,
               export_domain_share_path=None,cfme_install_loc=None,
               cfme_root_password=None, cfme_admin_password=None):
        """
        Creates a new RHCI deployment with the provided details.
        """
        # RHCI: software selection page
        self.wait_until_element(locators["rhci.select"]).click()
        # RHCI: Satellite Configuration
        if self.wait_until_element(locators["rhci.satellite_name"]):
            self.find_element(locators["rhci.satellite_name"]).send_keys(sat_name)
            self.find_element(locators["rhci.satellite_description"]).send_keys(sat_desc)
            self.wait_until_element(locators["rhci.next"]).click()
        # RHCI: Configure organization page
        # TODO: Add ability to add new deploy org once the feature is available
        # if self.wait_until_element(locators["rhci.deployment_org"]):
        #    self.find_element(locators["rhci.deployment_org"]).click()
        self.wait_until_element(locators["rhci.next"]).click()
        # RHCI: Lifecycle environment page
        if use_default_org_view:
            self.wait_until_element(locators["rhci.use_default_org_view"]).click()
            # weird trashing happens here that breaks waiting for the next button
            # unfortunately, the best I have right now to fix it is a sleep
            sleep(3)
            self.wait_until_element(locators["rhci.next"]).click()
        elif self.wait_until_element((locators["rhci.env_path"][0],
                                    locators["rhci.env_path"][1] % env_path)):
            self.find_element((locators["rhci.env_path"][0],
                               locators["rhci.env_path"][1] % env_path)).click()
            self.wait_until_element(locators["rhci.next"]).click()
        else:
            print "Can't find env_path: %s" % env_path
        # RHCI: RHEV Setup Type page.
        if self.wait_until_element((locators["rhci.rhev_setup_type"][0],
                                    locators["rhci.rhev_setup_type"][1] % rhev_setup_type)):
            self.wait_until_element((locators["rhci.rhev_setup_type"][0],
                                    locators["rhci.rhev_setup_type"][1] % rhev_setup_type)).click()
            self.wait_until_element(locators["rhci.next"]).click()
        else:
            print "Can't find locator for rhev_setup_type: %s" % rhev_setup_type
        # RHCI: RHEV Engine selection page.
        if self.wait_until_element((locators["rhci.engine_mac_radio"][0],
                                    locators["rhci.engine_mac_radio"][1] % rhevm_mac)):
            self.find_element((locators["rhci.engine_mac_radio"][0],
                               locators["rhci.engine_mac_radio"][1] % rhevm_mac)).click()
            self.wait_until_element(locators["rhci.next"]).click()
        # RHCI: RHEV Hypervisor selection page.
        for mac_address in rhevh_macs:
            if self.wait_until_element((locators["rhci.hypervisor_mac_check"][0],
                                        locators["rhci.hypervisor_mac_check"][1] % mac_address)):
                self.find_element((locators["rhci.hypervisor_mac_check"][0],
                                   locators["rhci.hypervisor_mac_check"][1] % mac_address)).click()
        self.wait_until_element(locators["rhci.next"]).click()
        # RHCI: RHEV Configuration page.
        if self.wait_until_element(locators["rhci.rhev_root_pass"]):
            self.find_element(locators["rhci.rhev_root_pass"]).send_keys(rhevm_adminpass)
            self.find_element(locators["rhci.rhevm_adminpass"]).send_keys(rhevm_adminpass)
            if datacenter_name is not None:
                self.find_element(locators["rhci.datacenter_name"]).send_keys(datacenter_name)
            if cluster_name is not None:
                self.find_element(locators["rhci.cluster_name"]).send_keys(cluster_name)
            if cpu_type is not None:
                self.find_element(locators["rhci.cpu_type"]).send_keys(cpu_type)
        self.wait_until_element(locators["rhci.next"]).click()
        # RHCI: RHEV Storage page.
        if self.wait_until_element(locators["rhci.data_domain_name"]):
            # XXX name fields aren't cleared before typing :(
            self.find_element(locators["rhci.data_domain_name"]).send_keys(data_domain_name)
            self.find_element(locators["rhci.data_domain_address"]).send_keys(data_domain_address)
            self.find_element(locators["rhci.data_domain_share_path"]).send_keys(data_domain_share_path)
            self.find_element(locators["rhci.export_domain_name"]).send_keys(export_domain_name)
            self.find_element(locators["rhci.export_domain_address"]).send_keys(export_domain_address)
            self.find_element(locators["rhci.export_domain_share_path"]).send_keys(export_domain_share_path)
            self.wait_until_element(locators["rhci.next"]).click()
        # RHCI: Cloudforms configuration page.
        if self.wait_until_element((locators['rhci.cfme_install_on'][0],
                                    locators['rhci.cfme_install_on'][1] % cfme_install_loc)):
            self.find_element((locators['rhci.cfme_install_on'][0],
                               locators['rhci.cfme_install_on'][1] % cfme_install_loc)).click()
        self.wait_until_element(locators['rhci.next']).click()
        self.wait_until_element(locators['rhci.cfme_root_password']).send_keys(cfme_root_password)
        self.wait_until_element(locators['rhci.cfme_admin_password']).send_keys(cfme_admin_password)
        self.wait_until_element(locators['rhci.next']).click()
        # RHCI: Subscription Credentials page.
        if self.wait_until_element(locators['rhci.rhsm_username']):
            self.find_element(locators['rhci.rhsm_username']).send_keys(rhsm_username)
            self.find_element(locators['rhci.rhsm_password']).send_keys(rhsm_password)
        self.wait_until_element(locators["rhci.next"]).click()
        # RHCI: Subscription Management Application.
        self.wait_until_element((locators["rhci.rhsm_satellite_radio"][0],
                                 locators["rhci.rhsm_satellite_radio"][1] % rhsm_satellite_uuid)).click()
        self.wait_until_element(locators["rhci.next"]).click()
        # RHCI: Select Subscriptions
        for sub in rhsm_subs:
            if self.wait_until_element((locators["rhci.subscription_check"][0],
                                        locators["rhci.subscription_check"][1] % sub)):
                self.wait_until_element((locators["rhci.subscription_check"][0],
                                         locators["rhci.subscription_check"][1] % sub)).click()
        self.wait_until_element(locators["rhci.next"]).click()
        # RCHI: Review Installation page.
        self.wait_until_element(locators["rhci.deploy"]).click()
