#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

#from app import app as app
from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
#app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:cr122@localhost:5432/fyyurdb'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#db.init_app(app)
db = SQLAlchemy()
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String())
    shows = db.relationship("Show", backref="venues", lazy=False)
    

    def __repr__(self):
      return f'<Venue id: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, address: {self.address}, phone: {self.phone}, genres: {self.genres}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, website_link: {self.website_link}, seeking_talent: {self.seeking_talent}, seeking_description: {self.seeking_description}, shows: {self.shows}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    seeking_performance_venue = db.Column(db.Boolean())
    seeking_description = db.Column(db.String())
    shows = db.relationship("Show", backref="artists", lazy=False)

    def __repr__(self):
      return f'<Artist id: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, phone: {self.phone}, genres: {self.genres}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, website_link: {self.website_link}, seeking_performance_venue: {self.seeking_performance_venue}, seeking_description: {self.seeking_description}, shows: {self.shows}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
 __tablename__ = 'Show'

 id = db.Column(db.Integer, primary_key=True)
 artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
 venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
 start_time = db.Column(db.DateTime, nullable=False)

 def __repr__(self):
  return f'<Artist id: {self.id}, artist_id: {self.artist_id}, venue_id: {self.venue_id}, start_time: {self.start_time}>'



# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.