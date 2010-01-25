from django.http import HttpResponse, Http404
from django.template import Template, Context, RequestContext
from django.template.loader import get_template
from django.shortcuts import render_to_response, redirect
from django.utils import simplejson
from django import forms
from pickle import dumps
from calendar import Calendar
from gdata.calendar.service import CalendarService
#from calendar import calendar
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


from google.appengine.api import users
from google.appengine.ext import db

from models import Group, User, SystemAccount
import calendar
from sync import Sync
from calendar import CS
from urlparse import parse_qsl, parse_qs

def get_auth_sub_url(request):
	next = 'http://%s/authsub/?url=%s' % (request.get_host(), request.get_full_path()) #META['SERVER_NAME']
	scope = 'http://www.google.com/calendar/feeds/'
	secure = False
	session = True
	calendar_service = gdata.calendar.service.CalendarService()
	return calendar_service.GenerateAuthSubURL(next, scope, secure, session);

def index(request):
	user = users.get_current_user()
	if user:
		user_name = user.nickname()
		is_admin = users.is_current_user_admin()
		logout_url = users.create_logout_url('/')
		return render_to_response('index.html', 
			context_instance=RequestContext(request))
			#locals())
	else:
		return redirect(users.create_login_url('/'))

def cal(request):
	if 'logout' in request.GET:
		del request.session['authsub_token']
	if 'authsub_token' not in request.session:
		authSubUrl = get_auth_sub_url(request)
		return redirect(authSubUrl.__str__())
	return HttpResponse("Ok")

def createCalendar(calendar_service, title, hidden=False, 
			summary='', where='', color=None, tz=None):
	calendar = gdata.calendar.CalendarListEntry()
	calendar.title = atom.Title(text=title)
	calendar.summary = atom.Summary(text=summary)
	calendar.where = gdata.calendar.Where(text=where, value_string=where)
	if color:
		calendar.color = gdata.calendar.Color(value=color)
	if tz:
		calendar.timezone = gdata.calendar.Timezone(value=tz)
	calendar.hidden = gdata.calendar.Hidden(value='true' if hidden else 'false')
	new_calendar = calendar_service.InsertCalendar(new_calendar=calendar)
	return new_calendar

def getTime(timestr):
	date = datetime.datetime.strptime(timestr[0:19], '%Y-%m-%dT%H:%M:%S')
	if len(timestr) <= 24:
		return date
	seconds = 3600 * int(timestr[24:26]) + 60 * int(timestr[27:29])
	if timestr[23] == '+':
		return date - datetime.timedelta(0, seconds)
	else:
		return date + datetime.timedelta(0, seconds)


def auth(request):
	if 'authsub_token' not in request.session:
		authSubUrl = get_auth_sub_url(request)
		return redirect(authSubUrl.__str__())
	else:
		return request.session['authsub_token']
	
def authsub(request):
	calendar_service = gdata.calendar.service.CalendarService()
	if "authsub_token" in request.session:
		calendar_service.SetAuthSubToken(request.session["authsub_token"])
		#return HttpResponse("token " + request.session["authsub_token"])
	else:
		url = request.build_absolute_uri()
		token = gdata.auth.extract_auth_sub_token_from_url(url)
		calendar_service.SetAuthSubToken(token)
		calendar_service.UpgradeToSessionToken()
		request.session["authsub_token"] = calendar_service.GetAuthSubToken()
		#return HttpResponse("Ok: token " + request.session["authsub_token"])
	return redirect(request.REQUEST['url'])
	
	#for i in range(1, 10):
	#	create_calendar(calendar_service)
	calendar = calendar_service.GetCalendarListFeed().entry[1]
	calendar.calendar_service = calendar_service
	
	feed = calendar_service.GetCalendarEventFeed(calendar.GetEventFeedLink())
	feed = calendar.GetEventFeed()
	#	'/calendar/feeds/default/owncalendars/full/a63fvb48%40gmail.com')
	#	'/calendar/feeds/default/allcalendars/full/gmc2jrirg1850pg1b102n9e56g%40group.calendar.google.com')
	#feed = calendar_service.GetCalendarListFeed()
	#evt = getTime(feed.entry[1].when[0].start_time)
	#uri = feed.entry[0].GetEditLink().href
	event = None#uri
	#feed = calendar_service.GetCalendarEventFeed(uri)
	return render_to_response('authsub.html', { 'feed': feed, 'event': event })

def getAppUser(user=None):
	if not user:
		user = users.get_current_user()
	gql = User.all().filter('account =', user)
	for u in gql.fetch(1):
		return u
	return None

def getCalendarService2(request, sa):
	cs = gdata.calendar.service.CalendarService()
	if 'auth_token' in request.session:
		cs.SetAuthSubToken(request.session['auth_token'])
		return cs
	
	cs.email = sa.email
	cs.password = sa.password
	cs.source = 'Google-Calendar_Python_Sample-1.0' # ???
	try:
		cs.ProgrammaticLogin()
		request.session["auth_token"] = cs.GetAuthSubToken()
		return cs
	except Exception, e:
		raise e
		return None
	
def calendars(request):
	if not 'id' in request.REQUEST:
		return redirect('/')
	id = request.REQUEST['id']
	user = getAppUser()
	user.calendarId = id if id.strip().__len__() > 0 else None
	user.put()
	return JsonResponse("Ok")
	
def calendar(request):
	user = getAppUser()
	sa = getSystemAccount()
	if not user or not sa:
		return redirect('/')
	
	if 'authsub_token' not in request.session:
		authSubUrl = get_auth_sub_url(request)
		return redirect(authSubUrl.__str__())
	cs = getCalendarService(request)
	if not cs:
		return redirect('/')
	
	if not user.calendarId:
		feed = cs.GetCalendarListFeed()
		calendars = []
		for e in feed.entry:
			c = {}
			c['id'] = str(e.GetEventFeedLink()) #str(e.GetEditLink().href)
			c['name'] = str(e.title.text)
			calendars.append(c)
		#return HttpResponse(simplejson.dumps(calendars))
	else:
		calendars = None
	"""else:
		try:
			cs = getCalendarService2(request, sa)
		except Exception as e:
			return redirect('/' + e.__str__())
	"""
	groups = getGroups(None)
	groups_json = simplejson.dumps(groups)
	return render_to_response('calendar.html',
		{'groups': groups, 'groups_json': groups_json, 
		 'calendars': simplejson.dumps(calendars)},
			context_instance=RequestContext(request))

def sync(request):
	cs = getCalendarService(request)
	user = getAppUser()
	return HttpResponse(Sync(cs).sync(user))

def makeTime(h=0, m=0, time=None):
	if time:
		h = time.hour
		m = time.minute
	return { 'hours': h, 'minutes': m }
	
def makeDate(y=1, m=1, d=1, date=None):
	if date:
		y = date.year
		m = date.month
		d = date.day
	return { 'year': y, 'month': m, 'day': d }
	
def events(request):
	times = []
	t1 = 8 * 60
	t2 = t1 + 95
	for i in range(0, 10):
		times.append({
			'start': makeTime(t1 / 60, t1 % 60),
			'end':   makeTime(t2 / 60, t2 % 60) });
		t1 += 105
		t2 += 105
		
	d = datetime.date.today()
	d -= datetime.timedelta(days=d.weekday())
	dates = []
	for i in range(0, 7):
		dates.append({ 'year': d.year, 'month': d.month, 'day': d.day }) 
		d += datetime.timedelta(days=1)
	
	cs = getCalendarService(request)
	if 'html' in request.REQUEST:
		del request.REQUEST['html']
	events = getEventsForRequest(request)
	return JsonResponse({ 
		'places': 'L1 L2 L3 L4 478 479',
		'times'	: times,
		'dates'	: dates,
		'events': events
	})

def getEventsForRequest(request):
	user = getAppUser()
	if not user or not user.calendarId:
		return JsonResponse(None, 400)
	
	r = GetParams(request)
	try:
		if 'start' in r:
			startDate = datetime.datetime.strptime(r['start'], '%Y-%m-%d')
		else:
			startDate = datetime.datetime.now()
			startDate -= datetime.timedelta(startDate.date().weekday())
		
		if 'end' in r:
			endDate = datetime.datetime.strptime(r['end'], '%Y-%m-%d')
		else:
			endDate = startDate + datetime.timedelta(days=7)
	except Exception, e:
		return HttpResponse(str(e))
	
	calendarService = getCalendarService(request)
	feed = CS(calendarService).getEvents(user.calendarId, startDate, endDate)
	if 'html' in r:	 
		s = ''
		for i, event in enumerate(feed.entry):
			s += '\t%s. %s\n' % (i, event.title.text,)
			for when in event.when:
				s += '\t\tStart time: %s\n' % when.start_time
				s += '\t\tEnd time:   %s\n' % when.end_time
			s += '\t\tId: %s\n' % event.id.text
			s += '\t\tWhere: %s\n' % str(event.where[0])
			#for p in event.__dict__:
			#	s += '\t\t%s : %s %s\n\n' % (p, str(event.__dict__[p]), event.__dict__[p].__class__)
				#if p == 'where':
				#	for pp in event.__dict__[p].__dict__:
				#		s += '\t\t\t%s : %s\n\n' % (pp, str(event.__dict__[p].__dict__[pp]),)
			if event.original_event:
				s += '\t\tOriginal: %s\n' % event.original_event.id 
		return s
	else:
		events = []
		for event in feed.entry:
			for when in event.when:
				e = {}
				e['name'] = event.title.text
				e['when'] = convertWhen(when)
				e['where'] = event.where[0].value_string
				e['id'] = event.id.text
				e['status'] = event.event_status.value
				if event.original_event:
					e['orig_id'] = event.original_event.id
				events.append(e)
		return events

def events2(request):
	e = getEventsForRequest(request)
	if type(e) is str:
		return HttpResponse(e)
	else:
		return JsonResponse(e)
	
def convertWhen(when):
	start = getTime(when.start_time)
	end = getTime(when.end_time) 
	return { 'start' : { 'date' : makeDate(date=start.date()),
						 'time' : makeTime(time=start) },
			 'end'   : { 'date' : makeDate(date=end.date()),
						 'time' : makeTime(time=end) } }


def JsonResponse(object, status=200):
	return HttpResponse(simplejson.dumps(object),
			#mimetype="application/json",
			status=status)

class DateTime:
	def __init__(self, date, hour, minute):
		self.date = date
		self.hour = hour
		self.minute = minute
		
	def __str__(self):
		time.strftime(self.date.isoformat() + 
				'T%d:%d:00.000Z' % (hour, minute), time.gmtime())

def nth_index(str, sub, n):
	i = 0
	for a in range(0, n):
		i = str.find(sub, i) + 1
		#if i < 0: 
		#	return -1
	return i - 1

def getCalendarService(request):
	calendarService = gdata.calendar.service.CalendarService()
	calendarService.SetAuthSubToken(request.session["authsub_token"])
	return calendarService

def event(request):
	user = getAppUser()
	if not user or not user.calendarId:
		return JsonResponse(None, 400)
	
	if request.method == 'GET':
		return event_get(request, user)
	if request.method == 'PUT':
		pass
	return JsonResponse(request.method)

def parseTimes(s):
	i = nth_index(s, "-", 3)
	start = datetime.datetime.strptime(s[0:i], '%Y-%m-%d  %H:%M')
	end = datetime.datetime.strptime(s[i + 1:], '%H:%M') 
	end = start.replace(hour=end.hour, minute=end.minute)
	#start = start.strftime('%Y-%m-%dT%H:%M:%S.000Z')
	#end   = end.strftime('%Y-%m-%dT%H:%M:%S.000Z')
	return (start, end,)

#def insertEvent(cs, calendarId, name, content, where, when, rec, who):
#	InsertSingleEvent(cs, calendarId, name, content, where, when[0], when[1], rec, who)
	
def addEvent(user, cs, name, where, when, who, repeat):
	calendars = []
	if who:
		try:
			key = db.Key(who)
			group = Group.get(key)
		except:
			return JsonResponse({}, 404)
		gg = group.getAllChildren()
		#gg.append(group)
		for g in gg:
			if g.calendarId and len(g.calendarId) > 0 and g.type != 'user':
				calendars.append(g.calendarId)
	#try:
	calendars.append(user.calendarId)
	#return JsonResponse(calendars)
	#event = InsertSingleEvent(calendarService,
	#		user.calendarId, name, '', where, when[0], when[1])
	cs2 = CS(cs)
	for cal in calendars:
		event = cs2.InsertSingleEvent(cal, name, '',
				where, when[0], when[1], reccurence(when, repeat), 
				{	'name': user.name if cal != user.calendarId else group.name, 
					'email': getSystemAccount().email 
				})
	#except Exception, err:
	#	return JsonResponse(cal + ' ' + err.__str__())
	
	return JsonResponse({ 'id': event.id.text })

def reccurence(time, repeat):
	if repeat == '0':
		return None
	if repeat == '7':
		rrule = 'RRULE:FREQ=WEEKLY'
	elif repeat == '14':
		rrule = 'RRULE:FREQ=WEEKLY;INTERVAL=2'
	else:
		return None
	
	return ('DTSTART:%s\r\n' +
		    'DTEND:%s\r\n' +
			 rrule) % (	time[0].strftime('%Y%m%dT%H%M%S'), 
						time[1].strftime('%Y%m%dT%H%M%S'),)
	

def event_get(request, user):
	# XXX errors
	r = GetParams(request)
	name   = r['name']
	where  = r['where']
	when   = r['when']
	who    = r['who']
	repeat = r['repeat']
	times = parseTimes(when)
	event = None
	#try:
	calendarService = getCalendarService(request)
	return addEvent(user, calendarService, name, where, times, who, repeat)

	

def groups(request, id=None):
	user = users.get_current_user()
	if (not user or not users.is_current_user_admin()):
		return redirect('/')

	if (request.method == 'GET'):
		return groups_get(request, id)
	if (request.method == 'POST'):
		return groups_post(request)
	if (request.method == 'PUT'):
		return groups_put(request)
	
	return render_to_response('groups.html',context_instance=RequestContext(request))

def getGroups(id):
	query = Group.all()
	if id:
		query = query.filter('parentGroup =', db.Key(id)) # XXX exceptions
	query.order('name')
	groups = []
	for g in query.fetch(1000):
		gg = g.json()
		try:
			gg['parent'] = g.parentGroup.key().__str__() if g.parentGroup else None
		except Exception:
			continue
		groups.append(gg)
	return groups

def groups_get(request, id):
	#cleanGroups()
	groups = getGroups(id)
	if id:
		return JsonResponse(groups)
	
	groups_json = simplejson.dumps(groups)
	return render_to_response('groups.html',
		{'groups': groups, 'groups_json': groups_json},
		context_instance=RequestContext(request))

def groups_post(request):
	name = request.REQUEST['name']
	parentId = request.REQUEST['id']
	type = request.REQUEST['type'] if ('type' in request.REQUEST) else 'group'
	# XXX errors
	#parentGroupQuery = Group.gql('WHERE __key__ = :1', parentId)
	if (parentId == None or parentId.__len__() == 0):
		key = None
	else:
		key = db.Key(parentId)
	if (type == 'group'):
		group = Group(name=name, parentGroup=key, calendarId=None)
	elif (type == 'user'):
		group = User(name=name, parentGroup=key, calendarId=None)
	key = group.put()
	return JsonResponse({'id' : key.__str__() })


def cleanGroups():
	for g in db.GqlQuery('SELECT * FROM Group'):
		try:
			if (g.parentGroup):
				db.get(g.parentGroup.key())
		except:
			g.delete()

def deleteGroup(id):
	db.get(id).delete()
	children = db.GqlQuery(	'SELECT __key__ FROM Group  ' + 
							'WHERE parentGroup = :1', id)
	for cid in children:
		deleteGroup(cid)

def groups_delete(request):
	id = request.REQUEST['id']
	if (not id):
		return JsonResponse({ }, 404)
	key = db.Key(id)
	deleteGroup(key)
	return JsonResponse({})

def GetParams(request):
	if (request.method == 'GET' or request.method == "POST"):
		return request.REQUEST
	params = parse_qs(request.raw_post_data)
	p = {}
	for name in params:
		p[name] = params[name][0]
	return p
		
def groups_put(request):
	try:
		try:
			r = GetParams(request)
		except:# Exception as e:
			return JsonResponse(sys.exc_info()[0].__str__())
		
		if (not 'id' in r or not 'name' in r):
			return JsonResponse({}, 400)
		
		id = r['id']
		name = r['name']
		try:
			key = db.Key(id)
			group = Group.get(key)
			if (group.type() == 'user'):
				if ('email' in r):
					group.account = users.User(r['email'])
		except: # Exception as e:
			return JsonResponse(sys.exc_info()[0].__str__(), 404) 
		if 'calId' in r:
			group.calendarId = r['calId'].strip() if r['calId'].strip().__len__() > 0 else None
		group.name = name
		group.put()
		return JsonResponse({})
	except:# Exception as e:
		return JsonResponse(sys.exc_info()[0].__str__()) 

def groups_newcal(request):
	if not 'id' in request.REQUEST:
		return JsonResponse({}, 400)
	id = request.REQUEST['id']
	try:
		key = db.Key(id)
		group = Group.get(key)
	except:
		return JsonResponse({}, 404)
	
	cs = getCalendarService(request)
	cal = createCalendar(cs, group.name)
	calendarId = cal.GetEventFeedLink()
	group.calendarId = calendarId
	group.put()
	return JsonResponse({ 'calId' : calendarId })

def getSystemAccount():
	try:
		sa = SystemAccount.all()
		for a in sa.fetch(1):
			return a
		return None
	except:
		return None

def systemAccount(request):
	user = users.get_current_user()
	if not user or not users.is_current_user_admin():
		return redirect('/')
	
	sa = getSystemAccount()
	if 'email' in request.REQUEST and 'password' in request.REQUEST:
		if not sa:
			sa = SystemAccount(email=request.REQUEST['email'],
						password=request.REQUEST['password'])
		else:
			sa.email = request.REQUEST['email']
			sa.password = request.REQUEST['password']
		sa.put()
	return render_to_response('systemAccount.html', locals())
	
def filter(view):
	def f(request, *args):
		#user = users.get_current_user()
		#if (not user or not users.is_current_user_admin()):
		#	return HttpResponse("access denied")
		#else:
		return view(request, *args)
	return f

def clearSession(request):
	for key in request.session.keys():
		del request.session[key]
	request.session.clear()
	return redirect('/')

