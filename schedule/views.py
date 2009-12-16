from django.http import HttpResponse, Http404
from django.template import Template, Context
from django.template.loader import get_template
from django.shortcuts import render_to_response, redirect
from django.utils import simplejson
from django import forms
from pickle import dumps
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

from models import Group 
import calendar
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
		return render_to_response('index.html', locals())
	else:
		return redirect(users.create_login_url('/'))

		
def cal(request):
	if 'logout' in request.GET:
		del request.session['authsub_token']
	if 'authsub_token' not in request.session:
		authSubUrl = get_auth_sub_url(request)
		return redirect(authSubUrl.__str__())
	return HttpResponse("Ok")

def create_calendar(calendar_service):
	calendar = gdata.calendar.CalendarListEntry()
	calendar.title = atom.Title(text='Little League Schedule')
	calendar.summary = atom.Summary(text='This calendar contains practice and game times')
	calendar.where = gdata.calendar.Where(value_string='Oakland')
	calendar.color = gdata.calendar.Color(value='#2952A3')
	calendar.timezone = gdata.calendar.Timezone(value='America/Los_Angeles')
	calendar.hidden = gdata.calendar.Hidden(value='false')
	new_calendar = calendar_service.InsertCalendar(new_calendar=calendar)

def get_time(timestr):
	date = datetime.datetime.strptime(timestr[0:19], '%Y-%m-%dT%H:%M:%S')
	seconds = 3600 * int(timestr[24:26]) + 60 * int(timestr[27:29])
	if (timestr[23] == '+'):
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
	#evt = get_time(feed.entry[1].when[0].start_time)
	#uri = feed.entry[0].GetEditLink().href
	event = None#uri
	#feed = calendar_service.GetCalendarEventFeed(uri)
	return render_to_response('authsub.html', { 'feed': feed, 'event': event })

"""	<ul>
	{% for a_when in cal.when %}
    	<li>Start: {{a_when.start_time}}<br/>
    		End: {{a_when.end_time}}<br/>  		
    	</li>
    {% endfor %}
	</ul>
"""


def calendar(request):
	if 'authsub_token' not in request.session:
		authSubUrl = get_auth_sub_url(request)
		return redirect(authSubUrl.__str__())
	return render_to_response('calendar.html')

def make_time(h, m):
	return { 'hours': h, 'minutes': m }
	
def events(request):
	times = []
	t1 = 8 * 60
	t2 = t1 + 95
	for i in range(0, 10):
		times.append({
			'start': make_time(t1 / 60, t1 % 60),
			'end':   make_time(t2 / 60, t2 % 60) });
		t1 += 105
		t2 += 105
		
	d = datetime.date.today()
	d -= datetime.timedelta(days=d.weekday())
	dates = []
	for i in range(0, 7):
		dates.append({ 'year': d.year, 'month': d.month, 'day': d.day }) 
		d += datetime.timedelta(days=1)
		
	return HttpResponse(simplejson.dumps(
		{ 'places'	: 'L1 L2 L3 L4 478 479',
		  'times'	: times,
		  'dates'	: dates }),
		mimetype="application/json")	


def InsertSingleEvent(calendar_service,
					title='One-time Tennis with Beth', 
					content='Meet for a quick lesson',
					where='On the courts', 
					start_time=None, end_time=None):
	event = gdata.calendar.CalendarEventEntry()
	event.title = atom.Title(text=title)
	event.content = atom.Content(text=content)
	event.where.append(gdata.calendar.Where(value_string=where))

	if start_time is None:
    	# Use current time for the start_time and have the event last 1 hour
		start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
		end_time   = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(time.time() + 3600))
	event.when.append(gdata.calendar.When(start_time=start_time, end_time=end_time))

	new_event = calendar_service.InsertEvent(event, '/calendar/feeds/default/private/full')
    
	print 'New single event inserted: %s' % (new_event.id.text,)
	print '\tEvent edit URL: %s' % (new_event.GetEditLink().href,)
	print '\tEvent HTML URL: %s' % (new_event.GetHtmlLink().href,)
	
	return new_event

def JsonResponse(object, status=200):
	return HttpResponse(simplejson.dumps(object),
			mimetype="application/json",
			status= status)

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

def event(request):
	if request.method == 'GET':
		name  = request.REQUEST['name']
		where = request.REQUEST['where']
		when  = request.REQUEST['when']
		i = nth_index(when, "-", 3)
		start = datetime.datetime.strptime(when[0:i], '%Y-%m-%d  %H:%M')
		end = datetime.datetime.strptime(when[i + 1:], '%H:%M') 
		end = start.replace(hour=end.hour, minute=end.minute)
		#start + datetime.timedelta(hours=1)
		start = start.strftime('%Y-%m-%dT%H:%M:%S.000Z')
		end   = end.strftime('%Y-%m-%dT%H:%M:%S.000Z')
		event = None
		#try:
		calendar_service = gdata.calendar.service.CalendarService()
		calendar_service.SetAuthSubToken(request.session["authsub_token"])
		event = InsertSingleEvent(calendar_service, name, '', where, start, end)
		#except Exception as err:
		#	return JsonResponse(err.__str__())
		
		return JsonResponse(
			{ 'id': event.id.text, 'name': name, 'when': when, 'where': where })
	if request.method == 'PUT':
		pass
	return JsonResponse('GET')


def groups(request):
	user = users.get_current_user()
	if (not user or not users.is_current_user_admin()):
		return redirect('/')

	if (request.method == 'GET'):
		return groups_get(request)
	if (request.method == 'POST'):
		return groups_post(request)
	if (request.method == 'PUT'):
		return groups_put(request)
	
	return render_to_response('groups.html', locals())

def groups_get(request):
	cleanGroups()
	#group = Group(name='new group', parentGroup=None, calendarId="calId") 
	#group.put()
	groupsQuery = db.GqlQuery('SELECT * FROM Group')
	groups_json = []
	groups = []
	for g in groupsQuery.fetch(1000):
		gg = {}
		gg['name'] = g.name
		gg['id'] = g.key().__str__()
		try:
			if g.parentGroup:
				gg['parent'] = g.parentGroup.key().__str__()
			else:
				gg['parent'] = None
		except Exception:
			continue	
		groups.append(gg)

	groups_json = simplejson.dumps(groups)
	
	t = get_template('groups.html')
	html = t.render(Context({'groups': groups, 'groups_json': groups_json,}))
	return HttpResponse(html)

def groups_post(request):
	name = request.REQUEST['name']
	parentId = request.REQUEST['id']
	# XXX errors
	#parentGroupQuery = Group.gql('WHERE __key__ = :1', parentId)
	if (parentId == None or parentId.__len__() == 0):
		key = None
	else:
		key = db.Key(parentId)
	group = Group(name=name, parentGroup=key, calendarId="calId") 
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
		r = GetParams(request)
	except Exception as e:
		return JsonResponse(e.__str__())
	
	if (not 'id' in r or not 'name' in r):
		return JsonResponse({}, 400)
	
	id = r['id']
	name = r['name']
	try:
		key = db.Key(id)
		group = Group.get(key)
	except Exception as e:
		return JsonResponse(e.__str__(), 404) 
	
	group.name = name
	group.put()
	return JsonResponse({})
	

def filter(view):
	def f(request):
		user = users.get_current_user()
		if (not user or not users.is_current_user_admin()):
			return HttpResponse("access denied")
		else:
			return view(request)
	return f

