# -*- coding: utf-8 -*-
from plone.dexterity.content import Container
from plone.supermodel import model
from plone.namedfile.field import NamedBlobImage
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
        required=False,
    )

    availability = schema.Text(
        title=_('Availability'),
        required=False,
    )

    occupationStart = schema.Date(
        title=_('Start of occupation'),
        required=False,
    )

    cultivationType = schema.Text(
        title=_('Type of cultivation'),
        required=False,
    )

    orientation = schema.Text(
        title=_('Orientation'),
        required=False,
    )

    accessibility = schema.Text(
        title=_('Accessibility'),
        required=False,
    )

    address = schema.TextLine(
        title=_('Address'),
        required=False,
    )

    image = NamedBlobImage(
        title=_('Lead image'),
        required=False,
    )


@implementer(IProject)
class Project(Container):
    """
    """
