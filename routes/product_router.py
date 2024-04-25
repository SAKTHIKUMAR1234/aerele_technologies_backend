from flask import request
from flask import Blueprint
from config import db
from common import response_functions,response_strings
from models.models import Product,Location,ProductMovement

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
    return response_functions.created_response_sender(None,response_strings.user_created_success)
  except Exception as e:
    return response_functions.bad_request_sender(None,response_strings.invalid_data_string)
  
@product_route.post('')
def get_products():
  try :
    try:
      request.json
    except Exception as e:
      return response_functions.bad_request_sender(None,response_strings.invalid_data_string)
    session = db.session()
    if 'product_query' not in request.json:
      return response_functions.bad_request_sender(None,response_strings.invalid_data_string)
    session = db.session()
    session.begin()
    product_list = []
    if request.json['product_query'] == '':
      product_list = session.query(Product).all()
    else : 
      product_list = session.query(Product).filter(Product.product_name.like(f'%{request.json['product_query']}%')).all()
    response_body = [
      {
        'id' : product.id,
        'product_name' : product.product_name,
        'product_quantity' : product.quantity,
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
