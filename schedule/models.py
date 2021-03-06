from appengine_django.models import BaseModel
from google.appengine.ext.db.polymodel import PolyModel
from google.appengine.ext import db

class Callable:
	def __init__(self, callable):
		self.__call__ = callable

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
		
	def getAllChildren(self):
		children = [self]
		query = Group.all().filter('parentGroup =', self)
		for g in query.fetch(10000):
			children.extend(g.getAllChildren())
		return children
	
	def getByName(name):
		query = Group.all().filter('name =', name)
		for g in query.fetch(10000):
			return g
		return None
	
	getByName = Callable(getByName)
		
class Place(Group):
	pass
	
class User(Group):
	account		= db.UserProperty()
	timezone	= db.IntegerProperty()
	
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
	
