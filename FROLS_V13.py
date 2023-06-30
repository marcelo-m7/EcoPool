
'''
29-06-2023
legend
Text colm 1, HR colm 2, VelocVent colm 3, Pisc colm 4, Pisc_colet colm 5, Ts_colect colum6, Pisc_Pav colm 7, Pisc_ColecCob colm 8

'''
import calendar
import random
import pickle
import time
from tkinter import Text
import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sysidentpy.model_structure_selection import FROLS
from sysidentpy.basis_function._basis_function import Polynomial
from sysidentpy.metrics import root_relative_squared_error
from sklearn.metrics import mean_absolute_error
from sysidentpy.utils.display_results import results
import requests
from csv import writer
from datetime import datetime
import datetime

#################################################################################
#   Emon service info
emon_ip = "193.136.227.157"
emon_apikey = "95ca8292ee40f87f6ff0d1a07b2dca6f" # emon ecopool
node_id = "ecopool"
##################################################################################
API_KEY = "23ffbe727b2bee451d3dc7b37ad2b813"
cidade = "faro"
code = "351"
link = "https://api.openweathermap.org/data/2.5/forecast?q="+str(cidade)+"&appid="+str(API_KEY)
link_meteo = "https://api.open-meteo.com/v1/forecast?latitude=37.025408&longitude=-7.922246&hourly=temperature_2m,relativehumidity_2m,precipitation,windspeed_10m"

class Models:
    def __init__(self):
        self.lista_RRSE =[];self.lista_SSE = [];self.lista_MAPE = [];
        self.lista_y_hat = [];self.lista_y_hat1 = [];self.models=[];

#Defining MAPE function
def MAPE(Y_actual,Y_Predicted):
    mape = np.mean(np.abs((Y_actual - Y_Predicted)/Y_actual))*100
    return mape

def forecast(model, x_id, y_id, x_val,ph):
    X_id = copy.copy(x_id[-(model.max_lag + 1 ):,:])
    Y_id = copy.copy(y_id[-(model.max_lag + 1 ):])
    y_hat = np.zeros([ph,1],float)
    for i in range(ph):
        y_hat_total = model.predict(X_id, Y_id)
        y_hat_t = y_hat_total[model.max_lag]
        X_id [0:-1,:]= X_id[1:,:]
        X_id [-1,:] = x_val[i,:]
        Y_id [0:-1]= Y_id[1:]
        Y_id [-1] = y_hat_t
        y_hat[i]=y_hat_t
    return y_hat


# Parametros do emoncms
lista_feed_id = {'temp':939,'hr':940,'vel':941,'cen':945,'tpool':939}

def converter_data_unit(inicio):
    data_hora_atual = datetime.datetime.now()
    #data_hora_atual. = data_hora_atual.hour +1
    # Formatando a data e hora atual
    data_hora_formatada = data_hora_atual.strftime("%d-%m-%Y %H:%M:%S")
    data_hora_formatada = data_hora_formatada.replace("-", "/")
    data_hora_formatada_str = str(data_hora_formatada)
    #print(data_hora_formatada_str)
    # Converter a string em objeto datetime
    data_hora_obj = datetime.datetime.strptime(data_hora_formatada_str, "%d/%m/%Y %H:%M:%S")
    # Converter o objeto datetime em um número inteiro
    data_unixtime = int(data_hora_obj.timestamp())
    return data_unixtime
# Função utilizada para carregar dados
def carregar_dados_emoncms(ph, treino, inicio, fim):
    inicio = 0
    hora_desejada = 24
    fim = converter_data_unit(inicio)
    inicio = fim - 3600 * hora_desejada
    if treino == True:
        id_temp = lista_feed_id['temp']; id_hr = lista_feed_id['hr']; id_vel = lista_feed_id['vel']; id_cen = lista_feed_id['cen'];
        id_tpool=lista_feed_id['tpool']
        temp = "http://193.136.227.157/emoncms/feed/data.json?id=" + str(id_temp) + "&start=" + str(inicio) + "000&end=" + str(fim) + "000&interval=1800"
        hr = "http://193.136.227.157/emoncms/feed/data.json?id=" + str(id_hr) + "&start=" + str(inicio) + "000&end=" + str(fim) + "000&interval=1800"
        vel = "http://193.136.227.157/emoncms/feed/data.json?id=" + str(id_vel) + "&start=" + str(inicio) + "000&end=" + str(fim) + "000&interval=1800"
        tpool = "http://193.136.227.157/emoncms/feed/data.json?id=" + str(id_tpool) + "&start=" + str(inicio) + "000&end=" + str(fim) + "000&interval=1800"
        # faz a requisição para o emoncms
        requisicao_temp = requests.get(temp); requisicao_hr = requests.get(hr);requisicao_vel = requests.get(vel); requisicao_tpool = requests.get(tpool)
        #armazena os valores solicitado nas variaveis correspondentes
        text = requisicao_temp.json(); hr = requisicao_hr.json(); vel = requisicao_vel.json(); tpool = requisicao_tpool.json()
        tamanho = len(text)
        #Converter valores das variaveis externas para formato array
        text_array = np.array(text); hr_array = np.array(hr); vel_array = np.array(vel)
        tpool_array = np.array(tpool)
        fim_treino = ph
        x_id = np.array([text_array[0:-fim_treino, 1], hr_array[0:-fim_treino, 1], vel_array[0:-fim_treino, 1]]).transpose().reshape(tamanho - fim_treino, 3)
        x_val = np.array([text_array[-fim_treino - 15:, 1], hr_array[-fim_treino - 15:, 1],vel_array[-fim_treino - 15:, 1]]).transpose().reshape(ph + 15, 3)

        y_id = np.array([tpool_array[0:-fim_treino, 1]]).reshape(tamanho - fim_treino, 1)
        y_val = np.array([tpool_array[-fim_treino - 15:, 1]]).reshape(ph + 15, 1)

    else:
        #Faz requisição dos dados no emomcms das varias externas
        id_temp = lista_feed_id['temp']; id_hr = lista_feed_id['hr']; id_vel = lista_feed_id['vel'];id_tpool=lista_feed_id['tpool']
        #determinar o dia atual e hora - será a variavel da data de fim(2023-06-13 00:00:00)
        inicio = 0
        hora_desejada = 24
        fim = converter_data_unit(inicio)
        inicio = fim - 3600 * hora_desejada
        temp = "http://193.136.227.157/emoncms/feed/data.json?id=" + str(id_temp) + "&start=" + str(inicio) + "000&end=" + str(fim) + "000&interval=1800"
        hr = "http://193.136.227.157/emoncms/feed/data.json?id=" + str(id_hr) + "&start=" + str(inicio) + "000&end=" + str(fim) + "000&interval=1800"
        vel = "http://193.136.227.157/emoncms/feed/data.json?id=" + str(id_vel) + "&start=" + str(inicio) + "000&end=" + str(fim) + "000&interval=1800"
        tpool = "http://193.136.227.157/emoncms/feed/data.json?id=" + str(id_tpool) + "&start=" + str(inicio) + "000&end=" + str(fim) + "000&interval=1800"
        #faz a requisição para o emoncms
        requisicao_temp = requests.get(temp); requisicao_hr = requests.get(hr); requisicao_vel = requests.get(vel);requisicao_tpool = requests.get(tpool)
        #armazena os valores solicitado nas variaveis correspondentes
        text = requisicao_temp.json(); hr = requisicao_hr.json(); vel = requisicao_vel.json();tpool = requisicao_tpool.json()
        tamanho = len(text)
        #Converter valores das variaveis externas para formato array
        text_array = np.array(text);hr_array = np.array(hr);vel_array = np.array(vel);tpool_array = np.array(tpool)
        #Juntar as variaveis externas numa matrix com 3 colunas e varias linhas conforme o tamanho na variavel x_id
        x_id = np.array([text_array[:, 1], hr_array[:, 1],vel_array[:, 1]]).transpose().reshape(tamanho, 3)

        #faz a requisição para o site(api)
        requisicao_meteo = requests.get(link_meteo)
        #armazena os valores solicitado num dicionario
        requisicao_dic_meteo = requisicao_meteo.json()

        #armazena os valores solicitado nas variaveis correspondentes
        data = requisicao_dic_meteo['hourly']['time'];
        temperature = requisicao_dic_meteo['hourly']['temperature_2m'];
        windspeed = requisicao_dic_meteo['hourly']['windspeed_10m'];
        relativehumidity = requisicao_dic_meteo['hourly']['relativehumidity_2m'];
        #Converter valores das variaveis externas para formato array
        tamanho = len(temperature)
        text_forecast = np.array(temperature).reshape(tamanho,1); hr_forecast = np.array(relativehumidity).reshape(tamanho,1); windspeed_forecast = np.array(windspeed).reshape(tamanho,1);
        x_val_ph = np.array([text_forecast[-12:], hr_forecast[-12:], windspeed_forecast[-12:]]).transpose().reshape(12, 3)

        # concatenar com os valores do x_val com x_val_ph
        x_val = np.array([text_array[-15:, 1], hr_array[-15:, 1],vel_array[- 15:, 1]]).transpose().reshape(15, 3)
        x_val_total=np.concatenate([x_val,x_val_ph],axis=0)

        previsto_array = text_array
        tamanho = len(previsto_array)
        x_val = x_val_total
        fim_treino = ph
        y_id = np.array([previsto_array[:, 1]]).reshape(tamanho, 1)
        y_val = np.array([tpool_array[-fim_treino - 15:, 1]]).reshape(ph + 15, 1)

    return x_id, x_val, y_id, y_val

if __name__ == "__main__":
    train = False
    if train == False:
            lista_modelos = Models()
            #ler o ficheiro csv e as UNIXTIME respetivas para cada cenario (que esta na 1º coluna)
            registro_var = pd.read_csv(r'files/registro_variaveis.csv', header=None,names=['Inicio', 'Cenario', 'Duration'])
            registro_var.shape

            for cont in range(0,4):
                #substituir inicio e fim pela leitura direta de cada linha do ficheiro
                    inicio = registro_var.values[cont, 0]
                    fim = inicio + registro_var.values[cont, 2]
                    ph = 24
                    (x_id, x_val, y_id,y_val) = carregar_dados_emoncms(ph, True , inicio, fim)
                    # variaveis para fazer append
                    lista_rrse = [];lista_sse = [];lista_MAPE = [];modelos_cenario = [];
                    lista_y_hat = [];lista_y_hat1 = [];
                    tamanho = 2
                    for i in range(tamanho):
                        a = random.randint(1,11);b = random.randint(1,11);c = random.randint(1,11);d = random.randint(1,11);
                        # Setting the input lags
                        x1lag = list(range(1,a+1));x2lag = list(range(1,b+1));x3lag = list(range(1,c+1));x3lag
                        # Model training and evalutation
                        basis_function = Polynomial(degree=1)
                        model = FROLS(
                            order_selection=True,
                            n_info_values=30,
                            extended_least_squares=False,
                            ylag=d, xlag=[x1lag, x2lag, x3lag],
                            info_criteria='bic',
                            estimator='least_squares',
                            basis_function=basis_function
                        )
                        model.fit(X=x_id, y=y_id)

                        y_hat_1 = model.predict(x_val[-model.max_lag-ph:], y_val[-model.max_lag-ph:])
                        y_hat1=y_hat_1[-ph:]
                        y_hat = np.zeros([ph,1])

                        y_forecast_1 = forecast(model, x_id[-40:,:], y_id[-40:], x_val, ph)
                        y_hat = y_forecast_1

                        rrse = root_relative_squared_error(y_val[-ph:], y_hat) # sysidentpy.metrics
                        sse = mean_absolute_error(y_val[-ph:], y_hat) # sklearn.metrics

                        val_mape=MAPE(y_val[-ph:], y_hat)
                        # fazer append dessas variaves
                        lista_MAPE.append(val_mape);lista_rrse.append(rrse);lista_sse.append(sse);
                        lista_y_hat.append(y_hat);lista_y_hat1.append(y_hat1);modelos_cenario.append(model);
                        r = pd.DataFrame(
                            results(
                                model.final_model, model.theta, model.err,
                                model.n_terms, err_precision=8, dtype='sci'
                            ),
                            columns=['Regressors', 'Parameters', 'ERR'])
                        print(r)
                        xaxis = np.arange(1, ph + 1)
                        plt.plot(xaxis,y_hat1)
                        plt.plot(xaxis, y_hat)
                        plt.xlabel('Steps')
                        plt.ylabel('Previsão')
                        plt.show()
                        #Gravar em ficheiro

                    indice_melhor = lista_MAPE.index(min(lista_MAPE))
                    print('Calculo de RRSE utilizando sysidentpy.metrics: {} '.format(lista_rrse))
                    print('Calculo de SSE utilizando sklearn.metric: {} '.format(lista_sse))
                    print('Calculo do Erro MAPE: {} '.format(lista_MAPE))
                    print('Menores valores: RRSE SSE MAPE: {} {} {}'.format(min(lista_rrse),min(lista_sse),min(lista_MAPE)))

                    #regista o melhor modelo poara cada cenario
                    lista_modelos.lista_RRSE.append(lista_rrse[indice_melhor]);
                    lista_modelos.lista_SSE.append(lista_sse[indice_melhor]);
                    lista_modelos.lista_MAPE.append(lista_MAPE[indice_melhor]);
                    lista_modelos.lista_y_hat.append(lista_y_hat[indice_melhor]);
                    lista_modelos.lista_y_hat1.append(lista_y_hat1[indice_melhor]);
                    lista_modelos.models.append(modelos_cenario[indice_melhor]);

                # guardar modelo treinado para este cenario na posição da lista de modelo correta
            lista_modelos.models[registro_var.values[cont, 1]] = model

            modelos_file = open("dados_modelos.pkl", 'wb')
            pickle.dump(lista_modelos, modelos_file)
            modelos_file.close()

    else:
        # Recuperar os modelos
        modelos_file = open("dados_modelos.pkl", 'rb')
        modelos = pickle.load(modelos_file)
        modelos_file.close()
        mape = modelos.lista_MAPE; sse = modelos.lista_SSE;rrse = modelos.lista_RRSE;
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #system_scheduling = np.ones([1,6])
        system_scheduling = [1,2,3,4]
        #system_scheduling = [1, 1, 2, 2, 3, 3]
        n_times = len(system_scheduling)
        step = 0; ph= 4;
        inicio = calendar.timegm(time.strptime('2023-06-29 00:00:00', '%Y-%m-%d %H:%M:%S'))
        fim = calendar.timegm(time.strptime('2023-06-29 16:00:00', '%Y-%m-%d %H:%M:%S'))
        (x_id, x_val, y_id, y_val) = carregar_dados_emoncms(ph, False, inicio, fim)
        while step < n_times:
            y_forecast_1 = forecast(modelos.models[step], x_id[-15:, :], y_id[-15:], x_val, 1)
            print(f"{step}º: {y_forecast_1}")
            step = step + 1





