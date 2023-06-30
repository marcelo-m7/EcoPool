

import datetime

data_hora_atual = datetime.datetime.now()

# Formatando a data e hora atual
data_hora_formatada = data_hora_atual.strftime("%d-%m-%Y %H:%M:%S")
data_hora_formatada = data_hora_formatada.replace("-", "/")

print(data_hora_formatada)
data_hora_formatada_str = str(data_hora_formatada)
# Converter a string em objeto datetime
data_hora_obj = datetime.datetime.strptime(data_hora_formatada_str, "%d/%m/%Y %H:%M:%S")
# Converter o objeto datetime em um número inteiro
data_hora_int = int(data_hora_obj.timestamp())
print(data_hora_int)





# print("Número inteiro correspondente à data e hora:", data_hora_int)
# import pandas as pd
# import csv
# # Guardar os valores das variaveis: inicio_t, cenario e duration em csv
# inicio_t = 7000; cenario = 1; duration =200
# variaveis = [inicio_t, cenario, duration]
# registro_variaveis = r'files/registro_variaveis.csv'
# registro_var = pd.read_csv(r'files/registro_variaveis.csv', header=None,names=['Inicio', 'Cenario', 'Duration'])
# #registro_var = pd.read_csv(r'files/registro_variaveis.csv',header=None,names=['Inicio', 'Cenario', 'Duration'])
# lista_cenarios = registro_var.values[:,1]
# cenario=(cenario)
# if list(lista_cenarios[:]).count((cenario)) == 0: #trata do append
#     with open(registro_variaveis, 'a', newline='') as registro_variaveis_csv:
#         writer_object = csv.writer(registro_variaveis_csv)
#         writer_object.writerow(variaveis)
# else:
#     #trata de escrever onde ja existe
#     pos = list(lista_cenarios[:]).index(cenario)
#     registro_var.values[pos, 0] = inicio_t
#     registro_var.values[pos, 2] = duration
#     with open(registro_variaveis,'r') as registro_variaveis_csv:
#         reader = csv.reader(registro_variaveis_csv)
#         lines = list(reader)
#         lines[pos+1] = [inicio_t, cenario, duration]
#     with open(registro_variaveis, 'w', newline='') as registro_variaveis_csv:
#         writer_object = csv.writer(registro_variaveis_csv)
#         writer_object.writerows(lines)
