from plone.theme.interfaces import IDefaultPloneLayer
from zope.viewlet.interfaces import IViewletManager

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """

class IProjectTabsManager(IViewletManager):
    """A viewlet manager which will be used to display the tabs for
    a project.
    """
