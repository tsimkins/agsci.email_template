from Products.Five import BrowserView
from ..content import IEmailTemplateBase
from plone.app.textfield import RichText
from zope.component import getMultiAdapter
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from DateTime import DateTime
from premailer import Premailer
from Products.CMFPlone.utils import safe_unicode
from plone.app.theming.transform import ThemeTransform
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
from zope.component.hooks import getSite
from urlparse import urlparse

class FieldObject(object):

    def __init__(self, field_name, field_title, field_description, field_structure, field_value):
        self.name = field_name
        self.title = field_title
        self.description = field_description
        self.structure = field_structure
        self.value = field_value

class EmailTemplateBaseView(BrowserView):

    @property
    def anonymous(self):
        return self._portal_state.anonymous()

    @property
    def _portal_state(self):
        return getMultiAdapter((self.context, self.request),
                                name=u'plone_portal_state')

    def logged_out(self):
        return self.context.absolute_url().replace('https://', 'http://')

    def current_year(self):
        return DateTime().year()

    def structure(self, field):
        return isinstance(field, (RichText,))

    def fields(self):

        sort_order = ['email_heading', 'email_lead', 'email_callout', 'email_full_body', 'email_left_body', 'email_right_body', 'email_footer', '']

        skip = ['title', 'email_unsubscribe']

        def getSortOrder(x):
            try:
                return sort_order.index(x[0])
            except ValueError:
                return 99999

        for (field_name, field) in sorted(IEmailTemplateBase.namesAndDescriptions(), key=getSortOrder):
            if field_name in skip:
                continue

            v = getattr(self.context, field_name, None)

            if v:
                yield FieldObject(field_name, field.title, field.description, self.structure(field), v)

    def __call__(self):
        if self.anonymous:
            # Get the site path
            site = getSite()
            site_url_data = urlparse(site.absolute_url())
            site_path = site_url_data.path

            # Get the HTML that would normally be returned (before transform)
            html = safe_unicode(self.index())

            # Snag the transform
            transform = ThemeTransform(True, self.request)

            # Transform the original HTML
            transformed_html = transform.transformUnicode(html, 'utf-8').serialize()

            # Get a BeautifulSoup version of the transformed HTML
            soup = BeautifulSoup(transformed_html)

            # Replace the '<link rel="stylesheet" ... />' with the contained CSS in a <style> tag.
            for link in soup.findAll('link'):
                rel = link.get('rel', None)
                if rel == 'stylesheet':
                    href = link.get('href', None)
                    if href:
                        resource_path = str(href[len(site_path)+1:])
                        resource = site.restrictedTraverse(resource_path)
                        resource_data = open(resource.path, 'r').read()
                        style_tag = Tag(soup, 'style', [("type", "text/css")])
                        style_tag.insert(0, resource_data)
                        link.replaceWith(style_tag)

            # Fix the background-image URL in the style email.  Something in
            # Beautiful Soup transforms a 'x=1&y=2' into 'x=1&y;=2', inside a
            # CSS style, so we're fixing that.

            # Iterate through the style elements (hopefully just one) with
            # id='litmus'
            for style in soup.findAll('style', attrs={'id' : 'litmus'}):

                # Iterate through the contents of the element and replace the
                # text containing ';=' with a plain '='.  This also introduces
                # an encoded '&amp;'.  So, replace that with the token '__AMPERSAND__'
                # and then re-replace that after the HTML is rendered.

                for _i in style.contents:
                    if isinstance(_i, NavigableString):
                        _f = unicode(_i).encode('utf-8')
                        _t = _f.replace(';=', '=').replace('&', '__AMPERSAND__')
                        _i.replaceWith(NavigableString(_t))

                # Get rid of id
                del style['id']

            # After updating the HTML via BeautifulSoup, turn it back into HTML
            transformed_html = repr(soup)

            # Replace our token with a non-encoded amperand.
            transformed_html = transformed_html.replace('__AMPERSAND__', '&')

            # Premailer transform
            premailer = Premailer(safe_unicode(transformed_html), strip_important=False)
            transformed_html = premailer.transform()

            # Return mailified HTML
            return transformed_html
        else:
            return super(EmailTemplateBaseView, self).__call__()
