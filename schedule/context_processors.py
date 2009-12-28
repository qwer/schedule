from google.appengine.api import users

def userContext(request):
	user = users.get_current_user()
	userName = user.nickname()
	isAdmin = users.is_current_user_admin()
	logoutUrl = users.create_logout_url('/')
	return locals()