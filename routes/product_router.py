from flask import request
from flask import Blueprint
from config import db
from common import response_functions,response_strings
from models.models import Product

product_route = Blueprint('product_route',__name__,url_prefix='/api/product')


# @product_route.post('/add')
# def create_product():
  
  
