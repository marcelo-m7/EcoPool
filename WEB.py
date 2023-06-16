import os.path
from http import client
from tkinter import Tk, Label, W, Entry, Button, mainloop
import requests
from csv import writer
from math import trunc
from pymodbus.client import ModbusTcpClient
from flask import Flask, g, redirect, render_template, request, session, url_for

client = ModbusTcpClient("192.168.1.3", timeout=3)
x = client.connect()
print('Connect? ', x)

# Emon service info
emon_ip = "193.136.227.157"
emon_apikey = "95ca8292ee40f87f6ff0d1a07b2dca6f"  # emon ecopool
node_id = "ecopool"

class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'

users = []
users.append(User(id=1, username='client', password='password'))
users.append(User(id=2, username='admin', password='admin'))
users.append(User(id=3, username='jailson', password='password'))

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']

        user = [x for x in users if x.username == username][0]
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('profile'))

        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/menu')
def profile():
    if not g.user:
        return redirect(url_for('login'))

    return render_template('menu.html')

@app.route("/write_plc", methods=['GET', 'POST'])
def write_plc():
    if request.method == 'POST':
        setpoint = request.form.get('setpoint')
        diferencial = request.form.get('diferencial')
        cenario = request.form.get('cenario')
        fator = 10

        if setpoint is not None and diferencial is not None:
            if setpoint.find('.') != -1:
                inteiro = setpoint[0:setpoint.find('.')]
                decimal = setpoint[setpoint.find('.') + 1:]
                setpoint = int(inteiro) * fator + int(decimal)
                ddiferencial = int(diferencial)
                ccenario = int(cenario)
            else:
                setpoint = int(setpoint) * fator
                ddiferencial = int(diferencial) * fator
                ccenario = int(cenario) * fator

            nregistro1 = 58  # number register for setpoint
            nregistro2 = 59  # number register for diferencial
            nregistro206 = 60  # number register for cenario
            nregistro59 = client.write_register(nregistro1, setpoint)
            nregistro60 = client.write_register(nregistro2, ddiferencial)
            nregistro206 = client.write_register(nregistro206, ccenario)

            data_json = '{"Setpoint":' + str(setpoint) + ',"Diferencial":' + str(ddiferencial) + ',"Cenario":' + str(
                ccenario) + '}'
            emon_link = 'http://' + emon_ip + '/emoncms/input/post?node=' + node_id + '&fulljson=' + str(
                data_json) + "&apikey=" + str(emon_apikey)
            pedido = requests.get(emon_link)

            registro_variaveis = 'registro_variaveis.csv'
            with open(registro_variaveis, 'a', newline='') as dados:
                writer_object = writer(dados)
                writer_object.writerow([data_json])

    return render_template('write_plc.html')

@app.route("/read_plc", methods=['GET'])
def read_plc():
    if request.method == 'GET':
        read = client.read_holding_registers(address=57, port=502, count=9, unit=1)
        leitura = read.registers  # dados de todas as leituras
        fator = 10
        setpoint = read.registers[1]
        diferencial = read.registers[2]
        cenario = read.registers[3]
        print(setpoint, diferencial, cenario)
        print(leitura)
        set_point = trunc(int(setpoint) / 10)  # trunc pega apenas parte inteiro do valor
        cena_rio = trunc(int(cenario) / 10)
        differencial = trunc(int(diferencial) / 10)

    return render_template('read_plc.html', setpoint=set_point, diferencial=differencial, cenario=cena_rio)

@app.route("/read_emcms", methods=['GET'])
def read_emcms():
    temperaturaExtt = "http://193.136.227.157/emoncms/feed/value.json?id=939&apikey=95ca8292ee40f87f6ff0d1a07b2dca6f"
    velocidadeExtt = "http://193.136.227.157/emoncms/feed/value.json?id=941&apikey=95ca8292ee40f87f6ff0d1a07b2dca6f"
    humidadeExtt = "http://193.136.227.157/emoncms/feed/value.json?id=940&apikey=95ca8292ee40f87f6ff0d1a07b2dca6f"
    setpoint = "http://193.136.227.157/emoncms/feed/value.json?id=943&apikey=95ca8292ee40f87f6ff0d1a07b2dca6f"
    cenario = "http://193.136.227.157/emoncms/feed/value.json?id=945&apikey=95ca8292ee40f87f6ff0d1a07b2dca6f"

    request5 = requests.get(temperaturaExtt)
    request6 = requests.get(velocidadeExtt)
    request7 = requests.get(humidadeExtt)
    request8 = requests.get(setpoint)
    request9 = requests.get(cenario)

    temperaturaExt = float(request5.content)
    velocidadeExt = float(request6.content)
    humidadeExt = int(request7.content)
    set_point = trunc(int(request8.content) / 10)  # trunc pega apenas parte inteiro do valor
    cena_rio = trunc(int(request9.content) / 10)

    return render_template('read_emcms.html', msg4=temperaturaExt, msg6=velocidadeExt, msg7=humidadeExt,
                           msg8=set_point, msg9=cena_rio)

@app.route("/historico", methods=['GET'])
def historico():
    return render_template("historico.html")

@app.route('/menu', methods=['GET'])
def menu():
    return render_template('menu.html')

@app.route("/register", methods=['GET'])
def register():
    return render_template("register.html")

app.run(port=5000, host='localhost', debug=True)
