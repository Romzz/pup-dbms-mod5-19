import webapp2
import jinja2
from google.appengine.api import users
from google.appengine.ext import ndb
import os
import urllib
import logging
import json
import cgi

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
	
DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)

class Thesis(ndb.Model):
    year = ndb.IntegerProperty(indexed=True)
    title = ndb.StringProperty(indexed=True)
    abstract = ndb.StringProperty(indexed=True)
    adviser = ndb.StringProperty(indexed=True)
    section = ndb.IntegerProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)

class UserDB(ndb.Model):
    id = ndb.StringProperty(indexed = True)
    email = ndb.StringProperty(indexed = True)
    first_name = ndb.StringProperty(indexed = True)
    last_name = ndb.StringProperty(indexed = True)
    mobile_phone = ndb.StringProperty(indexed = True)
    current_date = ndb.DateTimeProperty(auto_now_add = True)

class RegisterPageHandler(webapp2.RequestHandler):
    def get(self):
        loggedin_user = users.get_current_user()

        if loggedin_user:
                    ###### This syntax works on my classmates
                    ###### but not in my workspace. It's depressing
            # user_key = ndb.key(UserDB, loggedin_user.user_id())
            # user = user_key.get()

            # if user:
            #     self.redirect('/home') 
            # else:

            template = JINJA_ENVIRONMENT.get_template('register.html')
            logout_url = users.create_logout_url(self.request.uri)
            template_values = {
                'logout_url' : logout_url
            }
            self.response.write(template.render(template_values))
        else:
            # login_url = users.create_login_url(self.request.uri)
            # template_values = {
            #     'login_url' : login_url
            # }
            # template = jinja_env.get_template('login.html')
            # self.response.write(template.render(template_values))

            login_url = users.create_login_url('/register')
            self.redirect(login_url)

    def post(self):
        loggedin_user = users.get_current_user()
        
        user = UserDB(
            id=loggedin_user.user_id(),
            email=loggedin_user.email(),
            first_name=cgi.escape(self.request.get('first_name')),
            last_name=cgi.escape(self.request.get('last_name')),
            mobile_phone=cgi.escape(self.request.get('mobile_phone'))
            )
        user.put()
        self.redirect('/home')

class APIRegisterHandler(webapp2.RequestHandler):
    def get(self):
        user = UserDB.query().order(-UserDB.current_date).fetch()
        user_list = []

        for datas in user:
            user_list.append({
                'id': datas.key.urlsafe(),
                'email': datas.email,
                'first_name': datas.first_name,
                'last_name': datas.last_name,
                'mobile_phone': datas.mobile_phone
                })

        response = {
            'result': 'OK',
            'data': user_list
        }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response))

    def post(self):
        user = UserDB(
            email=cgi.escape(self.request.get('email')),
            first_name=cgi.escape(self.request.get('first_name')),
            last_name=cgi.escape(self.request.get('last_name')),
            mobile_phone=cgi.escape(self.request.get('mobile_phone')),
            )
        user.put()

        self.response.headers['Content-Type'] = 'application/json'
        response = {
            'result': 'OK',
            'data': {
                'id': user.key.urlsafe(),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'mobile_phone': user.mobile_phone,
            }
        }
        self.response.out.write(json.dumps(response))

class MainPageHandler(webapp2.RequestHandler):
	 def get(self):

			user = users.get_current_user()
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'

			template_data = {
				'user': user,
				'url': url,
				'url_linktext': url_linktext
			}
			if user:
				template = JINJA_ENVIRONMENT.get_template('main.html')
				self.response.write(template.render(template_data))
			else:
				self.redirect(users.create_login_url(self.request.uri))

class APIThesisHandler(webapp2.RequestHandler):
    def get(self):
        thesiss = Thesis.query().order(-Thesis.date).fetch()
        thesis_list = []

        for thesis in thesiss:
            thesis_list.append({
                'id': thesis.key.urlsafe(),
                'year' : thesis.year,
                'title' : thesis.title,
                'abstract' : thesis.abstract,
                'adviser' : thesis.adviser,
                'section' : thesis.section
                });
            
        response = {
             'result' : 'OK',
             'data' : thesis_list
        }
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response))

    def post(self):
        thesis = Thesis()
        thesis.year = int(self.request.get('year'))
        thesis.title = self.request.get('title')
        thesis.abstract = self.request.get('abstract')
        thesis.adviser = self.request.get('adviser')
        thesis.section = int(self.request.get('section'))
        thesis.key = thesis.put()
        thesis.put()

        self.response.headers['Content-Type'] = 'application/json'
        response = {
        'result' : 'OK',
        'data':{
            'id': thesis.key.urlsafe(),
                'year' : thesis.year,
                'title' : thesis.title,
                'abstract' : thesis.abstract,
                'adviser' : thesis.adviser,
                'section' : thesis.section
        }
        }
        self.response.out.write(json.dumps(response))

app = webapp2.WSGIApplication([
    ('/api/thesis', APIThesisHandler),
    ('/home', MainPageHandler),
    ('/', RegisterPageHandler),
    ('/register', RegisterPageHandler),
    ('/api/register', APIRegisterHandler)
], debug=True)