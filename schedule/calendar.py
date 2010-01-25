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


class CS:
	def __init__(self, cs):
		self.cs = cs
		
	def getCalId(self, str):
		s = '/calendar/feeds/'
		str = str[len(s) + str.index(s):]
		return str.split('/')
	
	def getEvents(self, calId, startDate, endDate):
		a = self.getCalId(calId)
		query = gdata.calendar.service.CalendarEventQuery(a[0], a[1], a[2])
		query.start_min = startDate.strftime('%Y-%m-%d')
		query.start_max = endDate.strftime('%Y-%m-%d')
		return self.cs.CalendarQuery(query)

	def createEvent(self,
			title='One-time Tennis with Beth', 
			content='Meet for a quick lesson',
			where='On the courts', 
			start_time=None, end_time=None, recurrence=None, who=None):
		event = gdata.calendar.CalendarEventEntry()
		event.title = atom.Title(text=title)
		event.content = atom.Content(text=content)
		event.where.append(gdata.calendar.Where(value_string=where))
	
		if start_time.__class__ is datetime.datetime:
			start = start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
			end = end_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
		elif start_time is None:
			start = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
			end  = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(time.time() + 3600))
		elif start_time.__class__ is str:
			start = start_time
			end = end_time
		
		if recurrence:
			event.recurrence = gdata.calendar.Recurrence(text=recurrence)
		else:
			event.when.append(gdata.calendar.When(
					start_time=start, end_time=end))
		
		if who:
			event.who.append(gdata.calendar.Who(name=who['name'], email=who['email']))
		return event

	def createCopy(self, e):
		event = gdata.calendar.CalendarEventEntry()
		event.title = atom.Title(text=e.title.text)
		event.content = atom.Content(text=e.content.text)
		for where in e.where:
			event.where.append(gdata.calendar.Where(value_string=where.value_string))
		if e.recurrence and len(e.recurrence.text) > 0:
			event.recurrence = gdata.calendar.Recurrence(text=e.recurrence.text)
		else:
			for when in e.when:
				event.when.append(gdata.calendar.When(
						start_time=when.start_time, end_time=when.end_time))
		return event
		
	def InsertSingleEvent(self,
			calendar,
			title='One-time Tennis with Beth', 
			content='Meet for a quick lesson',
			where='On the courts',
			start_time=None, end_time=None, reccurence=None, who=None):
		event = self.createEvent(title, content, where, start_time, end_time, reccurence, who)
		new_event = self.cs.InsertEvent(event, calendar)
			#'/calendar/feeds/gmc2jrirg1850pg1b102n9e56g@group.calendar.google.com/private/full')
			#'/calendar/feeds/default/allcalendars/full') 
			#calendar) #'/calendar/feeds/default/private/full')
	    
		print 'New single event inserted: %s' % (new_event.id.text,)
		print '\tEvent edit URL: %s' % (new_event.GetEditLink().href,)
		print '\tEvent HTML URL: %s' % (new_event.GetHtmlLink().href,)
		
		return new_event

if __name__ == '__main__':
	__init__()
