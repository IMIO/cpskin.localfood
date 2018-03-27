# -*- coding: utf-8 -*-
from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.interface import implementer

from cpskin.localfood import _


class ICommunityGarden(model.Schema):
    """ Marker interface and Dexterity Python Schema for CommunityGarden
    """

    owner = schema.TextLine(
        title=_('Owner'),
        required=True,
    )

    project_author = schema.TextLine(
        title=_('Project Author'),
        required=True,
    )

    manager = schema.TextLine(
        title=_('Manager'),
        required=True,
    )

    inauguration = schema.TextLine(
        title=_('Inauguration'),
        required=True,
    )

    gardener = schema.TextLine(
        title=_('Gardener'),
        required=True,
    )

    address = schema.TextLine(
        title=_('Address'),
        required=True,
    )


@implementer(ICommunityGarden)
class CommunityGarden(Item):
    """
    """
