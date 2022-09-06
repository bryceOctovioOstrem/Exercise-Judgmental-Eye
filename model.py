"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)
    
    def __repr__(self):

        return f"<User user_id={self.user_id} email={self.email}>"

    def predict_rating(self, movie):

        UserMovies = db.aliased(Rating)
        MovieUsers = db.aliased(Rating)

        query = (db.session.query(Rating.user_id, Rating.score, UserMovies.score, MovieUsers.score)
                 .join(UserMovies, UserMovies.movie_id == Rating.movie_id)
                 .join(MovieUsers, Rating.user_id == MovieUsers.user_id)
                 .filter(UserMovies.user_id == self.user_id)
                 .filter(MovieUsers.movie_id == movie.movie_id))

        known_ratings = {}
        paired_ratings = defaultdict(list)

        for rating_user_id, rating_score, user_movie_score, movie_user_score in query:
            paired_ratings[rating_user_id].append((user_movie_score, rating_score))
            known_ratings[rating_user_id] = movie_user_score

        similarities = []

        for _id, score in known_ratings.items():
            similarity = correlation.pearson(paired_ratings[_id])
            if similarity > 0:
                similarities.append((similarity, score))


        if not similarities:
            return None

        numerator = sum([score * sim for sim, score in similarities])
        denominator = sum([sim for sim, score in similarities])

        return numerator / denominator

# Put your Movie and Rating model classes here.
class Movie(db.Model):

    __tablename__ = "movies"
    movie_id = db.Column(db.Integer,
                        autoincrement=True
                        primary_key=True)
    title = db.Column(db.String(1000))
    released_at = db.Column(db.DateTime)
    imdb_url = db.Column(db.String(200))

class Rating(db.Model):

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer,
                          autoincrement=True,
                          primary_key=True)
    movie_id = db.Column(db.Integer,
                         db.ForeignKey('movies.movie_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    score = db.Column(db.Integer)

    user = db.relationship("User",
                           backref=db.backref("ratings",
                                              order_by=rating_id))

    movie = db.relationship("Movie",
                            backref=db.backref("ratings",
                                               order_by=rating_id))

    def __repr__(self):

        return f"""<Rating rating_id={self.rating_id}
                   movie_id={self.movie_id}
                   user_id={self.user_id}
                   score={self.score}>"""   




##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print("Connected to DB.")
