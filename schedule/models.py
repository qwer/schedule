from appengine_django.models import BaseModel
from google.appengine.ext import db

class Group(BaseModel):
	name		= db.StringProperty()
	parentGroup	= db.SelfReferenceProperty()
	calendarId	= db.StringProperty()

class Place(BaseModel):
	name		= db.StringProperty()
	group		= db.ReferenceProperty(Group)
	
class User(BaseModel):
	account		= db.UserProperty()
	
	
	

	
