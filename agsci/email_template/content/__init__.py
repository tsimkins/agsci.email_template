from plone.autoform import directives as form
from plone.supermodel import model
from plone.dexterity.content import Container
from z3c.form.interfaces import IAddForm, IEditForm
from zope import schema
from plone.app.textfield import RichText



from agsci.email_template import EmailTemplateMessageFactory as _

# Parent schema class for all products, and product contained content
class IEmailTemplateBase(model.Schema):

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

class EmailTemplateBase(Container):
    pass