#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
#from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#from flask_migrate import Migrate
from models import *

db.init_app(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  venues = Venue.query.all()

  # Use set so there are no duplicate venues
  city_and_state = set()

  for venue in venues:
      # add city_state tuples
    city_and_state.add((venue.city, venue.state))

  # for each unique city/state, add venues
  for area in city_and_state:
    data.append({
        "city": area[0],
        "state": area[1],
        "venues": []
    })

  for venue in venues:
    num_upcoming_shows = 0

    shows = Show.query.filter_by(venue_id=venue.id).all()

    # get current date to filter num_upcoming_shows
    current_date = datetime.now()

    for show in shows:
      if show.start_time > current_date:
          num_upcoming_shows += 1

    for area in data:
      if venue.state == area['state'] and venue.city == area['city']:
        area['venues'].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_upcoming_shows
        })


  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')

  response = {}

  venues = list(Venue.query.filter(
    Venue.name.ilike(f"%{search_term}%") | Venue.city.ilike(f"%{search_term}%") | Venue.state.ilike(f"%{search_term}%")
  ).all())

  response['count'] = len(venues)
  response['data'] = []

  for v in venues:
    venue = {
      "id": v.id,
      "name": v.name,
      "num_upcoming_shows": len(list(filter(lambda d: d.start_time > datetime.now(), v.shows)))
    }

    response['data'].append(venue)

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  setattr(venue, "genres", venue.genres.split(","))

  data = []
  past_show = []
  upcoming_show = []

  past_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time>=datetime.now()).all()

  # Format past shows and append the data to the venue
  for show in past_shows:
    past_show.append({
      "artist_id": show.artist_id,
      "artist_name": show.artists.name,
      "artist_image_link": show.artists.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
  })

  # Format upcoming shows and append the data to the venue
  for show in upcoming_shows:
    upcoming_show.append({
      "artist_id": show.artist_id,
      "artist_name": show.artists.name,
      "artist_image_link": show.artists.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")    
  })

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description":venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_show,
    "upcoming_shows": upcoming_show,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    # TODO: insert form data as a new Venue record in the db, instead
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    genre_data = request.form.getlist('genres')
    genres = ', '.join(genre_data)
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')
    website_link = request.form.get('website_link')
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description')

    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()

    # TODO: modify data to be the data object returned from db insertion
    # on successful db insert, flash success
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occurred while deleting. Could not successfully delete venue ' + venue_id)
    else:
      flash('Successfully deleted venue ' + venue_id)
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for("index"))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term', '')

  response = {}

  artists = list(Artist.query.filter(
    Artist.name.ilike(f"%{search_term}%") | Artist.city.ilike(f"%{search_term}%") | Artist.state.ilike(f"%{search_term}%")
  ).all())

  response = {
    "count": len(artists),
    "data": artists
  }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.get(artist_id)
  setattr(artist, "genres", artist.genres.split(","))

  data = []

  past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()
  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>=datetime.now()).all()

  # Formatting past_shows and appending the formatted data to the artist
  for past_show in past_shows:
    show = {}
    show['venue_name'] = past_show.venues.name
    show['venue_id'] = past_show.venues.id
    show['venue_image_link'] = past_show.venues.image_link
    show['start_time'] = past_show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

    data.append(show)

  setattr(artist, "past_shows", data)
  setattr(artist, "past_shows_count", len(past_shows))

  data = []

  # Formatting upcoming_shows and appending the formatted data to the artist
  for upcoming_show in upcoming_shows:
    show = {}
    show['venue_name'] = upcoming_show.venues.name
    show['venue_id'] = upcoming_show.venues.id
    show['venue_image_link'] = upcoming_show.venues.image_link
    show['start_time'] = upcoming_show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

    data.append(show)
  
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  if artist: 
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  error = False
  try:
    # artist.name = request.form['name']
    # artist.city = request.form['city']
    # artist.state = request.form['state']
    # artist.phone = request.form['phone']
    # genre_data = request.form.getlist('genres')
    # artist.genres = ', '.join(genre_data)
    # #artist.genres = request.form.getlist('genres')
    # artist.facebook_link = request.form['facebook_link']
    # artist.image_link = request.form['image_link']
    # artist.website_link = request.form['website_link']
    # artist.seeking_talent = request.form['seeking_talent']
    # artist.seeking_description = request.form['seeking_description']

    artist.name = request.form.get('name', False)
    artist.city = request.form.get('city', False)
    artist.state = request.form.get('state', False)
    artist.phone = request.form.get('phone', False)
    genre_data = request.form.getlist('genres', False)
    artist.genres = ', '.join(genre_data)
    artist.facebook_link = request.form.get('facebook_link', False)
    artist.image_link = request.form.get('image_link', False)
    artist.website_link = request.form.get('website_link', False)
    artist.seeking_venue = request.form.get('seeking_venue')
    artist.seeking_description = request.form.get('seeking_description', False)

    db.session.add(artist)
    db.session.commit()

    # TODO: modify data to be the data object returned from db insertion
    # on successful db insert, flash success
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited')
    else:
      flash('Artist ' + request.form['name'] + ' was successfully edited!')
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  if venue: 
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  error = False
  try:
    # venue.name = request.form['name']
    # venue.city = request.form['city']
    # venue.state = request.form['state']
    # venue.address = request.form['address']
    # venue.phone = request.form['phone']
    # genre_data = request.form.getlist('genres')
    # venue.genres = ', '.join(genre_data)
    # venue.facebook_link = request.form['facebook_link']
    # venue.image_link = request.form['image_link']
    # venue.website_link = request.form['website_link']
    # venue.seeking_talent = request.form['seeking_talent']
    # venue.seeking_description = request.form['seeking_description']

    venue.name = request.form.get('name', False)
    venue.city = request.form.get('city', False)
    venue.state = request.form.get('state', False)
    venue.address = request.form.get('address', False)
    venue.phone = request.form.get('phone', False)
    genre_data = request.form.getlist('genres', False)
    venue.genres = ', '.join(genre_data)
    venue.facebook_link = request.form.get('facebook_link', False)
    venue.image_link = request.form.get('image_link', False)
    venue.website_link = request.form.get('website_link', False)
    venue.seeking_talent = request.form.get('seeking_talent')
    venue.seeking_description = request.form.get('seeking_description', False)

    db.session.add(venue)
    db.session.commit()

    # TODO: modify data to be the data object returned from db insertion
    # on successful db insert, flash success
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully edited!')
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    # artist = Artist()
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    #address = request.form.get('address')
    phone = request.form.get('phone')
    genre_data = request.form.getlist('genres')
    genres = ', '.join(genre_data)
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')
    website_link = request.form.get('website_link')
    seeking_venue = request.form.get('seeking_venue')
    seeking_description = request.form.get('seeking_description')

    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed')
    else:
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # called upon submitting the new artist listing form
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.order_by(db.desc(Show.start_time)).all()
  data = []
  for show in shows:
    data.append({
      'venue_id': show.venue_id,
      'venue_name': show.venues.name,
      'artist_id': show.artist_id,
      'artist_name': show.artists.name,
      'artist_image_link': show.artists.image_link,
      'start_time': show.start_time.isoformat()
    })
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
    show = Show()
    show.artist_id = request.form.get('artist_id')
    show.venue_id = request.form.get('venue_id')
    show.start_time = request.form.get('start_time')
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Show was not successfully listed')
    else:
      flash('Show was successfully listed!')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
