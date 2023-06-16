
'''
legend
Text colm 1, HR colm 2, VelocVent colm 3, Pisc colm 4, Pisc_colet colm 5, Ts_colect colum6, Pisc_Pav colm 7, Pisc_ColecCob colm 8

'''
import random
import pickle
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

data_e_hora_atuais = datetime.now()
data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
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
# def download_file():
#     requisicao = requests.get(link)  # faz a requisição para o site(api)
#     requisicao_dic = requisicao.json()  # armazena os valores solicitado num dicionario
#
#     temp = requisicao_dic['list'][0]['main']['temp'] - 273.15
#     humidade = requisicao_dic['list'][0]['main']['humidity']
#     veloc_vent = ((requisicao_dic['list'][0]['wind']['speed']) / (1000)) * 3600
#     velocidade = '{:.0f}'.format(veloc_vent)
#     temperatura = '{:.0f}'.format(temp)
#
#     # enviar para emoncms
#     data_json = '{"TemperaturaExt":' + str(temperatura) + ',"HumidadeExt":' + str(humidade) + ',"VelocidadeExt":' + str(velocidade) + '}'
#     emon_link = 'http://' + emon_ip + '/emoncms/input/post?node=' + node_id + '&fulljson=' + str(data_json) + "&apikey=" + str(emon_apikey)
#     request = requests.get(emon_link)
#     list_data = [data_e_hora_em_texto, temperatura, velocidade, humidade]
#
#     with open('C:/Users/Jailson/PycharmProjects/TESTES/ecopol/files/files2.csv', 'a', newline='') as f_object:
#         # Pass the CSV  file object to the writer() function
#         writer_object = writer(f_object)
#         # Result - a writer object
#         # Pass the data in the list as an argument into the writerow() function
#         writer_object.writerow(list_data)
#         # Close the file object
#         f_object.close()

if __name__ == "__main__":
    train = False
    if train == True:
            inicio = 2849; ph = 48; janela = 600; past_samples = 40;
            piscina = pd.read_csv(r'files/files2.csv', header=None, names=['tex', 'hr', 'vel', 'pisc','pisc_colet', 'ts_colect', 'pisc_pav', 'pisc_col_cob'])
            piscina.shape

            #Spliting the data
            x1_id, x1_val = piscina['tex'][inicio-janela+1:inicio+1].values.reshape(-1, 1), piscina['tex'][inicio-past_samples:inicio+ph].values.reshape(-1, 1)
            x2_id, x2_val = piscina['hr'][inicio-janela+1:inicio+1].values.reshape(-1, 1), piscina['hr'][inicio-past_samples:inicio+ph].values.reshape(-1, 1)
            x3_id, x3_val = piscina['vel'][inicio-janela+1:inicio+1].values.reshape(-1, 1), piscina['vel'][inicio-past_samples:inicio+ph].values.reshape(-1, 1)
            x_id = np.concatenate([x1_id, x2_id, x3_id], axis=1)
            x_val = np.concatenate([x1_val, x2_val, x3_val], axis=1)

            lista_modelos = Models()
            for cont in range(1,5):
                    cenarios = ['pisc', 'pisc_colet', 'pisc_pav', 'pisc_col_cob']
                    y_id, y_val = piscina[cenarios[cont-1]][inicio - janela + 1:inicio + 1].values.reshape(-1, 1), piscina[cenarios[cont-1]][inicio - past_samples:inicio + ph].values.reshape(-1, 1)

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

            modelos_file = open("dados_modelos.pkl", 'wb')
            pickle.dump(lista_modelos, modelos_file)
            modelos_file.close()

    else:
        #download_file()
        inicio = 25; ph = 24; janela = 10; past_samples = 10;
        data = pd.read_csv(r'files/files2.csv', header=None,names=['data','tex', 'vel', 'hr'])
        data.shape
        #print(data)

        # Spliting the data
        x1_id, x1_val = data['tex'][inicio - janela + 1:inicio + 1].values.reshape(-1, 1), data['tex'][inicio - past_samples:inicio + ph].values.reshape(-1, 1)
        x2_id, x2_val = data['hr'][inicio - janela + 1:inicio + 1].values.reshape(-1, 1), data['hr'][inicio - past_samples:inicio + ph].values.reshape(-1, 1)
        x3_id, x3_val = data['vel'][inicio - janela + 1:inicio + 1].values.reshape(-1, 1), data['vel'][inicio - past_samples:inicio + ph].values.reshape(-1, 1)
        x_id = np.concatenate([x1_id, x2_id, x3_id], axis=1)
        x_val = np.concatenate([x1_val, x2_val, x3_val], axis=1)
        print('x_id: {}'.format(x_id))
        print('x_val: {}'.format(x_val))
        # y_forecast_1 = forecast(modelos.models[0], x_id[-40:, :], y_id[-40:], x_val, ph)


        # Recuperar os modelos
        modelos_file = open("dados_modelos.pkl", 'rb')
        modelos = pickle.load(modelos_file)
        modelos_file.close()
        mape = modelos.lista_MAPE;sse = modelos.lista_SSE;rrse = modelos.lista_RRSE;
        # forecasting = modelos.lista_y_hat; predicting = modelos.lista_y_hat1;
        # print('Calculo do Erro MAPE: {}. Menor valor: {} '.format(mape,min(mape)));
        # print('Calculo de SSE utilizando sklearn.metric: {}. Menor valor: {} '.format(sse,min(sse)));
        # print('Calculo de RRSE utilizando sysidentpy.metrics: {}. Menor valor: {} '.format(rrse,min(rrse)));
        # print('Forecast: {}'.format(forecasting));
        # print('Preditc: {}'.format(predicting));
        # ph =48;
        # xaxis = np.arange(1, ph + 1)
        # plt.plot(xaxis,predicting[2])
        # plt.plot(xaxis, forecasting[2])
        # plt.xlabel('Steps')
        # plt.ylabel('Previsão')
        # plt.show()l

