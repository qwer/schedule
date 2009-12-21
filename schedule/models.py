from appengine_django.models import BaseModel
from google.appengine.ext.db.polymodel import PolyModel
from google.appengine.ext import db

class Group(PolyModel):
	name		= db.StringProperty()
	parentGroup	= db.SelfReferenceProperty()
	calendarId	= db.StringProperty()
	
	def type(self):
		return self.__class__.__name__.lower()
	
	def json(self):
		return { 
			'name':  self.name, 
			'id':    self.key().__str__(),
			'type':  self.type(),
			'calId': self.calendarId 
		} 

class Place(Group):
	pass
	
class User(Group):
	account		= db.UserProperty()
	def json(self):
		return { 
			'name':  self.name, 
			'id':    self.key().__str__(),
			'type':  self.type(),
			'calId': self.calendarId,
			'email': self.account.email() if self.account else None 
		}
	
class User2(BaseModel):
	account		= db.UserProperty()

class SystemAccount(BaseModel):
	email		= db.StringProperty()
	password	= db.StringProperty()
	
	

	
