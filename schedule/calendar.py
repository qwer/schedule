try:
	from xml.etree import ElementTree
except ImportError:
	from elementtree import ElementTree
import gdata.calendar.service
import gdata.service
import atom.service
import gdata.calendar
import atom

import datetime

class Calendar(gdata.calendar.CalendarListEntry):
	pass

def Calendar_GetEventFeedLink(self):
	for link in self.link:
		if link.rel == 'http://schemas.google.com/gCal/2005#eventFeed':
			return link.href
	return None

def Calendar_GetEventFeed(self):
	return self.calendar_service.GetCalendarEventFeed(self.GetEventFeedLink())

def __init__():
	raise 1123
	
gdata.calendar.CalendarListEntry.GetEventFeedLink = Calendar_GetEventFeedLink
gdata.calendar.CalendarListEntry.GetEventFeed = Calendar_GetEventFeed  

if __name__ == '__main__':
	__init__()
