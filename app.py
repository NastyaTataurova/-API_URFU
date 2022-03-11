from flask import Flask, \
    json, Response
from flask_restful import reqparse, \
    abort, Api, Resource

app = Flask(__name__)
api = Api(app)

events = {}


def abort_404(todo_id):
    if todo_id not in events:
        abort(404, message="promo {} doesn't exist".format(todo_id))


parser = reqparse.RequestParser()
parser.add_argument('name')
parser.add_argument('description')
parser.add_argument('participant')
parser.add_argument('prize')


class promo(Resource):
    def get(self):
        dict_get_all_promos = {}
        for id_promo in events.keys():
            id_promo = int(id_promo)
            task = {'id': events[id_promo]['id'], 'name': events[id_promo]['name'],
                    'description': events[id_promo]['description']}
            dict_get_all_promos[id_promo] = task
        return dict_get_all_promos

    def post(self):
        args = parser.parse_args()
        id = int(max(events.keys())) + 1
        if args['name'] is None:
            abort(404, message="name is not defined")
        elif args['description'] is None:
            task = {'id': id, 'name': args['name'], 'description': None, 'participant': [],
                    'prizes': []}
        else:
            task = {'id': id, 'name': args['name'], 'description': args['description'], 'participant': [],
                    'prizes': []}
        events[int(id)] = task
        return id, 201


class promo_id(Resource):
    def get(self, id_promo: int):
        abort_404(id_promo)
        return events[id_promo]

    def delete(self, id_promo: int):
        abort_404(id_promo)
        del events[id_promo]
        return '', 204

    def put(self, id_promo: int):
        args = parser.parse_args()
        if id_promo in events.keys() and args['name'] is not None and args['description'] is not None:
            task = ({
                'id': id_promo,
                'name': args['name'],
                'description': args['description'],
                'participant': events[id_promo]['participant'],
                'prize': events[id_promo]['prize']
            })
        elif id_promo in events.keys() and args['name'] is not None:
            task = ({
                'id': id_promo,
                'name': args['name'],
                'description': None,
                'participant': events[id_promo]['participant'],
                'prize': events[id_promo]['prize']
            })
        else:
            abort(404, message="name is not defined")
        events[id_promo] = task
        return task, 201


class participant(Resource):
    def post(self, id_promo: int):
        args = parser.parse_args()
        if id_promo in events.keys():
            if len(events[id_promo]['participant']) >= 1:
                id_participant = int(events[id_promo]['participant'][-1]['id']) + 1
            else:
                id_participant = 1
            events[id_promo]['participant'].append({'id': id_participant, 'name': args['name']})
            return id, 201
        else:
            abort(404, message="name is not defined")


class participant_delete(Resource):
    def delete(self, id_promo: int, id_participant: int):

        abort_404(id_promo)

        for i, participant in enumerate(events[id_promo]['participant']):
            if id_participant == participant['id']:
                del events[id_promo]['participant'][i]
        return '', 204


class prize(Resource):
    def post(self, id_promo):
        args = parser.parse_args()
        id_promo = int(id_promo)
        if id_promo in events.keys():
            if len(events[id_promo]['prize']) >= 1:
                id_prize = int(events[id_promo]['prize'][-1]['id']) + 1
            else:
                id_prize = 1
            events[id_promo]['prize'].append({'id': id_prize, 'description': args['description']})
            return id_prize
        else:
            abort(404, message="name is not defined")


class prize_delete(Resource):
    def delete(self, id_promo: int, id_prize: int):
        abort_404(id_promo)
        for i, prize in enumerate(events[id_promo]['prize']):
            if id_prize == prize['id']:
                del events[id_promo]['prize'][i]

        return '', 204


class raffle(Resource):
    def get(self, id_promo: int):
        args = parser.parse_args()
        final_list = []
        if id_promo in events.keys():
            if len(events[id_promo]['prize']) == len(events[id_promo]['participant']):
                for i in range(len(events[id_promo]['prize'])):
                    final_list.append(
                        {
                            "winner": {
                            "id": events[id_promo]['participant'][i]['id'],
                            "name": events[id_promo]['participant'][i]['name']
                            },
                            "prize": {
                                "id": events[id_promo]['prize'][i]['id'],
                                "description": events[id_promo]['prize'][i]['description']
                            }
                        }
                    )
                return final_list
            else:
                abort(409, message="409 (Conflict)")
        else:
            abort(404, message="name is not defined")


api.add_resource(promo, '/promo')
api.add_resource(promo_id, '/promo/<id_promo>')
api.add_resource(prize, '/promo/<id_promo>/prize')
api.add_resource(participant, '/promo/<id_promo>/participant')
api.add_resource(prize_delete, '/promo/<id_promo>/prize/<id_prize>')
api.add_resource(participant_delete, '/promo/<id_promo>/participant/<id_participant>')
api.add_resource(raffle, '/promo/<id_promo>/raffle')


if __name__ == '__main__':
    app.run(debug=False, port=8080)
