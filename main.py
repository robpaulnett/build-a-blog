#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2
#  import cgi
from google.appengine.ext import db
# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class MainHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Entry(db.Model):        # defines the entity to bring in the DB
    title = db.StringProperty(required = True)    #  defines the types of the entity
    article = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(MainHandler):
    def render_base(self, title="", article="", error=""):
        theblogs = db.GqlQuery("SELECT * FROM Entry order by created ASC")    #theblogs is the "cursor"
        self.render("base.html", rendTitle=title, rendArticle=article, rendError=error, rendTheBlogs=theblogs)  #orange are what we reference in template

    def get(self):
        self.render_base()

    def post(self):
        self.render_base()

class CreateApost(MainHandler):
    def render_newpost(self, title="", article="", error=""):
        #theblogs = db.GqlQuery("SELECT * FROM Entry order by created ASC")    #theblogs is the "cursor"
        self.render("newpost.html", rendTitle=title, rendArticle=article, rendError=error)  #orange are what we reference in template


    def get(self):
        self.render_newpost()

    def post(self):
        postTitle = self.request.get("title")   #  "title" is from the name on the form
        postArticle = self.request.get("article")

        if postTitle and postArticle:
            blogOutput = Entry(title = postTitle, article = postArticle)    #self.write("thanks, for now")
            blogOutput.put()
            self.redirect("/permalinks/%s" % blogOutput.key().id())
        else:
            postError = "please create a title and a article"
            self.render_newpost(postTitle, postArticle, postError)

class RecentPost(MainHandler):
    def render_allposts(self, title="", article="", error=""):
        theblogs = db.GqlQuery("SELECT * FROM Entry order by created DESC LIMIT 5")    #theblogs is the "cursor"
        self.render("blog.html", rendTitle=title, rendArticle=article, rendError=error, rendTheBlogs=theblogs)  #orange are what we reference in template

    def get(self):
        self.render_allposts()

    def post(self):
        rendTitle = self.request.get("title")
        rendArticle = self.request.get("article")
        self.render_allposts(rendTitle, rendArticle)

class ViewPostHandler(MainHandler):
    def get(self, id):
        idEntry = Entry.get_by_id(int(id))
        #self.response.write(templates.render("permalinks", idEntry))
        if not idEntry:
            self.render("permalinks.html", idEntry=idEntry, error="Cannot find that blog entry")
        else:
            self.render("permalinks.html", idEntry=idEntry)
        #self.response.write(5910974510923776)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', CreateApost),
    ('/blog', RecentPost),
    (webapp2.Route('/permalinks/<id:\d+>', ViewPostHandler))
], debug=True)
