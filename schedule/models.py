from appengine_django.models import BaseModel
from google.appengine.ext.db.polymodel import PolyModel
from google.appengine.ext import db

class Group(PolyModel):
	name		= db.StringProperty()
	parentGroup	= db.SelfReferenceProperty()
	calendarId	= db.StringProperty()

class Place(Group):
	pass
	
class User(Group):
	account		= db.UserProperty()
	
class User2(BaseModel):
	account		= db.UserProperty()
	
	
	

	
