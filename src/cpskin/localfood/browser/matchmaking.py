# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from collective.taxonomy.interfaces import ITaxonomy
from collective.z3cform.select2.widget.widget import MultiSelect2FieldWidget
from plone import api
from plone.autoform import directives
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


class IProfessionnalsRegistration(Interface):
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

    producer_address = schema.Text(
        title=_(u'Address'),
        required=True,
    )

    horeca_address = schema.Text(
        title=_(u'Address'),
        required=True,
    )

    producer_company_number = schema.TextLine(
        title=_(u'Company number'),
        required=True,
    )

    horeca_company_number = schema.TextLine(
        title=_(u'Company number'),
        required=True,
    )

    producer_phone_number = schema.TextLine(
        title=_(u'Contact phone number'),
        required=True,
    )

    producer_mobile = schema.TextLine(
        title=_(u'Contact mobile'),
        required=False,
    )

    producer_email = schema.TextLine(
        title=_(u'Contact email'),
        required=True,
    )

    horeca_phone_number = schema.TextLine(
        title=_(u'Contact phone number'),
        required=True,
    )

    horeca_mobile = schema.TextLine(
        title=_(u'Contact mobile'),
        required=False,
    )

    horeca_email = schema.TextLine(
        title=_(u'Contact email'),
        required=True,
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

    directives.widget(proposed_products=MultiSelect2FieldWidget)
    proposed_products = schema.List(
        title=_(u'Proposed product types'),
        description=_(u'Please select the types of product you can propose'),
        value_type=schema.Choice(
            title=_(u'Product types'),
            vocabulary='collective.taxonomy.typesproduits',
        ),
        required=False,
    )

    directives.widget(wanted_products=MultiSelect2FieldWidget)
    wanted_products = schema.List(
        title=_(u'Wanted product types'),
        description=_(u'Please select the types of product you want to find'),
        value_type=schema.Choice(
            title=_(u'Product types'),
            vocabulary='collective.taxonomy.typesproduits',
        ),
        required=False,
    )


class LocalProducerSubscriptionForm(Form):
    implements(ILocalProducerForm)
    label = _(u'Subscription as a local producer')
    fields = field.Fields(IProfessionnalsRegistration).select(
        'producer_name',
        'producer_address',
        'producer_phone_number',
        'producer_mobile',
        'producer_email',
        'producer_company_number',
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
                groupname='local_producer',
                user=api.user.get_current(),
            )  # TODO: check if not already in
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
    fields = field.Fields(IProfessionnalsRegistration).select(
        'business_name',
        'purchasing_manager',
        'horeca_address',
        'horeca_phone_number',
        'horeca_mobile',
        'horeca_email',
        'horeca_company_number',
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
