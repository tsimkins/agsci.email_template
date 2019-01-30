from plone.autoform import directives as form
from plone.supermodel import model
from plone.dexterity.content import Container
from z3c.form.interfaces import IAddForm, IEditForm
from zope import schema
from plone.app.textfield import RichText
from zope.interface import invariant, Invalid
from plone.app.contenttypes.behaviors.leadimage import ILeadImage

from agsci.email_template import EmailTemplateMessageFactory as _

def is_non_blank_string(v):
    if isinstance(v, (unicode, str)):
        return len(v.strip()) > 0

    return False

# Parent schema class for all products, and product contained content
class IEmailTemplateBase(model.Schema, ILeadImage):

    form.order_after(image="email_lead")
    form.order_after(image_caption="image")
    form.order_after(email_image_size="image_caption")

    title = schema.TextLine(
        title=_(u'Title'),
        required=True
    )

    email_heading = schema.TextLine(
        title=_(u'label_title', default=u'Heading'),
        required=True
    )

    email_lead = RichText(
        title=u"Lead text",
        required=True
    )

    email_callout = RichText(
        title=u"Callout",
        required=False
    )

    email_full_body = RichText(
        title=u"Full Width Body Text",
        required=False
    )

    email_left_column = RichText(
        title=u"Left Column Text",
        required=False
    )

    email_right_column = RichText(
        title=u"Right Column Text",
        required=False
    )

    email_footer = RichText(
        title=u"Footer Text",
        required=False
    )

    email_unsubscribe = schema.TextLine(
        title=u"Unsubscribe Link",
        required=True
    )

    email_tracking_enable = schema.Bool(
        title=u"Enable email tracking?",
        default=True,
    )

    email_tracking_base_url = schema.TextLine(
        title=u"Email tracking base URL",
        required=False
    )

    email_tracking_custom_code = schema.TextLine(
        title=u"Email tracking custom code",
        required=False
    )

    email_image_size = schema.Choice(
        title=_(u"Image Width"),
        values=(u"Full", u"Half"),
        required=True,
        default=u"Full",
    )

    @invariant
    def email_tracking(data):
        if data.email_tracking_enable:
            email_tracking_base_url = is_non_blank_string(data.email_tracking_base_url)
            email_tracking_custom_code = is_non_blank_string(data.email_tracking_custom_code)

            if not (email_tracking_base_url and email_tracking_custom_code):
                raise Invalid('Base URL and Custom Code are required if email tracking is enabled.')


class EmailTemplateBase(Container):
    pass

class IEmailTemplateBaseCollege(IEmailTemplateBase):
    pass

class IEmailTemplateBaseExtension(IEmailTemplateBase):
    pass

class EmailTemplateBaseExtension(EmailTemplateBase):
    pass

class EmailTemplateBaseCollege(EmailTemplateBase):
    pass

class IEmailTemplateInternalExtension(IEmailTemplateBaseExtension):
    pass

class EmailTemplateInternalExtension(EmailTemplateBaseExtension):
    pass