# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from collective.taxonomy.interfaces import ITaxonomy
from collective.z3cform.select2.widget.widget import MultiSelect2FieldWidget
from plone import api
from plone.autoform import directives
from plone.z3cform.fieldsets.utils import remove
from z3c.form import button
from z3c.form import field
from z3c.form.form import Form
from zope import schema
from zope.component import queryUtility
from zope.interface import Interface, implements

from cpskin.localfood import _


class MatchmakingIntroView(BrowserView):
    pass


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

    # TODO: message explicite sur la case "I Validate"

    @button.buttonAndHandler(_(u'Confirm'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        if data.get('validated', None):
            api.group.add_user(group=self.professionals_group, user=self.member)
            api.portal.show_message(
                message=_(u'Your validation has been recorded.'),
                request=self.request,
                type='info'
            )
            self.request.response.redirect(self.context.absolute_url() + '/@@product-selection')

        if self.in_group:
            self.store_prefs(data)
            api.portal.show_message(
                message=_(u'Your product preferences have been recorded.'),
                request=self.request,
                type='info'
            )
            self.request.response.redirect(self.context.absolute_url() + '/@@product-selection')

        return ''

    def store_prefs(self, data):
        self.member.setMemberProperties(mapping={
            'localfood_proposed_products': data['proposed_products'],
            'localfood_wanted_products': data['wanted_products'],
        })


class ProducerDiscoveryView(BrowserView):

    def __call__(self, *args):
        self.member = api.user.get_current()
        self.professionals_group = api.group.get(groupname='localfood_professionals')
        self.in_group = self.professionals_group in api.group.get_groups(user=self.member)

        name = 'collective.taxonomy.typesproduits'
        self.translator = queryUtility(ITaxonomy, name=name)
        self.target_language = str(self.translator.getCurrentLanguage(self.request))

        return super(ProducerDiscoveryView, self).__call__(*args)

    def translate_taxonomy_id(self, taxo_id):
        return self.translator.translate(taxo_id,
                                         context=self.context,
                                         target_language=self.target_language)

    def get_producers(self):
        results = []
        wanted_products = set(self.member.getProperty('localfood_wanted_products', []))
        # TODO: cas où aucun product désiré
        all_members = api.user.get_users(group=self.professionals_group)
        if self.member in all_members:
            all_members.remove(self.member)
        for member in all_members:
            proposed_products = member.getProperty('localfood_proposed_products', [])
            intersection = wanted_products.intersection(proposed_products)
            if intersection:
                product_names = [self.translate_taxonomy_id(taxo_id) for taxo_id in intersection]
                results.append({
                    'member': member,
                    'products': sorted(product_names)
                })
        return results
