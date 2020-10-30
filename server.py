import datetime as dt 
from flask import Flask, jsonify, request
import json
import random

CARRIAGE_COUNT          = 5 
SEATS_COUNT_IN_CARRIAGE = 15

Trains  = []
Clients = []
Seats   = []

classes  = ['econom', 'business']
statuses = ['free', 'sold', 'booked']
days_of_the_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

app = Flask(__name__)

# Считываем все данные из файликов
def read_data():
    read_clients()
    read_seats()
    read_trains()

def read_clients():
    global Clients
    try:
        f = open('clients.txt') 
        Clients = json.load(f)
        f.close()        
    except:
        print('Unable to load clients...')

def read_seats():
    global Seats 
    try:
        f = open('seats.txt') 
        Seats = json.load(f)
        f.close()
    except:
        print('Unable to load seats...')

def read_trains():
    global Trains
    try:
        f = open('trains.txt')
        Trains = json.load(f)
        f.close()
    except:
        print('Unable to load trains...')

# Записываем все данные в файлик
def store_data():
    store_clients()
    store_seats()
    store_trains()

def store_clients():
    with open('clients.txt', 'w') as outfile:
        json.dump(Clients, outfile)
        outfile.close()

def store_seats():
    with open('seats.txt', 'w') as outfile:
        json.dump(Seats, outfile)
        outfile.close()

def store_trains():
    with open('trains.txt', 'w') as outfile:
        json.dump(Trains, outfile)
        outfile.close()

@app.route('/', methods=['GET'])
def hello():
    return "HELLO, WORLD!"

#---------------- Работа с клиентами ----------------
@app.route('/clients', methods=['GET'])
def get_all_clients():
    return jsonify(Clients)

@app.route('/clients/<string:login>', methods=['GET'])
def get_client_by_login(login):
    return jsonify([x for x in Clients if x['login'] == login])

@app.route('/clients', methods=['POST'])
def post_client():
    client = request.form.to_dict(flat=True)
    print("\n", client, "\n")
    if len([x for x in Clients if x['login'] == client['login']]) != 0: return jsonify([])
    if client.keys() != {'firstname', 'lastname', 'login', 'password'}: return 'KEYS'
    client['id'] = str(random.randint(1, 10 ** 10))
    Clients.append(client)
    store_clients()
    return jsonify(client)

@app.route('/clients/<string:id>', methods=['DELETE'])
def delete_client_by_id(id):
    client_to_del = [x for x in Clients if x['id'] == id]
    if len(client_to_del) == 0: return 'ID IS NOT FOUND!'
    else:
        client_to_del = client_to_del[0]
        Clients.remove(client_to_del)
        store_clients()
        return jsonify(Clients)

@app.route('/clients/<string:id>', methods=['PUT'])
def put_client_by_id(id):
    client_to_update = [x for x in Clients if x['id'] == id][0]
    tmp =  request.form.to_dict(flat=True)
	
    client_to_update['firstname'] = tmp['firstname']
    client_to_update['lastname'] = tmp['lastname']
    client_to_update['password'] = tmp['password']
    client_to_update['login'] = tmp['login']
    store_clients()
    return jsonify(Clients)
# ----------------------------------------------------

# ---------------- Работа с местами ------------------
@app.route('/seats', methods=['GET'])
def get_all_seats():
    print(request.args)
    if len(request.args) == 0: return jsonify(Seats)
    client_id = request.args.get('client_id', default=None, type=None)
    train_id = request.args.get('train_id', default=None, type=None)
    print(type(client_id))
    if type(client_id) != type(None) and len(client_id) != 0: return jsonify(get_seat_by_client_id(client_id))
    elif type(train_id) != type(None) and len(train_id) != 0: return jsonify(get_seat_by_train_id(train_id))
    else: return jsonify({})

def get_seat_by_train_id(t_id):
    return [x for x in Seats if x['train_id'] == t_id]

def get_seat_by_client_id(c_id):
    return [x for x in Seats if x['client_id'] == c_id]

@app.route('/seats', methods=['POST'])
def post_seat():
    tmp = request.form.to_dict(flat=True)
    if tmp.keys() != {'train_id', 'client_id', 'seat', 'date', 'class', 'cost', 'status'}: return jsonify({}) 
    tmp['id'] = str(random.randint(1, 10 ** 10))
    Seats.append(tmp)
    store_seats()
    return jsonify(Seats)

@app.route('/seats/<string:id>', methods=['GET'])
def get_seat_by_id(id):
    return jsonify([x for x in Seats if x['id'] == id])

@app.route('/seats/<string:id>', methods=['DELETE'])
def delete_seats_by_id(id):
    seat_to_del = [x for x in Seats if x['id'] == id]
    if len(seat_to_del) == 0: return 'SEAT IS NOT FOUND!'
    else:
        seat_to_del = seat_to_del[0]
        Seats.remove(seat_to_del)
        store_seats()
        return jsonify(Seats)

@app.route('/seats/<string:id>', methods=['PUT'])
def put_seat_by_id(id):
    seat_to_put = [x for x in Seats if x['id'] == id][0]
    tmp = request.form.to_dict(flat=True)
    seat_to_put['train_id'] = tmp['train_id']
    seat_to_put['client_id'] = tmp['client_id']
    seat_to_put['seat'] = tmp['seat']
    seat_to_put['date'] = tmp['date']
    seat_to_put['class'] = tmp['class']
    seat_to_put['cost'] = tmp['cost']
    seat_to_put['status'] = tmp['status']
    store_seats()
    return jsonify(Seats)

# seat format C<NUMBER>S<NUMBER>, where C stands for Carriege and S stands for Seat
def create_new_seat(train_id, carriage, seat):
    tmp = {}
    tmp['id'] = str(random.randint(1, 10 ** 10))
    tmp['train_id'] = train_id
    tmp['client_id'] = None
    tmp['date'] = None
    tmp['class'] = classes[random.randint(1, 2) - 1]
    tmp['cost'] = str(random.randint(1, 10000))
    tmp['status'] = statuses[random.randint(1, 3) - 1]
    tmp['seat'] = 'C' + str(carriage) + 'S' + str(seat)
    return tmp
# ----------------------------------------------------

# --------------- Работа с поездами ------------------
@app.route('/trains', methods=['GET'])
def get_all_trains():
    return jsonify(Trains)

@app.route('/trains', methods=['POST'])
def post_train():
    tmp = request.form.to_dict(flat=True)
    if tmp.keys() != {'name', 'from', 'to'}: return jsonify({}) 
    tmp['id'] = str(random.randint(1, 10 ** 10))
    tmp['name'] = tmp['name'].upper()
    tmp['to'] = tmp['to'].upper()
    tmp['from'] = tmp['from'].upper()
    tmp['schedule'] = {}

    for i in range(CARRIAGE_COUNT):
        for j in range(SEATS_COUNT_IN_CARRIAGE):
            tmp_seat = create_new_seat(tmp['id'], i, j)
            Seats.append(tmp_seat)

    for wd in days_of_the_week:
        tmp['schedule'][wd] = create_schedule_list()

    Trains.append(tmp)
    store_trains()
    store_seats()
    return jsonify(Trains)


@app.route('/trains/<string:id>', methods=['GET'])
def get_train_by_id(id):
    return jsonify([x for x in Trains if x['id'] == id][0])


@app.route('/trains/<string:id>', methods=['DELETE'])
def delete_train_by_id(id):
    global Seats
    train_to_del = [x for x in Trains if x['id'] == id]
    if len(train_to_del) == 0: return 'TRAIN NOT FOUND!'
    else:
        tmp = [x for x in Seats if x['train_id'] != id]
        Seats = tmp
        Trains.remove(train_to_del)
        store_trains()
        store_seats()
        return jsonify(Trains)


@app.route('/trains/<string:id>', methods=['PUT'])
def put_train_by_id(id):
    train_to_put = [x for x in Trains if x['id'] == id][0]
    tmp = request.form.to_dict(flat=True)
    train_to_put['name'] = tmp['name']
    train_to_put['from'] = tmp['from']
    train_to_put['to'] = tmp['to']
    train_to_put['schedule'] = tmp['schedule']
    train_to_put['seats'] = tmp['seats']
    store_trains()
    return jsonify(Seats)


def create_schedule_list():
    n = random.randint(1, 6)
    res = []

    for i in range(n):
        h = str(random.randint(0, 23))
        m = str(random.randint(0, 59))
        if len(h) == 1: h = '0' + h
        if len(m) == 1: m = '0' + m
        res.append(h + ':' + m)

    return res
# ----------------------------------------------------



if __name__ == '__main__':
    read_data()
    app.run(host = "127.0.0.1", port = 36666)

