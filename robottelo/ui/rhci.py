# -*- encoding: utf-8 -*-
# vim: ts=4 sw=4 expandtab ai

"""
Implements RHCI UI
"""
from robottelo.ui.base import Base
from robottelo.ui.locators import locators


def interp_loc(locator_name, interpolate_string):
    # given a locator name, return a locator tuple with the interpolate string
    # included in the second tuple element
    # if the string is None or otherwise Falsey, make it an empty string
    interpolate_string = interpolate_string or ''
    return (locators[locator_name][0], locators[locator_name][1] % interpolate_string)


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
               export_domain_share_path=None, cfme_install_loc=None,
               cfme_root_password=None, cfme_admin_password=None):
        """
        Creates a new RHCI deployment with the provided details.
        """
        # Build up dynamic locators:
        env_path_loc = interp_loc('rhci.env_path', env_path)
        rhev_setup_loc = interp_loc('rhci.rhev_setup_type', rhev_setup_type)
        rhevm_mac_loc = interp_loc('rhci.engine_mac_radio', rhevm_mac)
        rhevh_mac_locs = [interp_loc('rhci.hypervisor_mac_check', mac) for mac in rhevh_macs]
        # cfme_install_loc is a kwargs, apologies for the potential confusion
        cfme_install_locator = interp_loc('rhci.cfme_install_on', cfme_install_loc)
        rhsm_sat_radio_loc = interp_loc('rhci.rhsm_satellite_radio', rhsm_satellite_uuid)
        sub_check_locs = [interp_loc('rhci.subscription_check', sub) for sub in rhsm_subs]

        # RHCI: software selection page
        self.click(locators["rhci.select"])

        # RHCI: Satellite Configuration
        if self.wait_until_element(locators["rhci.satellite_name"]):
            self.text_field_update(locators["rhci.satellite_name"], sat_name)
            self.text_field_update(locators["rhci.satellite_description"], sat_desc)
        # RHCI: Configure organization page
        # TODO: Add ability to add new deploy org once the feature is available
        # if self.wait_until_element(locators["rhci.deployment_org"]):
        #    self.find_element(locators["rhci.deployment_org"]).click()
        self.click(locators["rhci.next"])

        # RHCI: Lifecycle environment page
        if use_default_org_view:
            self.click(locators["rhci.next"])
            self.click(locators["rhci.use_default_org_view"])
            self.click(locators["rhci.next"])
        elif self.wait_until_element(env_path_loc):
            self.click(env_path_loc)
            self.click(locators["rhci.next"])
        else:
            print "Can't find env_path: %s" % env_path

        # RHCI: RHEV Setup Type page.
        if self.wait_until_element(rhev_setup_loc):
            self.click(rhev_setup_loc)
            self.click(locators["rhci.next"])
        else:
            print "Can't find locator for rhev_setup_type: %s" % rhev_setup_type

        # RHCI: RHEV Engine selection page.
        self.click(rhevm_mac_loc)
        self.click(locators["rhci.next"])

        # RHCI: RHEV Hypervisor selection page.
        for rhevh_mac_loc in rhevh_mac_locs:
            self.click(rhevh_mac_loc)
        self.click(locators["rhci.next"])

        # RHCI: RHEV Configuration page.
        if self.wait_until_element(locators["rhci.rhev_root_pass"]):
            self.text_field_update(locators["rhci.rhev_root_pass"], rhevm_adminpass)
            self.text_field_update(locators["rhci.rhevm_adminpass"], rhevm_adminpass)
            if datacenter_name is not None:
                self.text_field_update(locators["rhci.datacenter_name"], datacenter_name)
            if cluster_name is not None:
                self.text_field_update(locators["rhci.cluster_name"], cluster_name)
            if cpu_type is not None:
                self.text_field_update(locators["rhci.cpu_type"], cpu_type)
        self.click(locators["rhci.next"])

        # RHCI: RHEV Storage page.
        if self.wait_until_element(locators["rhci.data_domain_name"]):
            # XXX name fields aren't cleared before typing :(
            self.text_field_update(locators["rhci.data_domain_name"], data_domain_name)
            self.text_field_update(locators["rhci.data_domain_address"], data_domain_address)
            self.text_field_update(locators["rhci.data_domain_share_path"], data_domain_share_path)
            self.text_field_update(locators["rhci.export_domain_name"], export_domain_name)
            self.text_field_update(locators["rhci.export_domain_address"], export_domain_address)
            self.text_field_update(locators["rhci.export_domain_share_path"],
                export_domain_share_path)
            self.click(locators["rhci.next"])

        # RHCI: Cloudforms configuration page.
        if self.wait_until_element(cfme_install_locator):
            self.click(cfme_install_locator)
        self.click(locators['rhci.next'])

        self.wait_until_element(locators['rhci.cfme_root_password'])
        self.text_field_update(locators['rhci.cfme_root_password'], cfme_root_password)
        self.text_field_update(locators['rhci.cfme_admin_password'], cfme_admin_password)
        self.click(locators["rhci.next"])

        # RHCI: Subscription Credentials page.
        if self.wait_until_element(locators['rhci.rhsm_username']):
            self.text_field_update(locators['rhci.rhsm_username'], rhsm_username)
            self.text_field_update(locators['rhci.rhsm_password'], rhsm_password)
        self.click(locators["rhci.next"])

        # RHCI: Subscription Management Application.
        self.wait_until_element(rhsm_sat_radio_loc)
        self.click(rhsm_sat_radio_loc)
        self.click(locators["rhci.next"])

        # RHCI: Select Subscriptions
        for sub_check_loc in sub_check_locs:
            if self.wait_until_element(sub_check_loc):
                self.click(sub_check_loc)
        self.click(locators["rhci.next"])

        # RCHI: Review Installation page.
        # self.click(locators["rhci.deploy"])
        # Wait a *long time* for the deployment to complete
