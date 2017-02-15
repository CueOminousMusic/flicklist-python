import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db
import re

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

# a list of movies that nobody should be allowed to watch
terrible_movies = [
    "Gigli",
    "Star Wars Episode 1: Attack of the Clones",
    "Paul Blart: Mall Cop 2",
    "Nine Lives"
]
#Free routes - no login requried
allowed_routes = [
    "/"
    "/login"
    "/logout"
    "/register"
]



class User(db.Model):
    username = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)

class Movie(db.Model):
    title = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    watched = db.BooleanProperty(required = True, default = False)
    rating = db.StringProperty()


def getUnwatchedMovies():
    """ Returns the list of movies the user wants to watch (but hasnt yet) """

    return [ "Star Wars", "Minions", "Freaky Friday", "My Favorite Martian" ]


def getWatchedMovies():
    """ Returns the list of movies the user has already watched """

    return [ "The Matrix", "The Big Green", "Ping Ping Playa" ]


class Handler(webapp2.RequestHandler):
    """ A base RequestHandler class for our app.
        The other handlers inherit form this one.
    """

    def renderError(self, error_code):
        """ Sends an HTTP error code and a generic "oops!" message to the client. """

        self.error(error_code)
        self.response.write("Oops! Something went wrong.")

        def login_user(self, user):
            user_id = user.key().id()
            self.set_secure_cookie('user_id', str(user_id))

        def logout_user(self):
            self.set_secure_cookie('user_id', '')

        def set_secure_cookie(self, name, val):
            cookie_val - hashutils.make_secure_val(val)
            self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/') % (name, cookie_val)

        def read_secure_cookie(self, name):
            cookie_val - self.request.cookies.get(name)
            if cookie_val:
                return hashutils.check_secure_val(cookie_val)

        def get_user_by_name(self, username):
            user-db.GqlQuery("SELECT * FROM User WHERE username = '%s' " % username)
            if user:
                return user.get()

        #is run automatically by GAE every time a route is requested.
        def initialize(self, *args, **kwargs):
            webapp2.Requesthandler.initialize(self, *args, **kwargs)
            uid = self.read_secure_cookie('user_id')
            self.user = uid And User.get_by_id(int(uid))

            if not self.user and self.request.path not in allowed_routes:
                self.redirect('/login')


class Index(Handler):
    """ Handles requests coming in to '/' (the root of our site)
        e.g. www.flicklist.com/
    """

    def get(self):
        unwatched_movies = db.GqlQuery("SELECT * FROM Movie where watched = False")
        t = jinja_env.get_template("frontpage.html")
        content = t.render(
                        movies = unwatched_movies,
                        error = self.request.get("error"))
        self.response.write(content)

class AddMovie(Handler):
    """ Handles requests coming in to '/add'
        e.g. www.flicklist.com/add
    """

    def post(self):
        new_movie_title = self.request.get("new-movie")

        # if the user typed nothing at all, redirect and yell at them
        if (not new_movie_title) or (new_movie_title.strip() == ""):
            error = "Please specify the movie you want to add."
            self.redirect("/?error=" + cgi.escape(error))

        # if the user wants to add a terrible movie, redirect and yell at them
        if new_movie_title in terrible_movies:
            error = "Trust me, you don't want to add '{0}' to your Watchlist.".format(new_movie_title)
            self.redirect("/?error=" + cgi.escape(error, quote=True))

        # 'escape' the user's input so that if they typed HTML, it doesn't mess up our site
        new_movie_title_escaped = cgi.escape(new_movie_title, quote=True)

        # construct a movie object for the new movie
        movie = Movie(title = new_movie_title_escaped)
        movie.put()

        # render the confirmation message
        t = jinja_env.get_template("add-confirmation.html")
        content = t.render(movie = movie)
        self.response.write(content)


class WatchedMovie(Handler):
    """ Handles requests coming in to '/watched-it'
        e.g. www.flicklist.com/watched-it
    """

    def renderError(self, error_code):
        self.error(error_code)
        self.response.write("Oops! Something went wrong.")


    def post(self):
        watched_movie_id = self.request.get("watched-movie")

        watched_movie = Movie.get_by_id( int(watched_movie_id) )

        # if we can't find the movie, reject.
        if not watched_movie:
            self.renderError(400)
            return

        # update the movie's ".watched" property to True
        watched_movie.watched = True
        watched_movie.put()

        # render confirmation page
        t = jinja_env.get_template("watched-it-confirmation.html")
        content = t.render(movie = watched_movie)
        self.response.write(content)


class MovieRatings(Handler):

    def get(self):
        # TODO 1
        # Make a GQL query for all the movies that have been watched
        watched_movies = db.GqlQuery("SELECT * FROM Movie where watched = True ORDER BY created DESC ")
         # type something else instead of an empty list

        # TODO (extra credit)
        # in the query above, add something so that the movies are sorted by creation date, most recent first

        t = jinja_env.get_template("ratings.html")
        content = t.render(movies = watched_movies)
        self.response.write(content)

    def post(self):
        rating = self.request.get("rating")
        movie_id = self.request.get("movie")

        # TODO 2
        # retreive the movie entity whose id is movie_id
        movie = Movie.get_by_id # type something else instead of None

        if movie and rating:
            # TODO 3
            # update the movie's rating property and save it to the database
            movie.rating = rating
            movie.put()

            # render confirmation
            t = jinja_env.get_template("rating-confirmation.html")
            content = t.render(movie = movie)
            self.response.write(content)
        else:
            self.renderError(400)


class Login(Handler):
    def render_login_form(self, error=""):
        t = jinja_env.get_template("login.html")
        content = t.render(error = error)
        self.response.write(content)


    def get(self):
        self.render_login_form()

    def post(self):
        submitted_username = self.request.get('username')
        submitted_password = self.request.get('password')

        user = self.get_user_by_name(submitted_username)
        if not user:
            self.render_login_form(error="Invalid Username")
        elif not hashutils.valid_pw(submitted_username, submitted_password, user.pw_hash):
            self.render_login_form(error"Invalid Password)
        else:
            self.login_user(user)
            self.redirect('/')


class Logout(Handler):
    def get(self):
        self.logout_user()
        self.redirect('/login')


class Register(Handler):

    def validate_username(self, username):
        USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        if USER_RE.match(username):
            return username
        return ""

    def validate_password(self, password):
        PWD_RE = re.compile(r"^.{3,20}$")
        if USER_RE.match(username):
            return password
        return ""

    def validate_verify(self, password, verify):
        if password == verify:
            return verify

    def get(self):
        t = jinja_env.get_template("register.html")
        content = t.render(errors={})
        self.response.write(content)

    def post(self):
        def post(self):
            submitted_username = self.request.get('username')
            submitted_password = self.request.get('password')
            submitted_verify = self.request.get('verify')

            username = self.validate_username(submitted_username)
            password = self.validate_username(submitted_password)
            verify = self.validate_username(submitted_verify)

            errors = {}
            existing_user = self.get_user_by_name(username)
            has_error = False

            if existing_user:
                has_error = True
                errors['username'] = "A user with that name already exists"
            elif (username and password and verify):
                pw_hash = hashutils.make_pw_hash(username, password)
                user = User(username=user, pw_hash=pw_hash)
                user.put()

                # TODO: Login User - we'll redirect later
                self.login_user(user)

            else:
                has_error = True
                if not username:
                    errors['username'] = "That username is invalid."
                if not password:
                    errors['password'] = "That password is invalid."
                if not verify:
                    errors['verify'] = "Your passwords do not match."

            if has_error:
                t = jinja_env.get_template("register.html")
                content = t.render(username=username, errors=errors)
                self.response.write(content)
            else:
                #TODO Redirect to home page
                self.redirect('')



app = webapp2.WSGIApplication([
    ('/', Index),
    ('/add', AddMovie),
    ('/watched-it', WatchedMovie),
    ('/ratings', MovieRatings),
    ('/login', Login),
    ('/logout', Logout),
    ('/register', Register)
], debug=True)
