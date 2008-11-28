from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter
from urllib import quote_plus


class XMProjectHeaderViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/project_header.pt')

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.site_url = self.portal_state.portal_url()
        self.project_title = self._get_project_title()
        self.project_url = self._get_project_url()

    def _get_project(self):
        try:
            project = self.context.getProject()
        except AttributeError:
            project = None
        return project

    def _get_project_title(self):
        project = self._get_project()
        if project is not None:
            return project.title
        else:
            return u'Extreme Management'

    def _get_project_url(self):
        project = self._get_project()
        if project is not None:
            return project.absolute_url()
        else:
            return self.site_url


class XMSearchBoxViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/searchbox.pt')

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        tools = getMultiAdapter((self.context, self.request),
                                        name=u'plone_tools')
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        self.site_url = self.portal_state.portal_url()
        self.checkPermission = tools.membership().checkPermission
        props = getToolByName(self.context, 'portal_properties')
        livesearch = props.site_properties.getProperty('enable_livesearch',
                                                       False)
        if livesearch:
            self.search_input_id = "searchGadget"
        else:
            self.search_input_id = ""

        folder = context_state.folder()
        self.folder_path = '/'.join(folder.getPhysicalPath())


class GoogleSearchViewlet(ViewletBase):

        render = ViewPageTemplateFile('templates/googlesearch.pt')


class XMPersonalBarViewlet(ViewletBase):
    index = ViewPageTemplateFile('templates/personal_bar.pt')

    def update(self):
        super(XMPersonalBarViewlet, self).update()

        context_state = getMultiAdapter((self.context, self.request),
                                         name=u'plone_context_state')
        tools = getMultiAdapter((self.context, self.request),
                                 name=u'plone_tools')
        self.user_actions = context_state.actions().get('user', None)
        plone_utils = getToolByName(self.context, 'plone_utils')
        self.getIconFor = plone_utils.getIconFor
        self.anonymous = self.portal_state.anonymous()
        if not self.anonymous:
            member = self.portal_state.member()
            userid = member.getId()
            self.homelink_url = self.site_url + '/author/' + quote_plus(userid)

            member_info = tools.membership().getMemberInfo(member.getId())
            # member_info is None if there's no Plone user object, as when
            # using OpenID.
            if member_info:
                fullname = member_info.get('fullname', '')
            else:
                fullname = None
            if fullname:
                self.user_name = fullname
            else:
                self.user_name = userid
