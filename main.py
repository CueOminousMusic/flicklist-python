import webapp2
import random

class Index(webapp2.RequestHandler):

    def getRandomMovie(self):

        # TODO: make a list with at least 5 movie titles
        movies_list = [
                    'Tron',
                    'The Big Lebowski',
                    'Seabiscuit',
                    'Iron Man',
                    'Tron: Legacy',
                    'K-Pax',
                    'The Fabulous Baker Boys',
                    'Wild Bill',
                    'The Men Who Stare at Goats',
                    'True Grit',
                    'The Giver'
        ]

        # TODO: randomly choose one of the movies, and return it
        movieIndex = random.randint(0, len(movies_list)-1)

        return movies_list[movieIndex]
        #return "The Big Lebowski"

    def get(self):
        # choose a movie by invoking our new function
        movie = self.getRandomMovie()
        movie2 = self.getRandomMovie()
        while movie2 == movie:
            movie2 = self.getRandomMovie()


        # build the response string
        content = "<h1>Movie of the Day</h1>"
        content += "<p>" + movie + "</p>"

        content += "<h1>Tomorrow's Movie of the Day</h1>"
        content += "<p>" + movie2 + "</p>"


        # TODO: pick a different random movie, and display it under
        # the heading "<h1>Tommorrow's Movie</h1>"

        self.response.write(content)

app = webapp2.WSGIApplication([
    ('/', Index)
], debug=True)
