from flask_restful import Api
from backend import app
from .__help__ import *
from . import user, year


api = Api(app)
api.add_resource(user.UserListResource, '/api/v1/user')
api.add_resource(user.UserResource, '/api/v1/user/<int:item_id>')
api.add_resource(year.YearListResource, '/api/v1/year')
api.add_resource(year.YearResource, '/api/v1/year/<int:item_id>')
