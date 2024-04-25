from flask import Blueprint,request
from models.models import Location
from common import response_strings,response_functions
from config import db

location_route = Blueprint('location_route',__name__,url_prefix='/api/loc')

@location_route.post('')
def get_locations():
  location_search = request.get_json()['search_query']
  
  try:
    session = db.session()
    session.begin()
    locations = []
    if location_search == '':
      locations = session.query(Location).all()
    else :
      locations = session.query(Location).filter(Location.location_name.like(f'%{location_search}%')).all()
    response_body = [
      {
        'id': location.id,
        'name': location.location_name,
      }
      for location in locations
    ]
    session.commit()
    session.close()
    return response_functions.success_response_sender(data=response_body,message=response_strings.success_response)
  except Exception as e:
    session.rollback()
    session.close()
    return response_functions.bad_request_sender(None,response_strings.invalid_data_string)


@location_route.post('/create/<location_name>')
def create_location(location_name):
  try:
    session = db.session()
    session.begin()
    location = session.query(Location).filter(Location.location_name == location_name).first()
    if location is not None:
      return response_functions.conflict_error_sender(None,response_strings.data_already_exist_message)
    location = Location()
    location.location_name = location_name
    session.add(location)
    session.commit()
    session.close()
    return response_functions.created_response_sender(None,response_strings.location_created_response)
  except Exception as e:
    session.rollback()
    session.close()
    return response_functions.bad_request_sender(None,response_strings.invalid_data_string)

@location_route.put('/update/<location_id>/<location_name>')
def update_location(location_id,location_name):
  try:
    session = db.session()
    session.begin()
    location = session.query(Location).filter(Location.location_name == location_name).first()
    if location is not None:
      return response_functions.conflict_error_sender(None,response_strings.data_already_exist_message)
    location = session.query(Location).filter(Location.id == location_id).first()
    if location is None:
      return response_functions.not_found_sender({'id':location_id},response_strings.location_not_found)
    location.location_name = location_name
    session.add(location)
    session.commit()
    return response_functions.success_response_sender(None,response_strings.location_updated_sender)
  except Exception as e:
    session.rollback()
    session.close()
    return response_functions.bad_request_sender(None,response_strings.invalid_data_string)
  