# -*- encoding: utf-8 -*-
# vim: ts=4 sw=4 expandtab ai

"""
Implements RHCI UI
"""
from time import sleep
from robottelo.ui.base import Base
from robottelo.ui.locators import locators
from robottelo.common.helpers import get_server_url
from selenium.webdriver.support.select import Select
import requests
import socket, errno


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

    def create(self, sat_name, sat_desc, products, deploy_org, env_path, overcloud_nodes,
               rhevh_macs, rhevm_mac, undercloud_user, undercloud_pass, update_lifecycle,
               rhevh_hostname, rhevm_hostname, rhevm_adminpass, rhsm_username, rhsm_password,
               rhsm_satellite_uuid, rhsm_subs, rhev_setup_type, use_default_org_view=False,
               enable_access_insights=False,
               datacenter_name=None, cluster_name=None, cpu_type=None, storage_type=None,
               data_domain_name=None, export_domain_name=None, data_domain_address=None,
               export_domain_address=None, data_domain_share_path=None,
               export_domain_share_path=None, selfhosted_domain_address=None,
               selfhosted_domain_share_path=None, selfhosted_domain_name=None, cfme_install_loc=None,
               cfme_root_password=None, cfme_admin_password=None, cfme_db_password=None,
               undercloud_address=None, overcloud_external_nic=None, overcloud_prov_network=None,
               overcloud_controller_count=None, overcloud_compute_count=None,
               overcloud_pub_network=None, overcloud_pub_gateway=None, overcloud_admin_pass=None,
               disconnected_url=None, disconnected_manifest=None, ose_install_loc=None,
               ose_storage_size=None, ose_username=None, ose_user_password=None,
               ose_root_password=None, ose_master_vcpu=None, ose_master_ram=None,
               ose_master_disk=None, ose_node_vcpu=None, ose_node_ram=None, ose_node_disk=None,
               ose_available_vcpu=None, ose_available_ram=None, ose_available_disk=None,
               ose_number_master_nodes=None, ose_number_worker_nodes=None, ose_storage_type=None,
               ose_storage_name=None, ose_storage_host=None, ose_export_path=None,
               ose_subdomain_name=None):

        """
        Creates a new RHCI deployment with the provided details.
        """
        # Build up dynamic locators:
        env_path_loc = interp_loc('rhci.env_path', env_path)
        rhev_setup_loc = interp_loc('rhci.rhev_setup_type', rhev_setup_type)
        rhevm_mac_loc = interp_loc('rhci.engine_mac_radio', rhevm_mac)
        rhevh_mac_locs = [interp_loc('rhci.hypervisor_mac_check', mac) for mac in rhevh_macs]
        rhev_storage_type_loc = interp_loc('rhci.storage_type', storage_type)
        # cfme_install_loc is a kwargs, apologies for the potential confusion
        cfme_install_locator = interp_loc('rhci.cfme_install_on', cfme_install_loc)
        rhsm_sat_radio_loc = interp_loc('rhci.rhsm_satellite_radio', rhsm_satellite_uuid)
        sub_check_locs = [interp_loc('rhci.subscription_check', sub) for sub in rhsm_subs]
        # TODO: get rid of this locator once we have actual version checking
        rhai_present_locator = interp_loc('rhci.active_view', '1D. Access Insights')

        # check whether the Configure Organization tab is present
        org_present_locator = interp_loc('rhci.active_view', '1B. Configure Organization')
        error_screenshot_name = 'webui_error_screenshot.png'
        try:
            self._page_software_selection(products)

            self._page_satellite_configuration(sat_name, sat_desc, org_present_locator)
            self._page_lifecycle_environment(env_path_loc, env_path, update_lifecycle)
            self._page_access_insights(rhai_present_locator,enable_access_insights)

            # RHCI: Openstack Configuration
            if "openstack" in products:
                self._page_discover_undercloud(undercloud_address, undercloud_user, undercloud_pass)
                self._page_register_nodes(overcloud_nodes)
                self._page_assign_nodes(overcloud_controller_count, overcloud_compute_count)
                self._configure_overcloud(overcloud_external_nic, overcloud_prov_network,
                                          overcloud_pub_network, overcloud_pub_gateway,
                                          overcloud_admin_pass)

            # RHCI: RHEV Setup Type page.
            if "rhev" in products:
                self._page_rhev_setup_type(rhev_setup_loc, rhev_setup_type)
                # Only go to the engine selection page if RHEV is not self-hosted
                if "selfhost" not in rhev_setup_type:
                    self._page_rhev_engine_selection(rhevm_mac_loc)
                self._page_rhev_hypervisor_selection(rhevh_mac_locs)
                self._page_rhev_configuration(rhevm_adminpass, datacenter_name, cluster_name, cpu_type)
                self._page_rhev_storage_configuration(data_domain_name, data_domain_address, data_domain_share_path,
                                                      export_domain_name, export_domain_address, export_domain_share_path,
                                                      rhev_storage_type_loc, selfhosted_domain_name,
                                                      selfhosted_domain_address, selfhosted_domain_share_path)

            if "cloudforms" in products:
                self._page_cloudforms_configuration(cfme_install_locator, cfme_root_password, cfme_admin_password, cfme_db_password)

            if disconnected_url and disconnected_manifest:
                self._page_disconnected(disconnected_url, disconnected_manifest)
            else:
                self._page_redhat_login(rhsm_username, rhsm_password)
                self._page_subscription_manager_apps(rhsm_sat_radio_loc)
                self._page_select_subscriptions(sub_check_locs)
            self._page_review_subscriptions()
            self._page_review_deployment()
        except:
            self.browser.get_screenshot_as_file(error_screenshot_name)
            raise


    def _page_software_selection(self, products):
        # RHCI: software selection page
        # Deselect everything
        # self.click(interp_loc('rhci.product_deselect', 'rhev'))
        # Select products to install
        for prod in products:
            self.click(interp_loc('rhci.product_select', prod))
        self.click(locators["rhci.next"])

    def _page_satellite_configuration(self, sat_name, sat_desc, org_present_locator):
        # RHCI: Satellite Configuration
        if self.wait_until_element(locators["rhci.satellite_name"]):
            self.text_field_update(locators["rhci.satellite_name"], sat_name)
            self.text_field_update(locators["rhci.satellite_description"], sat_desc)
        self.click(locators["rhci.next"])
        # RHCI: Configure organization page
        # TODO: Add ability to add new deploy org once the feature is available
        # if self.wait_until_element(locators["rhci.deployment_org"]):
        #    self.find_element(locators["rhci.deployment_org"]).click()
        #
        # The Configure Organization tab was removed at one point, so check whether the extra "next" click is necessary
        if self.wait_until_element(org_present_locator):
            self.click(locators["rhci.next"])

    def _page_lifecycle_environment(self, env_path_loc, env_path, update_lifecycle):
        # RHCI: Lifecycle environment page
        self.click(interp_loc('rhci.update_lifecycle_select', update_lifecycle))
        # if env_path:
        #     self.click(env_path_loc)
        self.click(locators["rhci.next"])

    def _page_access_insights(self, rhai_present_locator, enable_access_insights):
        # RHCI: Enable Access Insights page
        # TODO: replace this workaround once we have version checking.
        # if self.wait_until_element(rhai_present_locator):
        if enable_access_insights:
            self.click(locators["rhci.enable_access_insights"])
        self.click(locators["rhci.next"])

    def _page_discover_undercloud(self, undercloud_address, undercloud_user, undercloud_pass):
        # RHCI: Detect Undercloud page.
        self.text_field_update(locators['rhci.undercloud_ip'], undercloud_address)
        self.text_field_update(locators['rhci.undercloud_ssh_user'], undercloud_user)
        self.text_field_update(locators['rhci.undercloud_ssh_pass'], undercloud_pass)
        self.click(locators['rhci.detect_undercloud'])
        self.click(locators['rhci.next'])

    def _page_register_nodes(self, overcloud_nodes):
        # RHCI: Register Nodes
        node_count_loc = interp_loc('rhci.registered_node_count', len(overcloud_nodes))

        #Skip registering nodes if you have enough nodes available
        if not self.is_element_enabled(node_count_loc):
            self.click(locators['rhci.register_nodes'])
            # Select Manual Entry

            # Assume that all of the nodes are on the same libvirt server
            libvirt_info = {
                'driver': overcloud_nodes[0]['driver'],
                'ip_address': overcloud_nodes[0]['ip_address'],
                'username': overcloud_nodes[0]['username'],
                'password': overcloud_nodes[0]['password'],
                }
            self.text_field_update(locators['rhci.node_ip_address'], libvirt_info['ip_address'])
            self.click(interp_loc('rhci.node_driver_dropdown_item', libvirt_info['driver']))
            self.click(locators['rhci.node_driver_select'])
            self.text_field_update(locators['rhci.node_ipmi_user'], libvirt_info['username'])
            self.text_field_update(locators['rhci.node_ipmi_pass'], libvirt_info['password'])
            osp_node_macs = []
            # Need to append the macs into a string separated by newlines
            for node_num, node in enumerate(overcloud_nodes):
                osp_node_macs.append(node['mac_address'])

            if len(osp_node_macs) != len(overcloud_nodes):
                raise Exception(
                    'The number of mac address({}) for OSP node registration is not the same as'
                    ' the number of overcloud nodes({})'.format(
                        len(osp_node_macs), len(overcloud_nodes)))

            self.text_field_update(locators['rhci.node_nic_mac_addresses'], '\n'.join(osp_node_macs))
            self.wait_until_element_is_clickable(locators["rhci.node_node_register_submit"], timeout=30)
            self.click(locators["rhci.node_node_register_submit"])

        # TODO: Wait for node count > 0
        if not self.wait_until_element(locators['rhci.node_manager_panel'], timeout=120):
            print "Register Nodes: Timeout while waiting for OSP Manager table to display"

        if not self.wait_until_element(node_count_loc, timeout=1200):
            print "Register Nodes: Timeout while waiting for 'Node Count' to update"

        self.wait_until_element_is_clickable(locators['rhci.next'], timeout=30)
        self.click(locators['rhci.next'])

    def _page_assign_nodes(
            self, controller_count, compute_count, ceph_count=0, block_count=0, object_count=0):
        # RHCI: Assign Nodes
        # Assign some roles here once nodes are registered

        while self.is_element_visible(locators['rhci.spinner']):
            print 'Waiting for Loading... element to disappear'
            sleep(1)

        # Refresh the page if assign role isn't visible initially
        refresh_attempts = 0
        max_refresh_attempts = 3
        while not self.is_element_visible(locators['rhci.node_assign_role']):
            if refresh_attempts >= max_refresh_attempts:
                print 'Assign Nodes (): Assign role is not visible on initial page load'
                raise Exception('Unable to proceed because Assign Role element is missing')
            self.browser.refresh()
            refresh_attempts += 1

        print 'Starting assignment of OSP node roles'
        for role in [
                { # Controller node role
                    'locator':locators['rhci.node_role_controller'],
                    'locator_count':locators['rhci.node_role_controller_count_select'],
                    'name': 'Controller',
                    'count': controller_count},
                { # Compute node role
                    'locator':locators['rhci.node_role_compute'],
                    'locator_count':locators['rhci.node_role_compute_count_select'],
                    'name': 'Compute',
                    'count': compute_count},
                { # Ceph node role
                    'locator': locators['rhci.node_role_ceph'],
                    'locator_count':locators['rhci.node_role_ceph_count_select'],
                    'name': 'Ceph',
                    'count': ceph_count},
                { # Block node role
                    'locator': locators['rhci.node_role_block'],
                    'locator_count':locators['rhci.node_role_block_count_select'],
                    'name': 'Block',
                    'count': block_count},
                { # Object node role
                    'locator': locators['rhci.node_role_object'],
                    'locator_count':locators['rhci.node_role_object_count_select'],
                    'name': 'Object',
                    'count': object_count}, ]:

            if not self.is_element_enabled(role['locator']):
                if role['count'] < 1:
                    # Don't assign a role is there are zero nodes available
                    continue

                #Assign X nodes to role
                if not self.wait_until_element_is_clickable(
                        locators['rhci.node_assign_role'], timeout=180):
                    print 'Assign Nodes ({}): Assign role is not a clickable element'.format(
                            role['name'])
                    raise Exception('Unable to proceed because Assign Role element is missing')

                print 'Clicking assign role'
                self.click(locators['rhci.node_assign_role'])

                if not self.wait_until_element_is_clickable(role['locator'], timeout=30):
                    print 'Assign Nodes: Timeout while waiting for {} role'.format(role['name'])
                    raise Exception('Unable to proceed because Assign Role element is missing for {}'.format(role['name']))
                print 'Assigning {} role'.format(role['name'])
                self.click(role['locator'])

                print 'Assigning {} role count of {}'.format(role['name'], role['count'])
                ##### HACK UNTIL RHCI BRANCH IS REBASED ON TOP OF SOURCE BRANCH
                # Making pure Selenium calls to update the select element.
                # Robottelo master as assign_value to do this cleanly
                element = self.wait_until_element(role['locator_count'])
                Select(element).select_by_visible_text(str(role['count']))
                ##### HACK END


        self.wait_until_element_is_clickable(locators['rhci.next'],timeout=30)
        self.click(locators['rhci.next'])

    def _configure_overcloud(self, overcloud_external_nic, overcloud_prov_network,
                             overcloud_pub_network, overcloud_pub_gateway, overcloud_admin_pass):
        self.text_field_update(locators["rhci.osp_external_interface"], overcloud_external_nic)
        self.text_field_update(locators["rhci.osp_private_network"], overcloud_prov_network)
        self.text_field_update(locators["rhci.osp_public_network"], overcloud_pub_network)
        self.text_field_update(locators["rhci.osp_public_gateway"], overcloud_pub_gateway)
        self.text_field_update(locators["rhci.osp_overcloud_pass"], overcloud_admin_pass)
        self.text_field_update(locators["rhci.osp_overcloud_pass_confirm"], overcloud_admin_pass)
        self.wait_until_element_is_clickable(locators['rhci.next'],timeout=30)
        self.click(locators['rhci.next'])

    def _page_rhev_setup_type(self, rhev_setup_loc, rhev_setup_type):
        if self.wait_until_element(rhev_setup_loc):
            self.click(rhev_setup_loc)
            self.click(locators["rhci.next"])
        else:
            print "Can't find locator for rhev_setup_type: %s" % rhev_setup_type
            self.click(locators["rhci.next"])

    def _page_rhev_engine_selection(self, rhevm_mac_loc):
        # RHCI: RHEV Engine selection page.
        self.click(rhevm_mac_loc)
        self.click(locators["rhci.next"])

    def _page_rhev_hypervisor_selection(self, rhevh_mac_locs):
        # RHCI: RHEV Hypervisor selection page.s(self,
        for rhevh_mac_loc in rhevh_mac_locs:
            self.click(rhevh_mac_loc)
        self.click(locators["rhci.next"])

    def _page_rhev_configuration(self, rhevm_adminpass, datacenter_name, cluster_name, cpu_type):
        # RHCI: RHEV Configuration page.
        if self.wait_until_element(locators["rhci.rhev_root_pass"]):
            self.text_field_update(locators["rhci.rhev_root_pass"], rhevm_adminpass)
            if self.wait_until_element(locators["rhci.confirm_rhev_root_pass"],timeout=5):
                self.text_field_update(locators["rhci.confirm_rhev_root_pass"], rhevm_adminpass)
            self.text_field_update(locators["rhci.rhevm_adminpass"], rhevm_adminpass)
            if self.wait_until_element(locators["rhci.confirm_rhevm_adminpass"],timeout=5):
                self.text_field_update(locators["rhci.confirm_rhevm_adminpass"], rhevm_adminpass)
            if datacenter_name is not None:
                self.text_field_update(locators["rhci.datacenter_name"], datacenter_name)
            if cluster_name is not None:
                self.text_field_update(locators["rhci.cluster_name"], cluster_name)
            if cpu_type is not None:
                self.text_field_update(locators["rhci.cpu_type"], cpu_type)
        self.click(locators["rhci.next"])

    def _page_rhev_storage_configuration(self, data_domain_name, data_domain_address, data_domain_share_path,
                                         export_domain_name, export_domain_address, export_domain_share_path,
                                         rhev_storage_type_loc, selfhosted_domain_name, selfhosted_domain_address,
                                         selfhosted_domain_share_path):
        # RHCI: RHEV Storage page.
        if self.wait_until_element(rhev_storage_type_loc):
            self.click(rhev_storage_type_loc)
        if self.wait_until_element(locators["rhci.data_domain_name"]):
            self.text_field_update(locators["rhci.data_domain_name"], data_domain_name)
            self.text_field_update(locators["rhci.data_domain_address"], data_domain_address)
            self.text_field_update(locators["rhci.data_domain_share_path"], data_domain_share_path)
            # TODO: identify storage fields that should be present based on products being installed.
            if self.wait_until_element(locators["rhci.export_domain_name"],timeout=5):
                self.text_field_update(locators["rhci.export_domain_name"], selfhosted_domain_name)
                self.text_field_update(locators["rhci.export_domain_address"], selfhosted_domain_address)
                self.text_field_update(locators["rhci.export_domain_share_path"],
                    selfhosted_domain_share_path)
            if self.wait_until_element(locators["rhci.selfhosted_domain_name"],timeout=5):
                self.text_field_update(locators["rhci.selfhosted_domain_name"], export_domain_name)
                self.text_field_update(locators["rhci.selfhosted_domain_address"], export_domain_address)
                self.text_field_update(locators["rhci.selfhosted_domain_share_path"],
                    export_domain_share_path)
            self.click(locators["rhci.next"])

    def _page_cloudforms_configuration(self, cfme_install_locator, cfme_root_password, cfme_admin_password, cfme_db_password):
        print "CloudForms Install Location page"
        # RHCI: Cloudforms configuration page.
        if self.wait_until_element(cfme_install_locator):
            self.click(cfme_install_locator)
        self.click(locators['rhci.next'])

        print "CloudForms credentials configuration page"
        self.wait_until_element(locators['rhci.cfme_root_password'])
        self.text_field_update(locators['rhci.cfme_root_password'], cfme_root_password)
        if self.wait_until_element(locators['rhci.confirm_cfme_root_password'],timeout=5):
            self.text_field_update(locators['rhci.confirm_cfme_root_password'], cfme_root_password)

        self.text_field_update(locators['rhci.cfme_admin_password'], cfme_admin_password)
        if self.wait_until_element(locators['rhci.confirm_cfme_admin_password'], timeout=5):
            self.text_field_update(locators['rhci.confirm_cfme_admin_password'], cfme_admin_password)

        if self.is_element_visible(locators['rhci.cfme_db_password']):
            self.text_field_update(locators['rhci.cfme_db_password'], cfme_db_password)
            if self.wait_until_element(locators['rhci.confirm_cfme_db_password'], timeout=5):
                self.text_field_update(locators['rhci.confirm_cfme_db_password'], cfme_db_password)

        self.click(locators["rhci.next"])

    def _page_redhat_login(self, rhsm_username, rhsm_password):
        print "Customer Portal Login Page"
        # RHCI: Subscription Credentials page.
        if self.wait_until_element(locators['rhci.rhsm_username']):
            self.text_field_update(locators['rhci.rhsm_username'], rhsm_username)
            self.text_field_update(locators['rhci.rhsm_password'], rhsm_password)
        self.click(locators["rhci.next"])

    def _page_disconnected(self, disconnected_url, disconnected_manifest):
        if self.wait_until_element(locators['rhci.rhsm_disconnected']):
            self.click(locators['rhci.rhsm_disconnected'])
        self.text_field_update(locators['rhci.rhsm_mirror'], disconnected_url)
        path = self.wait_until_element(locators['rhci.manifest_upload_file'])
        path.send_keys(disconnected_manifest)
        self.wait_until_element(locators["rhci.manifest_upload_button"]).click()
        self.wait_for_ajax()
        # Waits till the below locator is visible or until 120 seconds.
        self.wait_until_element(locators["rhci.manifest_upload_success"], 120)
        self.click(locators["rhci.next"])

    def _page_subscription_manager_apps(self, rhsm_sat_radio_loc):
        print "Selecting Subscription Management Application"
        # RHCI: Subscription Management Application.
        self.wait_until_element(rhsm_sat_radio_loc)
        self.click(rhsm_sat_radio_loc)
        self.click(locators["rhci.next"])

    def _page_select_subscriptions(self, sub_check_locs):
        print "Selecting Subscriptions"
        # RHCI: Select Subscriptions
        for sub_check_loc in sub_check_locs:
            if self.wait_until_element(sub_check_loc):
                self.click(sub_check_loc)
        self.click(locators["rhci.next"])

    def _page_review_subscriptions(self):
        # RHCI: Review Subscriptions
        print "Review  Subscriptions Page"
        # Disable the ajax wait.  The addition of the "Syncing OpenStack..." API call server side
        # was causing the click method to click the button while still searching for the button
        self.click(locators["rhci.next"], wait_for_ajax=False)

    def _page_review_deployment(self):
        def wait_for_server_connection():
            success = False
            attempts = 0
            while attempts < 5 and not success:
                try:
                    r = requests.get(get_server_url(), verify=False, timeout=10)
                    if r.status_code == 200:
                        success = True
                except socket.error as e:
                    if e.errno == errno.ECONNREFUSED:
                        print "Attempt {} - connection refused! waiting 30s to retry...".format(attempts)
                        sleep(30)  # wait for 30 seconds before re-checking
                        attempts += 1
                    else:
                        raise

        # RHCI: Review Installation page.
        print "Review Installation page"
        self.wait_until_element_is_clickable(locators["rhci.deploy"], timeout=90)
        self.click(locators["rhci.deploy"], timeout=300)
        # Wait a *long time* for the deployment to complete
        # Sleep for five minutes, then check if the next button is available to click
#        for __ in range(60):
#            sleep(360)  # wait for 5 minutes
#            wait_for_server_connection()
#            if self.is_element_visible(locators["rhci.next"]):
#                self.click(locators["rhci.next"])
#                break
#            else:
#                wait_for_server_connection()
#                self.browser.refresh()
#        else:
#            raise Exception('Next button never became available to click')
