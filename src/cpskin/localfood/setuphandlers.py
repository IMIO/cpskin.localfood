# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer
from Products.CMFCore.utils import getToolByName


def installLocalfood(context):
    site = context.getSite()

    groups_tool = site.portal_groups
    group_id = 'localfood_professionals'
    if group_id not in groups_tool.getGroupIds():
        groups_tool.addGroup(group_id)

    portal_memberdata = getToolByName(site, "portal_memberdata")
    if not portal_memberdata.hasProperty("localfood_proposed_products"):
        portal_memberdata.manage_addProperty(id="localfood_proposed_products", value=[], type="lines")
    if not portal_memberdata.hasProperty("localfood_wanted_products"):
        portal_memberdata.manage_addProperty(id="localfood_wanted_products", value=[], type="lines")

def uninstallLocalfood(context):
    pass

@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            'cpskin.localfood:uninstall',
        ]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
