from flask import request
from flask import Blueprint
from config import db
from common import response_functions,response_strings
from util.current_user import get_current_user
from models.models import User
import traceback


user_route = Blueprint('user_route',__name__,url_prefix='/api/user')


@user_route.get("")
def user_details():
  try:
    session = db.session()
    session.begin()
    email = get_current_user()['email']
    user = session.query(User).filter(User.email == email).first()
    response_body = {
      'user_name' : user.name,
      'user_email' : user.email
    }
    session.commit()
    session.close()
    return response_functions.success_response_sender(data=response_body,message=response_strings.user_data_fetch_success)
  except Exception as e:
    traceback.print_exception(e)
    session.rollback()
    session.close()
    return response_functions.bad_request_sender(None,response_strings.invalid_data_string)