from calendar import Calendar
from gdata.calendar.service import CalendarService
import datetime
import time

try:
	from xml.etree import ElementTree
except ImportError:
	from elementtree import ElementTree
import gdata.calendar.service
import gdata.service
import atom.service
import gdata.calendar
import atom

from google.appengine.ext import db
from models import Group, User
from calendar import CS

class Sync:
	def __init__(self, calendarService):
		self.cs = CS(calendarService)
	
	def sync(self, user):
		start = datetime.date.today()
		start -= datetime.timedelta(days=start.weekday())
		end = start + datetime.timedelta(days=7)
		 
		eventFeed = self.cs.getEvents(user.calendarId, start, end)
		whos = {}
		events1 = {}
		s = ''
		for event in eventFeed.entry:
			#s += event.title.text + '<br/>'
			for who in event.who:
				if who.name not in whos:
					g = Group.getByName(who.name)
					whos[who.name] = g
					if g:
						events1[g] = []
				if whos[who.name]:
					events1[whos[who.name]].append(event)
		
		events2 = {}
		feeds = {}
		for who in whos:
			group = whos[who]
			if group:
				#try:
				feeds[group] = self.cs.getEvents(
						group.calendarId, start, end)
				for event in feeds[group].entry:
					for who2 in event.who:
						if who2.name == user.name:
							if group not in events2:
								events2[group] = []
							events2[group].append(event)
				#except:
				#	events2[group] = None
			
			s += who + ': ' + (whos[who].name if whos[who] else 'None') + '<br/>'
		
		s += '<br/>'
		for g in events2:
			if events2[g]:
				s += '<ul>' + g.name
				for e in events2[g]:
					s += '<li>' + e.title.text + '</li>'
				s += '</ul>'
			else:
				s += g.name + ': null<br/>'
		
		for name in whos:
			s += '<p>' + name + ': ' + (whos[name].name if whos[name] else 'null') + '</p>'
		
		for g in events1:
			s += g.name + '<br/>'
			for e1 in events1[g]:
				s += '' + e1.title.text + '</br>'
		
		for g in events2:
			feeds[g] = gdata.calendar.CalendarEventFeed()
			if not events2[g]:
				continue
			for e2 in events2[g]:
				e2.batch_id = gdata.BatchId(text='delete-request')
				feeds[g].AddDelete(entry=e2)
				s += '~'
		
		for g in events1:
			#feeds[g] = gdata.calendar.CalendarEventFeed()
			if not events1[g] or g not in feeds: 
				continue
			for e1 in events1[g]:
				s += '+'
				#self.cs.InsertSingleEvent(g.calendarId,
				#		title=e1.title.text,
				#		start_time=e1.when[0].start_time,
				#		end_time=e1.when[0].end_time,
				#		who={'name': user.name, 'email': user.account.email()})
				#continue
				e2 = self.cs.createCopy(e1)
				e2.who.append(gdata.calendar.Who(name=user.name, email=user.account.email()))
				e2.batch_id = gdata.BatchId(text='insert-request')
				feeds[g].AddInsert(entry=e2)
				#self.cs.cs.InsertEvent(e2, g.calendarId)
		
		for g in feeds:	
			s += '*'
			feed = self.cs.cs.ExecuteBatch(feeds[g], g.calendarId + '/batch')
							#gdata.calendar.service.DEFAULT_BATCH_URL)
			for e2 in feed.entry:
				s += str(e2.title.text) + ' ' + str(e2.batch_id) + ' <br/>'
					#' ' + e2.batch_status.reason 
		#for event in
		#for when in event.when:
		return s
		


