#!/usr/bin/python3
import requests

days_of_the_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

class Server:
    def __init__(self, url):
        self.url = url
        self.client_url = url + '/clients'
        self.trains_url = url + '/trains'
        self.seats_url  = url + '/seats'
        self.headers = {'Content-Type' : 'application/x-www-form-urlencoded'}
        self.current_client = {}
        self.all_trains = [] 
        self.seats = []
    
    def post_client(self, client):
        to_send = [(k, client[k]) for k in client]
        print(to_send)
        response = requests.post(self.client_url, data = to_send, headers = self.headers)
        if response.status_code != 200: raise NameError("Can't send POST request")
        #self.current_client = response.json()
        elif len(response.json()) == 0: return False
        else:
            self.current_client = response.json()
            return True

    def get_client(self, login):
        response = requests.get(self.client_url + "/" + login)
        if response.status_code != 200: raise NameError("No user like that")
        elif len(response.json()) == 0: return False 
        else: 
            self.current_client = response.json()[0]
            return True
    
    def get_all_trains(self):
        self.all_trains = requests.get(self.trains_url).json()
        if len(self.all_trains) == 0: raise NameError("Can't get list of trains, maybe it's empty.")
    
    def get_seats_by_train_id(self, train_id):
        response = requests.get(self.seats_url + '?train_id=' + train_id)
        if response.status_code != 200: raise NameError("Can't send GET request for seats")
        else: self.seats = response.json()
    
    def update_seat(self, seat):
        data_to_send = [(k, seat[k]) for k in seat]
        response = requests.put(self.seats_url + '/' + seat['id'], data = data_to_send, headers = self.headers)
        if response.status_code != 200: raise NameError("Can't send PUT request")
        self.seats = response.json()
    
    def get_seats_by_client_id(self):
        response = requests.get(self.seats_url + '?client_id=' + self.current_client['id'])
        if response.status_code != 200: raise NameError("Can't send GET request for seats")
        else: return response.json()
    
def registration():
    client = {}
    client['firstname'] = input('Введите имя: ')
    client['lastname']  = input('Введите фамилию: ')
    client['login']     = input('Придумайте логин: ')
    client['password']  = input('Придумайте пароль: ')
    return server.post_client(client)

def login():
    while server.get_client(input("Введите логин: ")) == False:
        server.get_client(input("Введите логин: "))

    password = input("Введите пароль: ")
    while password != server.current_client['password']:
        password = input("Пароль введен неверно. Попробуйте ещё раз: ")

def show_trains_list():
    server.get_all_trains()
    display_trains(server.all_trains)

def show_schedule_of_train():
    server.get_all_trains()
    train_id = input("Введите номер поезда: ")
    train_schedule = [x for x in server.all_trains if x['id'] == train_id]

    if len(train_schedule) == 0:
        print("Поезда с таким номером нет. Введите другой номер.")
        return
        #train_schedule = [x for x in server.all_trains if x['id'] == input("Поезда с таким номером нет. Введите другой номер: ")]

    train_schedule = train_schedule[0]['schedule']
    print("\nРасписание поезда №" + train_id)
    print('  ПОН  |  ВТР  |  СРД  |  ЧТВ  |  ПТН  |  СБТ  |  ВСК  ')
    print('-' * 55)
    
    max_times = max([len(train_schedule[x]) for x in train_schedule])

    # print(train_schedule)

    for i in range(max_times):
        put_str = ''
        for wd in days_of_the_week:
            put_str += ' ' +  train_schedule[wd][i] + ' ' if i < len(train_schedule[wd]) else ' ' * 7
            put_str += '|' if wd != 'sunday' else ''
        print(put_str)

def show_seats():
    train_id = input("Введите номер поезда: ")
    server.get_seats_by_train_id(train_id)

    if len(server.seats) == 0:
        print("Поезда с таким номером нет. Введите другой номер.")
        return
    
    #while len(server.seats) == 0:
     #   server.get_seats_by_train_id(input("Билета с таким номером нет. Введите другой номер: "))
    
    print("Показать места: 1. Свободные 2. Купленные 3. Забронированные")
    seat_status = ['free', 'booked', 'sold'][int(input()) - 1]

    display_seats([x for x in server.seats if x['status'] == seat_status])

def display_seats(mas):
    if len(mas) == 0:
        print("Пока что нет мест/билетов. ")
        return

    max_status_len = max([len(x['status']) for x in mas])
    max_seat_len   = max([len(x['seat'])   for x in mas])
    max_cost_len   = max([len(x['cost'])   for x in mas])
    max_class_len  = max([len(x['class'])  for x in mas])
    max_len = max_cost_len + max_seat_len + max_class_len + max_status_len + 2 * 4 + 3

    print('-' * max_len)
    put_str = ''
    put_str += ' Статус'+ ' ' * max(max_status_len - 6, 0)
    put_str += ' | Номер' + ' ' * max(0, max_seat_len - 5)  
    put_str += ' | Цена' + ' ' * max (max_cost_len - 4, 0) 
    put_str += ' | Класс' + ' ' * max(0, max_class_len - 5)
    print(put_str)
    
    for s in mas:
        print(' ' + s['status'] + ' ' * max(max_status_len- len(s['status']) , 0) + ' | ' + s['seat']  + ' ' * max(0, max_seat_len - len(s['seat'])) + ' | '+ s['cost'] + ' ' * max (max_cost_len - len(s['cost']), 0) + ' | ' + s['class'] + ' ' * max(0, max_class_len - len(s['class'])))
    
    print('-' * max_len)

def display_trains(lst):
    if len(lst) == 0:
        print("Пока что нет поездов :(")
        return 
    max_len_name = max([len(x['name']) for x in lst])
    max_len_from = max([len(x['from']) for x in lst])
    max_len_to = max([len(x['to']) for x in lst])
    max_len_id = max([len(x['id']) for x in lst])

    max_len = 2 * 4 + 3 + max_len_name + max_len_id + max_len_to + max_len_from

    print('-' * max_len)
    print(' Номер'+ ' ' * max(max_len_id - 5, 0) + ' | Имя' + ' ' * max(0, max_len_name - 3) + ' | Откуда' + ' ' * max (max_len_from - 6, 0) + ' | Куда' + ' ' * max(0, max_len_to - 4))

    for train in lst:
        print(' ' + train['id'] + ' ' * max(max_len_id - len(train['id']) , 0) + ' | ' + train['name']  + ' ' * max(0, max_len_name - len(train['name'])) + ' | '+ train['from'] + ' ' * max (max_len_from - len(train['from']), 0) + ' | ' + train['to'] + ' ' * max(0, max_len_to - len(train['to'])))
    
    print('-' * max_len)

def show_trains_by_route():
    server.get_all_trains()
    dest_city = input("Введите город, в который хотите попасть: ").upper()
    source_city = input("Введите город, откуда поедем: ").upper()
    tmp  = set([x['id'] for x in server.all_trains if x['to'] == dest_city])
    tmp |= set([x['id'] for x in server.all_trains if x['from'] == source_city])
    trains_to_display = [x for x in server.all_trains if x['id'] in tmp]
    display_trains(trains_to_display)

def check_date(date):
    for c in date:
        if c.isalpha(): return False

    tmp = date.split('.')
    if len(tmp) != 3: return False
    if int(tmp[1]) > 12 or int(tmp[2]) > 31: return False 
    return True

def show_my_tickets():
    display_seats(server.get_seats_by_client_id())

def get_ticket():
    # train
    train_id = input("Введтие номер поезда: ")
    server.get_seats_by_train_id(train_id)

    if len(server.seats) == 0:
        print("Поезда с таким номером нет. Введите другой номер.")
        return

    #while len(server.seats) == 0:
     #   server.get_seats_by_train_id(input("Поезда с таким номером нет. Введите другой номер: "))
        
    display_seats([x for x in server.seats if x['status'] == 'free']) 
    seat = input("Выберите место (укажите номер): ").upper()
    while seat not in [x['seat'] for x in server.seats if x['status'] == 'free']:
        seat = input("Выберите место (Укажите номер): ").upper()
    
    date = input("Введите дату отправления в формате YYYY.MM.DD: ")
    while check_date(date) == False: 
        date = input("Введите дату отправления в формате YYYY.MM.DD: ")

    seat_to_update = [x for x in server.seats if x['seat'] == seat][0]
    seat_to_update['client_id'] = server.current_client['id']
    seat_to_update['date'] = date
    seat_to_update['status'] = 'sold'
    
    server.update_seat(seat_to_update)
    print("Билет успешно приобретен!")

def users_actions():
    while True:
        print('\n')
        print("1. Просмотр всех поездов   2. Просмотр расписаний поезда   3. Поиск поезда по маршруту")
        print("4. Просмотр мест в поезде   5. Заказ билета   6. Мои билеты   0. Выxод")
        choise = input()

        if choise == '1':
            show_trains_list()
        elif choise == '2':
            show_schedule_of_train()
        elif choise == '3':
            show_trains_by_route()
        elif choise == '4':
            show_seats()
        elif choise == '5':
            get_ticket()
        elif choise == '6':
            show_my_tickets()
        elif choise == '0': return 
        else: print('Команда не распознанна')

server = Server('http://127.0.0.1:36666')

def main():
    print('Добро пожаловать в ЖД Кассу!')
    print('Войдите или зарегистрируйтесь, чтобы приобретать билеты, смотреть расписания поездов и прочее.')

    while True:
        print('1. Регистрация   2. Bход   3. Выxод')
        choise = input()
        if choise == '1':
            if registration() == True:
                users_actions()
            else:
                print("Такой логин уже есть!")
        elif choise == '2':
            login()
            users_actions()
        elif choise == '3': return
        else: print('Команда не распознана. Введите заново.')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(str(e))
