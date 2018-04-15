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
from zope.schema.interfaces import RequiredMissing

from cpskin.localfood import _


def must_be_checked(value):
    if value:
        return True
    raise Invalid(_("In order to continue, you must check this box."))


def must_have_selection(value):
    if value:
        return True
    raise RequiredMissing


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

    producer_address = schema.TextLine(
        title=_(u'Address'),
        required=True,
    )

    horeca_address = schema.TextLine(
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
        title=_(u'I accept the chart conditions.'),
        required=True,
        constraint=must_be_checked,
    )

    genuine_form_data = schema.Bool(
        title=_(u'The data I provide is genuine.'),
        required=True,
        constraint=must_be_checked,
    )

    genuine_form_data_and_quality = schema.Bool(
        title=_(u'The data I provide is genuine, the products are fine.'),
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
        required=True,
        constraint=must_have_selection,
    )

    directives.widget(wanted_products=MultiSelect2FieldWidget)
    wanted_products = schema.List(
        title=_(u'Wanted product types'),
        description=_(u'Please select the types of product you want to find'),
        value_type=schema.Choice(
            title=_(u'Product types'),
            vocabulary='collective.taxonomy.typesproduits',
        ),
        required=True,
        constraint=must_have_selection,
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
        data_dict = {'{0}_{1}'.format(prefix, key): value or ''
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
                groupname='horeca_business',
                user=api.user.get_current())  # TODO: check if not already in
            self.store_prefs(data)
            api.portal.show_message(
                message=_(u'Your preferences have been recorded.'),
                request=self.request,
                type='info',
            )

    def store_prefs(self, data):
        prefix = 'localfood'
        data_dict = {'{0}_{1}'.format(prefix, key): value or ''
                     for (key, value) in data.iteritems()}
        member = api.user.get_current()
        member.setMemberProperties(mapping=data_dict)


class HORECASubscriptionView(FormWrapper):
    form = HORECASubscriptionForm


class ProducerDiscoveryView(BrowserView):

    _producer_contact = (
        ('producer_name', u'Producer name'),
        ('producer_address', u'Address'),
        ('producer_phone_number', u'Contact phone number'),
        ('producer_mobile', u'Contact mobile'),
        ('producer_email', u'Contact email'),
        ('contact_by', u'Contact by'),
    )

    _horeca_contact = (
        ('business_name', u'Business name'),
        ('purchasing_manager', u'Purchasing manager'),
        ('horeca_address', u'Address'),
        ('horeca_phone_number', u'Contact phone number'),
        ('horeca_mobile', u'Contact mobile'),
        ('horeca_email', u'Contact email'),
        ('contact_by', u'Contact by'),
    )

    def __call__(self, *args):
        if not self.is_anonymous:
            self.current_user = api.user.get_current()
            self.user_groups = api.group.get_groups(user=self.current_user)
            self.translator = queryUtility(
                ITaxonomy,
                name='collective.taxonomy.typesproduits',
            )
            self.target_language = str(
                self.translator.getCurrentLanguage(self.request),
            )

        return super(ProducerDiscoveryView, self).__call__(*args)

    @property
    def is_anonymous(self):
        """Verify if the current user is anonymous"""
        return api.user.is_anonymous()

    @property
    def in_horeca_group(self):
        """Verify if the current user is in the horeca_business group"""
        return 'horeca_business' in [g.id for g in self.user_groups]

    @property
    def in_local_producer_group(self):
        """Verify if the current user is in the local_producer group"""
        return 'local_producer' in [g.id for g in self.user_groups]

    def translate_taxonomy_id(self, taxonomy_id):
        return self.translator.translate(
            taxonomy_id,
            context=self.context,
            target_language=self.target_language,
        )

    def looking_for_producers(self):
        """
        Return a list of producers by product that the user is looking for
        """
        products = self.current_user.getProperty(
            'localfood_wanted_products',
            [],
        )
        producers = [
            self.extract_producer_contact(u, products)
            for u in api.user.get_users(groupname='local_producer')
        ]
        return [
            {
                'name': self.translate_taxonomy_id(p),
                'contacts': [contact for contact, proposed_products in producers
                             if p in proposed_products]
            }
            for p in products
        ]

    def looking_for_horeca(self):
        """
        Return a list of horeca business by product that I propose
        """
        products = self.current_user.getProperty(
            'localfood_proposed_products',
            [],
        )
        horeca_business = [
            self.extract_horeca_contact(u, products)
            for u in api.user.get_users(groupname='horeca_business')
        ]
        return [
            {
                'name': self.translate_taxonomy_id(p),
                'contacts': [contact for contact, wanted_products in horeca_business
                             if p in wanted_products],
            }
            for p in products
        ]

    def extract_producer_contact(self, user, products):
        proposed_products = set(user.getProperty('localfood_proposed_products', []))  # noqa
        if proposed_products.intersection(products):
            return (
                [(_(t), user.getProperty('localfood_{0}'.format(k)))
                 for k, t in self._producer_contact],
                proposed_products.intersection(products),
            )

    def extract_horeca_contact(self, user, products):
        wanted_products = set(user.getProperty('localfood_wanted_products', []))  # noqa
        if wanted_products.intersection(products):
            return (
                [(_(t), user.getProperty('localfood_{0}'.format(k)))
                 for k, t in self._horeca_contact],
                wanted_products.intersection(products),
            )
