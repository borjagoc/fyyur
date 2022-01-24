#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from unicodedata import name
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from models import *



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
now = datetime.now()

@app.route('/venues')
def venues():
  locals = []
  venues = Venue.query.all()
  places = Venue.query.distinct(Venue.city, Venue.state).all()

  for place in places:
    locals.append({
        'city': place.city,
        'state': place.state,
        'venues': [{
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': Show.query.filter(Show.venue_id == venue.id, Show.start_time > now ).count()
        } for venue in venues if
            venue.city == place.city and venue.state == place.state]
    })

  return render_template('pages/venues.html', areas=locals);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term')
  search_query = Venue.query.filter(Venue.name.ilike("%"+search_term+"%")).all()
  response = search_query
  search_count = len(search_query)

  return render_template('pages/search_venues.html', results=response, search_count=search_count, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id)
  upcoming_shows_count = Show.query.filter(Show.venue_id == venue.id, Show.start_time >= now ).count()
  upcoming_shows = db.session.query(Artist.image_link.label('artist_image_link'), Show.artist_id, Artist.name.label('artist_name'), Show.start_time).join(Artist, Show.artist_id == Artist.id).join(Venue, Show.venue_id == Venue.id).filter(Show.start_time >= now, Show.venue_id == venue_id).all()
  past_shows_count = Show.query.filter(Show.venue_id == venue.id, Show.start_time < now ).count()
  past_shows = db.session.query(Artist.image_link.label('artist_image_link'), Show.artist_id, Artist.name.label('artist_name'), Show.start_time).join(Artist, Show.artist_id == Artist.id).join(Venue, Show.venue_id == Venue.id).filter(Show.start_time < now, Show.venue_id == venue_id).all()
  return render_template('pages/show_venue.html', venue=venue, upcoming_shows_count=upcoming_shows_count,past_shows_count=past_shows_count,past_shows=past_shows,upcoming_shows=upcoming_shows)

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
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    website = request.form['website_link']
    seeking_talent = bool(request.form.get('seeking_talent'))
    seeking_description = request.form['seeking_description']
    new_venue = Venue(name=name,city=city,state=state,address=address,phone=phone,image_link=image_link,genres=genres,seeking_talent=seeking_talent,facebook_link=facebook_link,website=website,seeking_description=seeking_description)
    db.session.add(new_venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term')
  search_query = Artist.query.filter(Artist.name.ilike("%"+search_term+"%")).all()
  response = search_query
  search_count = len(search_query)
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''), search_count=search_count)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artist = Artist.query.get(artist_id)
  upcoming_shows_count = Show.query.filter(Show.artist_id == artist_id, Show.start_time >= now ).count()
  upcoming_shows = db.session.query(Venue.image_link.label('venue_image_link'), Show.venue_id, Venue.name.label('venue_name'), Show.start_time).join(Artist, Show.artist_id == Artist.id).join(Venue, Show.venue_id == Venue.id).filter(Show.start_time >= now, Show.artist_id == artist_id).all()
  past_shows_count = Show.query.filter(Show.artist_id == artist_id, Show.start_time < now ).count()
  past_shows = db.session.query(Venue.image_link.label('venue_image_link'), Show.venue_id, Venue.name.label('venue_name'), Show.start_time).join(Artist, Show.artist_id == Artist.id).join(Venue, Show.venue_id == Venue.id).filter(Show.start_time < now, Show.artist_id == artist_id).all()
  return render_template('pages/show_artist.html', artist=artist, upcoming_shows_count=upcoming_shows_count,past_shows_count=past_shows_count,past_shows=past_shows,upcoming_shows=upcoming_shows)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  artist = Artist.query.get(artist_id)
  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.image_link = request.form['image_link']
    artist.genres = request.form.getlist('genres')
    artist.website = request.form['website_link']
    artist.seeking_venue = bool(request.form.get('seeking_venue'))
    artist.seeking_description = request.form['seeking_description']
    artist.facebook_link = request.form['facebook_link']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if not error:
    flash('Artist updated!')
  if error:
    flash('Artist could not be updated!')
  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  venue = Venue.query.get(venue_id)
  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.image_link = request.form['image_link']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website_link']
    venue.seeking_talent = bool(request.form.get('seeking_talent'))
    venue.seeking_description = request.form['seeking_description']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if not error:
    flash('Venue updated!')
  if error:
    flash('Venue could not be updated!')
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
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form.getlist('genres')
    website = request.form['website_link']
    seeking_venue = bool(request.form.get('seeking_venue'))
    seeking_description = request.form['seeking_description']
    facebook_link = request.form['facebook_link']
    new_artist = Artist(name=name,city=city,state=state,phone=phone,image_link=image_link,genres=genres,website=website,seeking_description=seeking_description,seeking_venue=seeking_venue,facebook_link=facebook_link)
    db.session.add(new_artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = db.session.query(Artist.image_link.label('artist_image_link'), Show.start_time , Show.artist_id, Show.venue_id, Artist.name.label('artist_name'), Venue.name.label('venue_name')).join(Venue, Show.venue_id == Venue.id).join(Artist, Show.artist_id == Artist.id).all()
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    new_show = Show(artist_id=artist_id,venue_id=venue_id,start_time=start_time)
    db.session.add(new_show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')
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
