# -*- coding: utf-8 -*-
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implementer

from cpskin.localfood import _


class IProject(model.Schema):
    """ Marker interface and Dexterity Python Schema for Project
    """

    area = schema.Text(
        title=_('Area'),
        required=True,
    )

    owner = schema.TextLine(
        title=_('Owner'),
        required=True,
    )

    occupant = schema.Text(
        title=_('Occupant'),
        required=True,
    )

    availability = schema.Text(
        title=_('Availability'),
        required=True,
    )

    occupationStart = schema.Date(
        title=_('Start of occupation'),
        required=True,
    )

    cultivationType = schema.Text(
        title=_('Type of cultivation'),
        required=True,
    )

    orientation = schema.Text(
        title=_('Orientation'),
        required=True,
    )

    accessibility = schema.Text(
        title=_('Accessibility'),
        required=True,
    )


@implementer(IProject)
class Project(Container):
    """
    """
