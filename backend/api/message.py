from flask_restful import reqparse, Resource

from . import get_point, str_or_int
from ..api import api_group, api_item, ApiStatus
from ..database import Iti, Message
from ..help import UserRoleGlobal
from ..queries.help import correct_new_line
from ..queries.messages_help import send_message_to_telegram


parser_simple = reqparse.RequestParser()
parser_simple.add_argument('title', required=True, type=str)
parser_simple.add_argument('content', required=True, type=str)
parser_simple.add_argument('date', required=True, type=str)
parser_simple.add_argument('time', required=True, type=str)
parser_simple.add_argument('timezone', required=True, type=int)
parser_simple.add_argument('priority', required=True, type=str_or_int)
parser_full = parser_simple.copy()
parser_full.add_argument('year', required=True, type=int)


class MessageResource(Resource):
    @api_item(db=Message.select, roles=[UserRoleGlobal.CHANGE_MESSAGE])
    def put(self, message: Message):
        args = parser_simple.parse_args()
        args['title'], args['content'] = correct_new_line(args['title']), correct_new_line(args['content'])
        point = get_point(args['date'], args['time'], args['timezone'])
        new = Message.build(None, None, args['title'], args['content'], point, args['priority'], allow_empty=True)
        message ^= new
        Message.update(message)
        return ApiStatus.OK, {'message': 'Сообщение обновлено'}

    @api_item(db=Message.select, roles=[UserRoleGlobal.CHANGE_MESSAGE])
    def delete(self, message: Message):
        Message.delete(message)
        return ApiStatus.OK, {'message': 'Сообщение удалено'}


class MessageListResource(Resource):
    @api_group(roles=[UserRoleGlobal.CHANGE_MESSAGE])
    def post(self):
        args = parser_full.parse_args()
        args['title'], args['content'] = correct_new_line(args['title']), correct_new_line(args['content'])
        point = get_point(args['date'], args['time'], args['timezone'], null=False)
        if Iti.select(args['year']) is None:
            return ApiStatus.FAIL, {'message': 'Этого года нет'}
        message = Message.build(None, args['year'], args['title'], args['content'], point, args['priority'])
        Message.insert(message)
        send_message_to_telegram(args['title'], args['content'], args['year'])
        return ApiStatus.OK, {'message': 'Сообщение добавлено'}
