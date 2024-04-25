from factory import createapp
from flask_migrate import Migrate
from config import db
from models.models import *
from common import response_functions,response_strings

app = createapp()
migrate = Migrate(app=app,db=db)


@app.errorhandler(404)
def invlaid_route_handle(error):
    return response_functions.not_found_sender([],response_strings.wrong_url_message)

@app.errorhandler(Exception)
def global_error(error):
    return response_functions.server_error_sender([],str(error))


if __name__ == '__main__':
  
  app.run(host='0.0.0.0',port=app.config['PORT'],debug=True)