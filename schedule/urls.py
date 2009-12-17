from django.conf.urls.defaults import *
#from views import hello, current_datetime, hours_ahead, contact
from views import index, authsub, cal, calendar, events, event
from views import filter
from views import groups, groups_post, groups_delete, groups_put

filters = filter

def filterViews(*p):
	args = []
	pp = []
	for pattern in p:
		if (not type(pattern) is str):
			args.append((pattern[0], filter(pattern[1])))
		else:
			args.append(pattern)
	return patterns(*args)

urlpatterns = filterViews(
	'',
	(r'^$', index), #lambda request: filter(index, request)),
	(r'^cal/$', cal),
	(r'^calendar/$', calendar),
	(r'^events/$', events),
	(r'^event/$', event),
	(r'^groups/([^/]+)/$', groups),
	(r'^groups/$', groups),
	(r'^groups_post/$', groups_post),
	(r'^groups_put/$', groups_put),
	(r'^groups_delete/$', groups_delete),
	(r'^authsub/$', authsub),
	
#	(r'^hello/$', hello),
#	(r'^time/$', current_datetime),
#	(r'^time/plus/(\d{1,2})/$', hours_ahead),
#	(r'^contact/$', contact),

	# Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
	# to INSTALLED_APPS to enable admin documentation:
	# (r'^admin/doc/', include('django.contrib.admindocs.urls')),
)
