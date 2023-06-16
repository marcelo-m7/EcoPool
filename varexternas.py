'''
@Jailson
Data: 17-11-2022
'''

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
API_KEY_PRO = "5c27c543425c4d4a1efc3c6bee965937"
cidade = "faro"
code = "351"
link = "https://api.openweathermap.org/data/2.5/forecast?q="+str(cidade)+"&appid="+str(API_KEY)

def main():

	requisicao = requests.get(link)  # faz a requisição para o site(api)
	requisicao_dic = requisicao.json()  # armazena os valores solicitado num dicionario
	print(requisicao_dic)
	temp = requisicao_dic['list'][0]['main']['temp'] - 273.15
	humidade = requisicao_dic['list'][0]['main']['humidity']
	veloc_vent = ((requisicao_dic['list'][0]['wind']['speed']) / (1000)) * 3600
	velocidade = '{:.0f}'.format(veloc_vent)
	temperatura = '{:.0f}'.format(temp)
	#print(temperatura,velocidade,humidade)
	# enviar para emoncms
	data_json = '{"TemperaturaExt":' + str(temperatura) + ',"HumidadeExt":' + str(humidade) + ',"VelocidadeExt":' + str(velocidade) +'}'
	emon_link = 'http://' + emon_ip + '/emoncms/input/post?node=' + node_id + '&fulljson=' + str(data_json) + "&apikey=" + str(emon_apikey)
	request = requests.get(emon_link)

    # enviar para arquivo csv
	# The data assigned to the list
	list_data = [data_e_hora_em_texto,temperatura, velocidade, humidade]

	with open('files/files.csv', 'a', newline='') as f_object:
		# Pass the CSV  file object to the writer() function
		writer_object = writer(f_object)
		# Result - a writer object
		# Pass the data in the list as an argument into the writerow() function
		writer_object.writerow(list_data)
		# Close the file object
		f_object.close()


if __name__ == "__main__":
	main()