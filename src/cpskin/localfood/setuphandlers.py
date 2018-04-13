# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer
from Products.CMFCore.utils import getToolByName


def installLocalfood(context):
    site = context.getSite()
    groups_tool = site.portal_groups
    portal_memberdata = getToolByName(site, "portal_memberdata")

    for group_id in (
        'local_producer',
        'horeca_business'
    ):
        if group_id not in groups_tool.getGroupIds():
            groups_tool.addGroup(group_id)

    for property_id in (
        'localfood_proposed_products',
        'localfood_wanted_products',
    ):
        if not portal_memberdata.hasProperty(property_id):
            portal_memberdata.manage_addProperty(id=property_id,
                                                 value=[],
                                                 type="lines")

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
