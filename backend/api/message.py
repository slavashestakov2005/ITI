from flask_restful import reqparse, Resource
from . import get_point
from ..api import api_item, api_group
from ..database import Message, Year
from ..queries.help import correct_new_line
from ..queries.messages_help import send_message_to_telegram


parser_simple = reqparse.RequestParser()
parser_simple.add_argument('title', required=True, type=str)
parser_simple.add_argument('content', required=True, type=str)
parser_simple.add_argument('date', required=True, type=str)
parser_simple.add_argument('time', required=True, type=str)
parser_full = parser_simple.copy()
parser_full.add_argument('year', required=True, type=int)


class MessageResource(Resource):
    @api_item(Message.select, 'admin')
    def put(self, message: Message):
        args = parser_simple.parse_args()
        args['title'], args['content'] = correct_new_line(args['title']), correct_new_line(args['content'])
        point = get_point(args['date'], args['time'])
        new = Message.build(None, None, args['title'], args['content'], point, allow_empty=True)
        message ^= new
        Message.update(message)
        return True, {'message': 'Сообщение обновлено'}

    @api_item(Message.select, 'admin')
    def delete(self, message: Message):
        Message.delete(message)
        return True, {'message': 'Сообщение удалено'}


class MessageListResource(Resource):
    @api_group('admin')
    def post(self):
        args = parser_full.parse_args()
        args['title'], args['content'] = correct_new_line(args['title']), correct_new_line(args['content'])
        point = get_point(args['date'], args['time'], null=False)
        if Year.select(args['year']) is None:
            return False, {'message': 'Этого года нет'}
        message = Message.build(None, args['year'], args['title'], args['content'], point)
        Message.insert(message)
        send_message_to_telegram(args['title'], args['content'], args['year'])
        return True, {'message': 'Сообщение добавлено'}
