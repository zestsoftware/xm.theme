from Acquisition import aq_inner
from Acquisition import aq_chain

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


class ProjectTabsBaseViewlet(ViewletBase):
    """Base viewlet for the project tabs."""

    render = ViewPageTemplateFile('templates/project_tab.pt')

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
        return self._get_project() and (self._is_single() or
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
        return TAB_NORMAL

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
        project = self._get_project()
        if not project:
            return None
        if self._is_more():
            return project.absolute_url()
        elif self._is_single():
            items = self._get_items()
            return items[0].get('url', None)
        else:
            return None

    @memoize
    def _get_project(self):
        """Return the project of this context."""
        try:
            project = self.context.getProject()
        except AttributeError:
            project = None
        return project

    @memoize
    def _get_iteration(self):
        """Return the iteration of this context."""
        try:
            iteration = self.context.getIteration()
        except AttributeError:
            iteration = None
        return iteration

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
        project = self._get_project()
        if not project:
            return []
        project_view = project.restrictedTraverse('@@project')
        return project_view.current_iterations()

    @memoize
    def _get_items(self):
        """Return the items for the tab."""
        selected = self._get_iteration()
        iterations = self._iterations()
        for iteration in iterations:
            iteration['id'] = iteration['brain'].getId
            if selected and selected.getId() == iteration['id']:
                iteration['tab_class'] = TAB_SELECTED
            else:
                iteration['tab_class'] = TAB_NORMAL
        return iterations

    @memoize
    def _get_tab_class(self):
        """Return the class for the tab."""
        selected = self._get_iteration()
        if not selected:
            return TAB_NORMAL
        items = self._get_items()
        if selected.getId() in [it['brain'].getId for it in items]:
            return TAB_SELECTED
        else:
            return TAB_NORMAL


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
        project = self._get_project()
        if not project:
            return []
        project_view = project.restrictedTraverse('@@project')
        return project_view.open_iterations()


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
        project = self._get_project()
        if not project:
            return []
        project_view = project.restrictedTraverse('@@project')
        return project_view.finished_iterations()


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
        project = self._get_project()
        selected_id = self._get_selected_offer()
        if not project:
            return []
        project_view = project.restrictedTraverse('@@project')
        offers = project_view.offers()
        if offers is None:
            return []
        for offer in offers:
            offer['id'] = offer['brain'].getId
            if selected_id == offer['id']:
                offer['tab_class'] = TAB_SELECTED
            else:
                offer['tab_class'] = TAB_NORMAL
        return offers

    @memoize
    def _get_tab_class(self):
        """Return the class for the tab."""
        selected_id = self._get_selected_offer()
        items = self._get_items()
        if selected_id in [offer['id'] for offer in items]:
            return TAB_SELECTED
        else:
            return TAB_NORMAL


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
        # get the project
        context = aq_inner(self.context)
        project = self._get_project()
        if not project:
            return []
        # get the types which need a /view url
        portal_props = getToolByName(self, 'portal_properties')
        view_types = portal_props['site_properties'].typesUseViewActionInListings
        # get the attachments
        cfilter = dict(portal_type=('Iteration', 'Offer',
                                    'PoiTracker'))
        exclude_ids = [item.id for item in
                       project.getFolderContents(cfilter)]
        all_brains = project.getFolderContents()
        attachmentbrains = [brain for brain in all_brains
                  if brain.id not in exclude_ids]
        if not attachmentbrains:
            return []
        # setup a dict with the necessary info
        attachments = []
        for brain in attachmentbrains:
            selected = False
            url = brain.getURL()
            tab_class = TAB_NORMAL
            if url in context.absolute_url():
                tab_class = TAB_SELECTED
                selected = True
            if brain.portal_type in view_types:
                url += '/view'
            attachments.append(dict(id = brain.getId,
                                    title = brain.Title,
                                    url = url,
                                    tab_class = tab_class,
                                    selected = selected,
                                    ))
        return attachments

    @memoize
    def _get_tab_class(self):
        """Return the class for the tab."""
        value = TAB_NORMAL
        items = self._get_items()
        for item in items:
            if item['selected']:
                value = TAB_SELECTED
        return value


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
        context = aq_inner(self.context)
        project = self._get_project()
        if not project:
            return []
        cfilter = dict(portal_type=('PoiTracker'))
        tracker_brains = project.getFolderContents(cfilter)
        trackers = []
        for brain in tracker_brains:
            selected = False
            url = brain.getURL()
            tab_class = TAB_NORMAL
            if url in context.absolute_url():
                tab_class = TAB_SELECTED
                selected = True
            trackers.append(dict(id = brain.getId,
                                 title = brain.Title,
                                 url = url,
                                 tab_class = tab_class,
                                 selected = selected,
                                 ))
        return trackers

    @memoize
    def _get_tab_class(self):
        """Return the class for the tab."""
        value = TAB_NORMAL
        items = self._get_items()
        for item in items:
            if item['selected']:
                value = TAB_SELECTED
        return value
