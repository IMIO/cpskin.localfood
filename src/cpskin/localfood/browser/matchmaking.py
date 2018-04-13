# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from collective.taxonomy.interfaces import ITaxonomy
from collective.z3cform.select2.widget.widget import MultiSelect2FieldWidget
from plone import api
from plone.autoform import directives
from plone.z3cform.fieldsets.utils import remove
from plone.z3cform.layout import FormWrapper

from z3c.form import button
from z3c.form import field
from z3c.form.form import Form
from z3c.form.interfaces import NO_VALUE
from zope import schema
from zope.component import queryUtility
from zope.interface import Interface, implements, Invalid

from cpskin.localfood import _


def must_be_checked(value):
    if value:
        return True
    raise Invalid(_("In order to continue, you must check this box."))


class ILocalProducerForm(Interface):
    """Marker interface for local producer/horeca forms"""


class LocalProducerDataProvider(object):

    def get(self):
        prefix = 'localfood'
        return self.member.getProperty(
            '{0}_{1}'.format(prefix, self.field.__name__),
            NO_VALUE
        )

    def __init__(self, context, request, form, field, widget):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget

        self.member = api.user.get_current()


class MatchmakingIntroView(BrowserView):
    pass


class IChartRegistration(Interface):
    validated = schema.Bool(
        title=u'I validate the chart.',
        required=True,
    )

    producer_name = schema.TextLine(
        title=_(u'Producer name'),
        required=True,
    )

    business_name = schema.TextLine(
        title=_(u'Business name'),
        required=True,
    )

    purchasing_manager = schema.TextLine(
        title=_(u'Purchasing manager'),
        required=True,
    )

    address = schema.Text(
        title=_(u'Address'),
        required=True,
    )

    company_number = schema.TextLine(
        title=_(u'Company number'),
        required=True,
    )

    contacts = schema.Text(
        title=_(u'Contacts'),
        required=False,
    )

    contact_by = schema.Choice(
        title=_(u'Contact by'),
        required=True,
        values=['Email', 'SMS'],
    )

    localfood_chart_acceptation = schema.Bool(
        title=u'I accept the chart conditions.',
        # TODO: comment ajouter proprement une URL dans le title, sans context?
        required=True,
        constraint=must_be_checked,
    )

    genuine_form_data = schema.Bool(
        title=u'The data I provide is genuine.',
        required=True,
        constraint=must_be_checked,
    )

    genuine_form_data_and_quality = schema.Bool(
        title=u'The data I provide is genuine, the products are fine.',
        required=True,
        constraint=must_be_checked,
    )

    proposed_products = schema.List(
        title=_(u'Proposed product types'),
        description=_(u'Please select the types of product you can propose'),
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


class LocalProducerSubscriptionForm(Form):
    implements(ILocalProducerForm)
    label = _(u'Subscription as a local producer')
    fields = field.Fields(IChartRegistration).select(
        'producer_name',
        'address',
        'contacts',
        'company_number',
        'proposed_products',
        'contact_by',
        'localfood_chart_acceptation',
        'genuine_form_data_and_quality',
    )

    ignoreContext = True


    @button.buttonAndHandler(_(u'Confirm'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        else:
            api.group.add_user(
                group='local_producer',
                user=api.user.get_current())  # TODO: check if not already in
            self.store_prefs(data)
            api.portal.show_message(
                message=_(u'Your preferences have been recorded.'),
                request=self.request,
                type='info',
            )

    def store_prefs(self, data):
        prefix = 'localfood'
        data_dict = {'{0}_{1}'.format(prefix, key): value
                     for (key, value) in data.iteritems()}
        member = api.user.get_current()
        member.setMemberProperties(mapping=data_dict)


class LocalProducerSubscriptionView(FormWrapper):
    form = LocalProducerSubscriptionForm


class HORECASubscriptionForm(Form):
    implements(ILocalProducerForm)
    label = _(u'Subscription as a HORECA business')
    fields = field.Fields(IChartRegistration).select(
        'business_name',
        'purchasing_manager',
        'address',
        'contacts',
        'company_number',
        'wanted_products',
        'contact_by',
        'localfood_chart_acceptation',
        'genuine_form_data',
    )

    ignoreContext = True

    @button.buttonAndHandler(_(u'Confirm'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        else:
            api.group.add_user(
                group='horeca_business',
                user=api.user.get_current())  # TODO: check if not already in
            self.store_prefs(data)
            api.portal.show_message(
                message=_(u'Your preferences have been recorded.'),
                request=self.request,
                type='info',
            )

    def store_prefs(self, data):
        prefix = 'localfood'
        data_dict = {'{0}_{1}'.format(prefix, key): value
                     for (key, value) in data.iteritems()}
        member = api.user.get_current()
        member.setMemberProperties(mapping=data_dict)


class HORECASubscriptionView(FormWrapper):
    form = HORECASubscriptionForm


class ProductSelectionForm(Form):
    label = _(u'Product selection')
    fields = field.Fields(IChartRegistration)

    ignoreContext = False

    def update(self):
        self.member = api.user.get_current()
        self.group = api.group.get(groupname='localfood_professionals')
        self.in_group = self.group in api.group.get_groups(user=self.member)

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
            api.group.add_user(group=self.group, user=self.member)
            api.portal.show_message(
                message=_(u'Your validation has been recorded.'),
                request=self.request,
                type='info'
            )
            self.request.response.redirect(
                '{0}/@@local-product-selection'.format(self.context.absolute_url()),
            )

        if self.in_group:
            self.store_prefs(data)
            api.portal.show_message(
                message=_(u'Your product preferences have been recorded.'),
                request=self.request,
                type='info'
            )
            self.request.response.redirect(
                '{0}/@@local-product-selection'.format(self.context.absolute_url()),
            )

        return ''

    def store_prefs(self, data):

        self.member.setMemberProperties(mapping={
            'localfood_proposed_products': data['proposed_products'],
            'localfood_wanted_products': data['wanted_products'],
        })


class ProducerDiscoveryView(BrowserView):

    def __call__(self, *args):
        self.member = api.user.get_current()
        self.horeca_business_group = api.group.get(groupname='horeca_business')
        self.local_producer_group = api.group.get(groupname='local_producer')
        self.is_horeca_business = self.horeca_business_group \
                                  in api.group.get_groups(user=self.member)

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
        all_producers = api.user.get_users(group=self.local_producer_group)
        if self.member in all_producers:
            all_producers.remove(self.member)
        for producer in all_producers:
            proposed_products = producer.getProperty('localfood_proposed_products', [])
            intersection = wanted_products.intersection(proposed_products)
            if intersection:
                product_names = [self.translate_taxonomy_id(taxo_id) for taxo_id in intersection]
                results.append({
                    'user': producer,
                    'products': sorted(product_names)
                })
        return results


