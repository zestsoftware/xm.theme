from Acquisition import aq_inner
from Acquisition import aq_chain
from DateTime import DateTime

from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.view import memoize

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from xm.theme import xmMessageFactory as _
from Products.eXtremeManagement.interfaces import IXMOffer

TAB_SELECTED = u'selected'
TAB_NORMAL = u''


class XMProjectTabsViewlet(ViewletBase):
    """A view to render the Project Tabs Manager."""

    render = ViewPageTemplateFile('templates/project_tabs_viewlet.pt')

    @memoize
    def get_project(self):
        """Return the project of this context.
        Also set a cookie with the project id. This can be used to redirect
        after logging in.
        """
        try:
            project = aq_inner(self.context).getProject()
        except AttributeError:
            project = None
        expires = (DateTime() + 90).toZone('GMT').rfc822()
        self.request.response.setCookie('last_project',
                                        project.getId(),
                                        path = '/',
                                        expires = expires)
        return project

    @memoize
    def get_iteration(self):
        """Return the iteration of this context."""
        try:
            iteration = aq_inner(self.context).getIteration()
        except AttributeError:
            iteration = None
        return iteration

    @memoize
    def get_contents(self):
        """Get the contents of the project in a single structure."""
        project = self.get_project()
        if not project:
            return {}
        contents = {'Iteration': [],
                    'Offer': [],
                    'PoiTracker': [],
                    'Attachment': [],
                    }
        portal_props = getToolByName(self, 'portal_properties')
        site_props = portal_props['site_properties']
        view_types = site_props.typesUseViewActionInListings
        project_contents = project.getFolderContents()
        for brain in project_contents:
            url = brain.getURL()
            if brain.portal_type in view_types:
                url += '/view'
            item = dict(id = brain.getId,
                        title = brain.Title,
                        state = brain.review_state,
                        url = url,
                        raw_url = brain.getURL(),
                        tab_class = TAB_NORMAL,
                        selected = False,
                       )
            if brain.portal_type not in contents.keys():
                contents['Attachment'].append(item)
            else:
                contents[brain.portal_type].append(item)
        return contents


class ProjectTabsBaseViewlet(ViewletBase):
    """Base viewlet for the project tabs."""

    render = ViewPageTemplateFile('templates/project_tab.pt')

    def __init__(self, context, request, view, manager):
        super(ProjectTabsBaseViewlet, self).__init__(context, request,
                                                     view, manager)
        self.project = view.get_project()
        self.iteration = view.get_iteration()
        self.contents = view.get_contents()

    def update(self):
        """Update method for the viewlet."""
        self.available = self._is_available()
        self.one_item = self._is_single()
        self.more_items = self._is_more()
        self.tab_class = self._get_tab_class()
        self.url = self._get_url()
        self.title = self._get_title()
        self.description = self._get_description()
        self.items = self._get_items()

    @memoize
    def _is_available(self):
        """Return whether the viewlet/tab is available."""
        return self.project and (self._is_single() or
                                 self._is_more())

    @memoize
    def _is_single(self):
        """Return if there is just a single item."""
        return len(self._get_items()) == 1

    @memoize
    def _is_more(self):
        """Return if there are more than one items."""
        return len(self._get_items()) > 1

    @memoize
    def _get_tab_class(self):
        """Return the class for the tab."""
        value = TAB_NORMAL
        items = self._get_items()
        for item in items:
            if item['selected']:
                value = TAB_SELECTED
        return value

    @memoize
    def _get_title(self):
        """Return the title of the tab."""
        return _(u'Example')

    @memoize
    def _get_description(self):
        """Return a description of the tab."""
        return _(u'Example tab')

    @memoize
    def _get_url(self):
        """Return the url for the tab."""
        if not self.project:
            return None
        if self._is_more():
            return self.project.absolute_url()
        elif self._is_single():
            items = self._get_items()
            return items[0].get('url', None)
        else:
            return None

    @memoize
    def _get_items(self):
        """Return the items for the tab."""
        return []


class CurrentIterationsViewlet(ProjectTabsBaseViewlet):
    """Viewlet for the current iteration tab."""

    @memoize
    def _get_title(self):
        """Return the title of the tab."""
        return _(u'Current')

    @memoize
    def _description(self):
        """Helper function which returns the default description of the tab."""
        return _(u'Current iterations')

    @memoize
    def _get_description(self):
        """Return a description of the tab."""
        if self._is_more():
            return self._description()
        elif self._is_single():
            items = self._get_items()
            return u'"%s"' % items[0]['title']
        else:
            return u''

    @memoize
    def _iterations(self):
        """Helper function to retrieve the relevant iterations."""
        iterations = []
        for item in self.contents.get('Iteration', []):
            if item.get('state', None) in ['in-progress']:
                iterations.append(item)
        return iterations

    @memoize
    def _get_items(self):
        """Return the items for the tab."""
        selected = self.iteration
        iterations = self._iterations()
        for iteration in iterations:
            if selected and selected.getId() == iteration['id']:
                iteration['tab_class'] = TAB_SELECTED
                iteration['selected'] = True
        return iterations


class OpenIterationsViewlet(CurrentIterationsViewlet):
    """Viewlet for the open iterations tab."""

    @memoize
    def _get_title(self):
        """Return the title of the tab."""
        return _(u'Open')

    @memoize
    def _description(self):
        """Helper function which returns the default description of the tab."""
        return _(u'Open iterations')

    @memoize
    def _iterations(self):
        """Helper function to retrieve the relevant iterations."""
        iterations = []
        for item in self.contents.get('Iteration', []):
            if item.get('state', None) in ['new']:
                iterations.append(item)
        return iterations


class ClosedIterationsViewlet(CurrentIterationsViewlet):
    """Viewlet for the closed iterations tab."""

    @memoize
    def _get_title(self):
        """Return the title of the tab."""
        return _(u'Closed')

    @memoize
    def _description(self):
        """Helper function which returns the default description of the tab."""
        return _(u'Closed iterations')

    @memoize
    def _iterations(self):
        """Helper function to retrieve the relevant iterations."""
        iterations = []
        for item in self.contents.get('Iteration', []):
            if item.get('state', None) in ['completed', 'invoiced']:
                iterations.append(item)
        return iterations


class OffersViewlet(CurrentIterationsViewlet):
    """Viewlet for the offers tab."""

    @memoize
    def _get_title(self):
        """Return the title of the tab."""
        if self._is_more():
            return _(u'Offers')
        elif self._is_single():
            return _(u'Offer')
        else:
            return u''

    @memoize
    def _description(self):
        """Helper function which returns the default description of the tab."""
        return _(u'Offers')

    @memoize
    def _get_selected_offer(self):
        """Helper function to determine the selected offer."""
        context = aq_inner(self.context)
        chain = aq_chain(context)
        for item in chain:
            if IXMOffer.providedBy(item):
                return item.getId()
        return None

    @memoize
    def _get_items(self):
        """Return the items for the tab."""
        offers = self.contents.get('Offer', [])
        selected_id = self._get_selected_offer()
        for offer in offers:
            if selected_id == offer['id']:
                offer['tab_class'] = TAB_SELECTED
                offer['selected'] = True
        return offers


class AttachmentsViewlet(ProjectTabsBaseViewlet):
    """Viewlet for the attachments tab."""

    @memoize
    def _get_title(self):
        """Return the title of the tab."""
        if self._is_more():
            return _(u'Attachments')
        elif self._is_single():
            return _(u'Attachment')
        else:
            return u''

    @memoize
    def _get_description(self):
        """Return a description of the tab."""
        if self._is_more():
            return _(u'Attachments')
        elif self._is_single():
            items = self._get_items()
            return u'"%s"' % items[0]['title']
        else:
            return u''

    @memoize
    def _get_items(self):
        """Return the items for the tab."""
        attachments = self.contents.get('Attachment', [])
        current_url = aq_inner(self.context).absolute_url()
        for attachment in attachments:
            if attachment['raw_url'] in current_url:
                attachment['tab_class'] = TAB_SELECTED
                attachment['selected'] = True
        return attachments


class IssueTrackerViewlet(ProjectTabsBaseViewlet):
    """Viewlet for an issue tracker."""

    @memoize
    def _get_title(self):
        """Return the title of the tab."""
        return _(u'Issues')

    @memoize
    def _get_description(self):
        """Return a description of the tab."""
        if self._is_more():
            return _(u'Issue trackers')
        elif self._is_single():
            return _(u'Issue tracker')
        else:
            return u''

    @memoize
    def _get_items(self):
        """Return the items for the tab."""
        trackers = self.contents.get('PoiTracker', [])
        current_url = aq_inner(self.context).absolute_url()
        for tracker in trackers:
            if tracker['raw_url'] in current_url:
                tracker['tab_class'] = TAB_SELECTED
                tracker['selected'] = True
        return trackers
