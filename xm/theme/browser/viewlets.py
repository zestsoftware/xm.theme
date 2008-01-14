from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

class ProjectHeader(ViewletBase):
    render = ViewPageTemplateFile('project_header.pt')

    def project_title(self):
        try:
            title = self.context.getProject().title
        except AttributeError:
            title = 'eXtremeManagement'
        return title
