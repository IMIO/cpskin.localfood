# -*- coding: utf-8 -*-

from cpskin.core.behaviors import directorycontact
from collective.contact.core import _ as CCMF
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider

from cpskin.localfood import _


@provider(IFormFieldProvider)
class IContactCard(directorycontact.IDirectoryContactDetails):

    form.omitted('use_parent_address')
    form.omitted('im_handle')

    model.fieldset(
        'contact_details',
        label=CCMF(u'Contact details'),
        fields=['name'],
    )

    name = schema.TextLine(
        title=_(u'Name'),
        required=False,
    )


@implementer(IContactCard)
@adapter(IDexterityContent)
class ContactCard(object):

    def __init__(self, context):
        self.context = context
