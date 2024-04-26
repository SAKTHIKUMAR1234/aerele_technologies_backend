from flask import request
from flask import Blueprint
from config import db
from common import response_functions,response_strings
from models.models import Product,Location,ProductMovement
import traceback


product_route = Blueprint('product_route',__name__,url_prefix='/api/product')


@product_route.post('/add')
def create_product():
  try:
    product_data = None
    try:
      product_data = request.get_json()
    except Exception as e:
      return response_functions.bad_request_sender(None,response_strings.invalid_data_string)
    required_data = ['product_name','product_quantity','product_location_id','product_price']
    if product_data is None :
      return response_functions.bad_request_sender(None,response_strings.invalid_data_string)
    if not all(key in request.json for key in required_data):
      return response_functions.bad_request_sender(None,response_strings.invalid_data_string)
    session = db.session()
    session.begin()
    location = session.query(Location).filter(Location.id == product_data['product_location_id']).first()
    if location == None:
      session.rollback()
      session.close()
      return response_functions.not_found_sender({'product_location_id':product_data['product_location_id']},response_strings.location_not_found)
    product = Product()
    product.location = location
    product.price = product_data['product_price']
    product.quantity = product_data['product_quantity']
    product.product_name = product_data['product_name']
    session.add(product)
    movement = ProductMovement()
    movement.product = product
    movement.to_location = location
    session.add(movement)
    session.commit()
    return response_functions.created_response_sender(None,response_strings.product_created_response)
  except Exception as e:
    session.rollback()
    session.close()
    return response_functions.bad_request_sender(None,response_strings.invalid_data_string)
  
@product_route.put('/edit/<product_id>')
def update_product(product_id):
  try:
    try:
      request.json
    except Exception as e:
      return response_functions.bad_request_sender(None,response_strings.invalid_data_string)
    product_data = request.get_json()
    if product_data is None :
      return response_functions.bad_request_sender(None,response_strings.invalid_data_string)
    required_data = ['product_name','product_quantity','product_location_id','product_price']
    if not all(key in request.json for key in required_data):
      return response_functions.bad_request_sender(None,response_strings.invalid_data_string)
    session = db.session()
    session.begin()
    location = session.query(Location).filter(Location.id == product_data['product_location_id']).first()
    product = session.query(Product).filter(Product.id == product_id,Product.is_deleted == False).first()
    if product.location != location:
      movement : ProductMovement = product.movement
      movement.from_location = movement.to_location
      movement.to_location = location
      session.add(movement)
    product.location = location
    product.price = product_data['product_price']
    product.quantity = product_data['product_quantity']
    product.product_name = product_data['product_name']
    session.add(product)
    session.commit()
    session.close()
    return response_functions.created_response_sender(None,response_strings.product_updated_success)
  except Exception as e:
    session.rollback()
    session.close()
    return response_functions.bad_request_sender(None,response_strings.invalid_data_string)
    
  
@product_route.post('')
def get_products():
  try :
    try:
      request.json
    except Exception as e:
      return response_functions.bad_request_sender(None,response_strings.invalid_data_string)
    if 'product_query' not in request.json:
      return response_functions.bad_request_sender(None,response_strings.invalid_data_string)
    session = db.session()
    session.begin()
    product_list = []
    if request.json['product_query'] == '':
      product_list = session.query(Product).filter(Product.is_deleted == False).all()
    else : 
      product_list = session.query(Product).filter(Product.product_name.like(f'%{request.json['product_query']}%'),Product.is_deleted == False).all()
    response_body = [
      {
        'id' : product.id,
        'product_name' : product.product_name,
        'product_quantity' : product.quantity,
        'product_price' : product.price,
        'product_location' : product.location.location_name
      }
    
      for product in product_list
      ]
    session.commit()
    session.close()
    return response_functions.success_response_sender(response_body,response_strings.success_response)
  except Exception as e:
    session.rollback()
    session.close()
    return response_functions.bad_request_sender(None,response_strings.invalid_data_string)
  
  
@product_route.post('/movements')
def get_product_movements():
  try :
    try:
      request.json
    except Exception as e:
      return response_functions.bad_request_sender(None,response_strings.invalid_data_string)
    if 'movement_query' not in request.json:
      return response_functions.bad_request_sender(None,response_strings.invalid_data_string)
    session = db.session()
    session.begin()
    movements = []
    if request.get_json()['movement_query'] == '':
      movements = session.query(ProductMovement).all()
    else : 
      movements = session.query(ProductMovement).join(Product).filter(Product.product_name.like(f'%{request.json["movement_query"]}%')).all()
    response_body = [
      {
        'from' : '' if movement.from_location is None else movement.from_location.location_name,
        'to' : '' if movement.to_location is None else movement.to_location.location_name,
        'product' : movement.product.product_name,
        'quantity' : movement.product.quantity if movement.product.is_deleted == False else ''
      }
        for movement in movements  
      ]
    return response_functions.success_response_sender(response_body,response_strings.success_response)
  except Exception as e:
    traceback.print_exception(e)
    session.rollback()
    session.close()
    return response_functions.bad_request_sender(None,response_strings.invalid_data_string)
  
  
@product_route.delete('/delete/<product_id>')
def delete_product(product_id):
  try:
    session = db.session()
    session.begin()
    product = session.query(Product).filter(Product.id == product_id,Product.is_deleted == False).first()
    if product == None:
      session.rollback()
      session.close()
      return response_functions.not_found_sender({'product_id':product_id},response_strings.product_not_found)
    movement : ProductMovement = product.movement
    movement.from_location = movement.to_location
    movement.to_location = None
    session.add(movement)
    product.is_deleted = True
    session.add(product)
    session.commit()
    session.close()
    return response_functions.success_response_sender(None,response_strings.product_deleted_response)
  except Exception as e:
    session.rollback()
    session.close()
    return response_functions.bad_request_sender(None,response_strings.invalid_data_string)
    