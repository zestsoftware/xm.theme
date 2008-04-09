from datetime import datetime

from zope.interface import implements
from plone.memoize.view import memoize

from interfaces import IEmployeesView

from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.CMFPlone.utils import safe_unicode

from Products.eXtremeManagement.browser.bookings import WeekBookingOverview

from xm.theme import xmMessageFactory as _


class EmployeesView(BrowserView):
    """Return information about the contents of a project."""
    implements(IEmployeesView)

    def __init__(self, context, request, year=None):
        self.context = context
        self.request = request
        portal_url = getToolByName(context, 'portal_url')
        self.portal = portal_url.getPortalObject()
        self.site_url = portal_url()
        self.catalog = getToolByName(context, 'portal_catalog')
        self.mtool = getToolByName(context, 'portal_membership')
        self.now = datetime.now()
        self.month = self.now.month
        self.months = [self.now]
        self.year = self.now.year
        # months is a list of datetime object of the past 12 months counting
        # from now.
        y = self.year
        for x in range(11):
            i = x + 1
            m = self.month - i
            if m <= 0:
                m += 12
                if y == self.year:
                    y -= 1
            self.months.append(datetime(y, m, self.now.day))

    @memoize
    def items(self):
        data = []
        employees = self.get_employees()
        for userid in employees:
            empldict = {}
            memberinfo = self.mtool.getMemberInfo(userid)
            if memberinfo and memberinfo is not None:
                empldict['name'] = memberinfo['fullname']
                # For each month create a list employees in a dict with
                # percentages and a url to the month view.
                results = []
                for m in self.months:
                    view = WeekBookingOverview(aq_inner(self.context),
                                                      self.request,
                                                      year=m.year,
                                                      month=m.month,
                                                      memberid=userid)
                    val = view.main()
                    url = "%s/booking_month?memberid=%s&month=%r" % \
                                                (self.site_url, userid,
                                                m.month)
                    perc_dict = dict(percentage = val['perc_billable'],
                                   url = url)
                    results.append(perc_dict)
                empldict['monthly_percentages'] = results
            data.append(empldict)

        return data

    @memoize
    def month_names(self):
        """ Return a list of translated month names used for the header of the
        table.
        """
        result = []
        for m in self.months:
            month = _(safe_unicode(m.strftime('%B')))
            year = safe_unicode(str(m.year))
            result.append(' '.join([month, year]))
        return result

    @memoize
    def get_employees(self):
        """return a list of userids which have a global role 'Employee'
        assigned.
        """
        employees = []
        acl_users = self.portal.acl_users
        roleman = acl_users.portal_role_manager
        for userid, loginname in roleman.listAssignedPrincipals('Employee'):
            if acl_users.getUser(userid):
                employees.append(userid)
        employees.sort()
        return employees
