from django.conf.urls.defaults import *

urlpatterns = patterns('',
	(r'', include('schedule.urls'))

	# Uncomment this for admin:
	# (r'^admin/', include('django.contrib.admin.urls')),
)
