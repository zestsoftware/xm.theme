from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.view import memoize

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


TAB_SELECTED = u'selected'
TAB_NORMAL = u'plain'


class XMProjectTabsViewlet(ViewletBase):
    """A view to render the Project Tabs Manager."""

    render = ViewPageTemplateFile('templates/project_tabs_viewlet.pt')


class ProjectTabsBaseViewlet(ViewletBase):
    """Base viewlet for the project tabs."""

    render = ViewPageTemplateFile('templates/project_tab.pt')

    def update(self):
        self.available = self._is_available()
        self.one_item = self._is_single()
        self.more_items = self._is_more()
        self.tab_class = self._get_tab_class()
        self.url = self._get_url()
        self.title = self._get_title()
        self.items = self._get_items()

    @memoize
    def _is_available(self):
        return self._get_project() and (self._is_single() or
                                        self._is_more())

    @memoize
    def _is_single(self):
        return len(self._get_items()) == 1

    @memoize
    def _is_more(self):
        return len(self._get_items()) > 1

    @memoize
    def _get_tab_class(self):
        return TAB_NORMAL

    @memoize
    def _get_url(self):
        return u'#'

    @memoize
    def _get_title(self):
        return u'Example'

    @memoize
    def _get_items(self):
        return []

    @memoize
    def _get_project(self):
        try:
            project = self.context.getProject()
        except AttributeError:
            project = None
        return project

    @memoize
    def _get_iteration(self):
        try:
            iteration = self.context.getIteration()
        except AttributeError:
            iteration = None
        return iteration


class CurrentIterationViewlet(ProjectTabsBaseViewlet):
    """Viewlet for the current iteration tab."""

    @memoize
    def _get_title(self):
        return u'Current'

    @memoize
    def _get_url(self):
        project = self._get_project()
        if not project:
            return None
        if self._is_more():
            return project.absolute_url()
        elif self._is_single():
            items = self._get_items()
            return items[0]['url']
        else:
            return None

    @memoize
    def _get_items(self):
        project = self._get_project()
        selected = self._get_iteration()
        if not project:
            return []
        project_view = project.restrictedTraverse('@@project')
        iterations = project_view.current_iterations()
        for iteration in iterations:
            iteration['id'] = iteration['brain'].getId
            if selected and selected.getId() == iteration['id']:
                iteration['tab_class'] = TAB_SELECTED
            else:
                iteration['tab_class'] = TAB_NORMAL
        return iterations

    @memoize
    def _get_tab_class(self):
        selected = self._get_iteration()
        if not selected:
            return TAB_NORMAL
        items = self._get_items()
        if selected.getId() in [it['brain'].getId for it in items]:
            return TAB_SELECTED
        else:
            return TAB_NORMAL
