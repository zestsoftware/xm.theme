from zope.component import getMultiAdapter
from plone.app.layout.viewlets.common import ViewletBase

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class XMProjectTabsViewlet(ViewletBase):
    """A view to render the Project Tabs Manager."""

    render = ViewPageTemplateFile('templates/project_tabs_viewlet.pt')


class ProjectTabsBaseViewlet(ViewletBase):
    """Base viewlet for the project tabs."""

    render = ViewPageTemplateFile('templates/project_tab.pt')

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        self.available = self._is_available()
        self.tab_class = self._get_tab_class()
        self.url = self._get_url()
        self.title = self._get_title()

    def _is_available(self):
        return False

    def _get_tab_class(self):
        return u'plain'

    def _get_url(self):
        return u'#'

    def _get_title(self):
        return u'Example'


class CurrentIterationViewlet(ProjectTabsBaseViewlet):
    """Viewlet for the current iteration tab."""

    def _is_available(self):
        return True
