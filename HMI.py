'''
22-05-2023
programa que permite escrever  atravez da interface tkinter os seguintes valores:
EV2 Aquecimento CG Setpoint: ',input58,'ºC'
EV2 Aquecimento Differencial: ',input59,'ºC'

'''
import requests
from tkinter import *
from tkinter import Tk, ttk
from tkinter import messagebox
from pymodbus3.client.sync import ModbusTcpClient
from flask import Flask, request

#################################################################################
#   Emon service info
emon_ip = "193.136.227.157"
emon_apikey = "95ca8292ee40f87f6ff0d1a07b2dca6f" # emon ecopool
node_id = "ecopool"
##################################################################################

client = ModbusTcpClient("192.168.1.3", timeout=3)
x = client.connect()
print('Connect? ',x)
# criando janela -----------------------------------------------------------
janela = Tk()
janela.title('Interface HMI')
janela.geometry('310x300')
janela.configure(background='#feffff')
janela.resizable(width=False, height=False)

# Dividindo a janela --------------------------------------------------------
#frame_cima = Frame(janela, width=310, height=50, bg='#feffff', relief='flat')
frame_cima = Frame(janela, width=310, height=50, bg='black', relief='flat')
frame_cima.grid(row=0, column=0, pady=1, padx=0, sticky=NSEW)
#frame_baixo = Frame(janela, width=310, height=250, bg='#feffff', relief='flat')
frame_baixo = Frame(janela, width=310, height=250, bg='black', relief='flat')
frame_baixo.grid(row=1, column=0, pady=1, padx=0, sticky=NSEW)
# Configurando frame de cima ---------------------------------------------------------
l_nome = Label(frame_cima, text = 'Login', anchor=NE, font=('Ivy 25'),bg='black', fg='white')
l_nome.place(x=5, y=5)
l_linha = Label(frame_cima, text = '',width=275, anchor=NW, font=('Ivy 1'),bg='black', fg='white')
l_linha.place(x=10, y=45)
# criar credencias ------------------------------
credenciais = ['client', '123456789', 'admin', 'admin']

# função para verificar senha-------------------------
def verificar_senha():
    user = e_nome.get()
    password = e_pass.get()
    if credenciais[0] == user and credenciais[1] == password:
        messagebox.showinfo('login', 'seja bem vindo !!!'+credenciais[0])
        # apagar o que tiver no frame baixo e cima ----
        for widget in frame_baixo.winfo_children():
            widget.destroy()
        for widget in frame_cima.winfo_children():
            widget.destroy()
        nova_janela()
    elif    credenciais[2] == 'admin' and credenciais[3] == 'admin':
        messagebox.showinfo('login', 'seja bem vindo !!!' +credenciais[2])
        # apagar o que tiver no frame baixo e cima ----
        for widget in frame_baixo.winfo_children():
            widget.destroy()
        for widget in frame_cima.winfo_children():
            widget.destroy()
        nova_janela2()
    else:
        messagebox.showerror('Erro', 'verifique o nome e a senha!')
#-------------------função para criar nova janela -----------------------
def nova_janela():
    l_nome = Label(frame_cima, text='User : ' +credenciais[0], anchor=NE, font=('Ivy 10'), bg='black', fg='white')
    l_nome.place(x=5, y=5)
    l_linha = Label(frame_cima, text='', width=275, anchor=NW, font=('Ivy 1'), bg='black', fg='white')
    l_linha.place(x=10, y=45)
    l_nome = Button(frame_baixo, text=' Read Value in plc', anchor=NE, font=('Ivy 10'), bg='black', fg='white', command =read_plc)
    l_nome.grid()
    l_nome2 = Button(frame_baixo, text='Back',anchor=NE, font=('Ivy 10'), bg='black', fg='white', command='')
    l_nome2.grid()
#-------------------função para criar nova janela2 -----------------------
def nova_janela2():
    global ssetpoint, ddiferencial, ccenario
    l_nome = Label(frame_cima, text='User : ' +credenciais[2], anchor=NE, font=('Ivy 10'), bg='black', fg='white')
    l_nome.place(x=5, y=5)
    l_linha = Label(frame_cima, text='', width=275, anchor=NW, font=('Ivy 1'), bg='black', fg='white')
    l_linha.place(x=10, y=45)

    l1 = Label(janela, text="Setpoint [ºC]", bg='black',foreground='white')
    l1.place(x=10, y = 60)
    ssetpoint = Entry(janela)
    ssetpoint.place(x=155, y = 60)
    l2 = Label(janela, text="Diferencial [ºC]", bg='black',foreground='white')
    l2.place(x=10, y=80)
    ddiferencial = Entry(janela)
    ddiferencial.place(x=155, y=80)
    l3 = Label(janela, text="Cenario", bg='black',foreground='white')
    l3.place(x=10, y=100)
    ccenario = Entry(janela)
    ccenario.place(x=155, y=100)

    btn1 = Button(frame_baixo, text='Write in plc', bg='grey', fg='black', command=write_plc)
    btn1.place(x=100, y=80)
    btn2 = Button(frame_baixo, text='On', bg='grey', fg='black', command='')
    btn2.place(x=100, y=110)
    btn2 = Button(frame_baixo, text='Off', bg='red', fg='black', command='')
    btn2.place(x=130, y=110)
    btn3 = Button(frame_baixo, text='Back', bg='grey', fg='black', command='')
    btn3.place(x=100, y=140)

'''função permite escrever informação no autómato'''
def write_plc():
    global ssetpoint, ddiferencial, ccenario
    setpoint = ssetpoint.get()
    diferencial = ddiferencial.get()
    cenario = ccenario.get()
    fator = 10
    if setpoint is not None and diferencial is not None:
        if setpoint.find('.') != -1:
            inteiro = setpoint[0:setpoint.find('.')]
            decimal = setpoint[setpoint.find('.') + 1:]
            setpoint = int(inteiro) * fator + int(decimal)
            diferencial = int(diferencial) * fator
            cenario = int(cenario) * fator
            nregistro1 = 58  # number register for setpoint
            nregistro2 = 59  # number register for diferencial
            nregistro206 = 60  # number register for cenario
            nregistro59 = client.write_register(nregistro1, setpoint)
            nregistro60 = client.write_register(nregistro2, diferencial)
            nregistro206 = client.write_register(nregistro206, cenario)
        else:
            setpoint = int(setpoint) * fator
            diferencial = int(diferencial) * fator
            cenario = int(cenario) * fator
            nregistro1 = 58  # number register for setpoint
            nregistro2 = 59  # number register for diferencial
            nregistro206 = 60  # number register for cenario
            nregistro59 = client.write_register(nregistro1, setpoint)
            nregistro60 = client.write_register(nregistro2, diferencial)
            nregistro206 = client.write_register(nregistro206, cenario)
    data_json = '{"Setpoint":' + str(setpoint) + ',"Diferencial":' + str(diferencial) + ',"Cenario":' + str(cenario) + '}'
    emon_link = 'http://' + emon_ip + '/emoncms/input/post?node=' + node_id + '&fulljson=' + str(data_json) + "&apikey=" + str(emon_apikey)
    pedido = requests.get(emon_link)

######################################################################################################################################################################
'''função permite ler informação no autómato'''
def read_plc():
        read = client.read_holding_registers(address=57, port=502, count=9, unit=1)
        leitura = read.registers  # dados de todas as leituras
        fator = 10
        setpoint = read.registers[1]
        diferencial = read.registers[2]
        cenario = read.registers[3]
        texto_resposta['text'] = f'''
            Setpoint(ºC)= {setpoint}
            Diferencial (ºC)= {diferencial}
            Cenario = {cenario}'''

# Configurando frame de baixo ---------------------------------------------------------
l_nome = Label(frame_baixo, text = 'User', anchor=NW, font=('Ivy 10'),bg='black', fg='white')
l_nome.place(x=10, y=20)
e_nome = Entry(frame_baixo, width = 25, justify ='left', font = ('', 15), highlightthickness=1, relief ='solid')
e_nome.place(x = 14, y = 50)
l_pass = Label(frame_baixo, text = 'Password', anchor=NW, font=('Ivy 10'),bg='black', fg='white')
l_pass.place(x=10, y=95)
e_pass = Entry(frame_baixo, width = 25, justify ='left',show='*', font = ('', 15), highlightthickness=1, relief ='solid')
e_pass.place(x = 14, y = 130)
b_confirmar = Button(frame_baixo, command= verificar_senha, text = 'Entrar', width = 39, height = 2,font=('Ivy 8 bold'),bg='grey', fg='white', relief = RAISED, overrelief = RIDGE)
b_confirmar.place(x=15, y=180)
texto_resposta = Label(janela, text="",bg='white')
texto_resposta.grid()

janela.mainloop()