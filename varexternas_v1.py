'''
@Jailson
Data: 24-02-2022
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
node_id = "ecopool+++"
##################################################################################
API_KEY = "23ffbe727b2bee451d3dc7b37ad2b813"
cidade = "faro"
code = "351"
link = "https://api.openweathermap.org/data/2.5/forecast?q="+str(cidade)+"&appid="+str(API_KEY)
link1 = "https://api.open-meteo.com/v1/forecast?latitude=37.025408&longitude=-7.922246&hourly=temperature_2m,relativehumidity_2m,precipitation,windspeed_10m"

def main():

	requisicao = requests.get(link1)  # faz a requisição para o site(api)
	requisicao_dic = requisicao.json()  # armazena os valores solicitado num dicionario

	# print('Primeira posição do hourly-Time: {}'.format(requisicao_dic['hourly']['time'][0]))
	# print('Ultima posição do hourly-Time: {}'.format(requisicao_dic['hourly']['time'][-1]))
	data = requisicao_dic['hourly']['time']
	temperature = requisicao_dic['hourly']['temperature_2m']
	windspeed = requisicao_dic['hourly']['windspeed_10m']
	precipitation = requisicao_dic['hourly']['precipitation']
	relativehumidity = requisicao_dic['hourly']['relativehumidity_2m']

	# print('Data: {}'.format(data))
	#print('Temperature: {}'.format(temperature))
	# print('Windspeed: {}'.format(windspeed))
	# print('Precipitation: {}'.format(precipitation))
	# print('Relativehumidity: {}'.format(relativehumidity))
	array0 = data
	array1 = temperature
	array2 = windspeed
	array3 = relativehumidity
	for a,b,c,d in zip(array0,array1,array2,array3):
		print(a,b,c,d)
		lista = [a,b,c,d]
		with open('files/files1.csv', 'a', newline='') as f_object:
		#Pass the CSV  file object to the writer() function
			writer_object = lwriter(f_object)
		 	# Result - a writer object
		    # Pass the data in the list as an argument into the writerow() function
			writer_object.writerow(lista)
		    # Close the file object
			f_object.close()
	# data_json = '{"Temperatura":' + str(temperature) + ',"Relative_Humidity":' + str(relativehumidity) + ',"Windspeed":' + str(windspeed) +'}'
	# emon_link = 'http://' + emon_ip + '/emoncms/input/post?node=' + node_id + '&fulljson=' + str(data_json) + "&apikey=" + str(emon_apikey)
	# request = requests.get(emon_link)

	# enviar para arquivo csv
	# The data assigned to the list
	# lista = [data,temperature, '\n', windspeed,'\n', relativehumidity]
	#
	# with open('C:/Users/Jailson/PycharmProjects/TESTES/ecopol/files/files1.csv', 'a', newline='') as f_object:
	# 	# Pass the CSV  file object to the writer() function
	# 	writer_object = writer(f_object)
	# 	# Result - a writer object
	# 	# Pass the data in the list as an argument into the writerow() function
	# 	writer_object.writerow(lista)
	# 	# Close the file object
	# 	f_object.close()

if __name__ == "__main__":
	main()