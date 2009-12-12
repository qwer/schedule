from django.conf.urls.defaults import *
#from views import hello, current_datetime, hours_ahead, contact
from views import index, authsub, cal, calendar, events, event
from views import groups, groups_post, groups_delete, groups_put

urlpatterns = patterns('',
	(r'^$', index),
	(r'^cal/$', cal),
	(r'^calendar/$', calendar),
	(r'^events/$', events),
	(r'^event/$', event),
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
