# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage
from collective.z3cform.select2.widget.widget import MultiSelect2FieldWidget
from cpskin.localfood import _
from plone import api
from plone.autoform import directives
from plone.z3cform.fieldsets.utils import remove
from z3c.form import button
from z3c.form import field
from z3c.form.form import Form
from zope import schema
from zope.interface import Interface, implements


class IChartRegistration(Interface):
    validated = schema.Bool(title=u'I validate the chart.')

    proposed_products = schema.List(
        title=_(u'Proposed product types'),
        description=_(u'Please select the types of product you have to propose'),
        value_type=schema.Choice(
            title=_(u'Product types'),
            vocabulary='collective.taxonomy.typesproduits',
        ),
        required=False,
    )
    directives.widget(proposed_products=MultiSelect2FieldWidget)

    wanted_products = schema.List(
        title=_(u'Wanted product types'),
        description=_(u'Please select the types of product you want to find'),
        value_type=schema.Choice(
            title=_(u'Product types'),
            vocabulary='collective.taxonomy.typesproduits',
        ),
        required=False,
    )
    directives.widget(wanted_products=MultiSelect2FieldWidget)


class ProductSelectionForm(Form):
    label = _(u'Product selection')
    fields = field.Fields(IChartRegistration)

    ignoreContext = False

    def update(self):
        self.member = api.user.get_current()
        self.professionals_group = api.group.get(groupname='localfood_professionals')
        self.in_group = self.professionals_group in api.group.get_groups(user=self.member)

        super(ProductSelectionForm, self).update()

    def getContent(self):

        class TemporarySettingsContext(object):
            implements(IChartRegistration)

        obj = TemporarySettingsContext()
        obj.validated = False
        obj.proposed_products = self.member.getProperty('localfood_proposed_products', [])
        obj.wanted_products = self.member.getProperty('localfood_wanted_products', [])

        return obj

    def updateWidgets(self):
        if self.in_group:
            remove(self, 'validated')
        else:
            remove(self, 'proposed_products')
            remove(self, 'wanted_products')

        super(ProductSelectionForm, self).updateWidgets()

    @button.buttonAndHandler(_(u'Confirm'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if data.get('validated', None):
            api.group.add_user(group=self.professionals_group, user=self.member)
            IStatusMessage(self.request).addStatusMessage(
                _(u'Your validation has been recorded.'),
                type=u'info'
            )

            self.request.response.redirect(self.context.absolute_url() + '/@@product-selection')
        if self.in_group:
            self.store_prefs(data)
            IStatusMessage(self.request).addStatusMessage(
                _(u'Your product preferences have been recorded.'),
                type=u'info'
            )

            self.request.response.redirect(self.context.absolute_url() + '/@@product-selection')

        return ''

    def store_prefs(self, data):
        self.member.setMemberProperties(mapping={
            'localfood_proposed_products': data['proposed_products'],
            'localfood_wanted_products': data['wanted_products'],
        })
