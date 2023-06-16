'''
@Jailson
Data: 17-11-2022


import requests
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
####################################################################################


def main():

	requisicao = requests.get(link)  # faz a requisição para o site(api)
	requisicao_dic = requisicao.json()  # armazena os valores solicitado num dicionario
	#print(requisicao_dic)
	temp = requisicao_dic['list'][0]['main']['temp'] - 273.15
	humidade = requisicao_dic['list'][0]['main']['humidity']
	veloc_vent = ((requisicao_dic['list'][0]['wind']['speed']) / (1000)) * 3600
	velocidade = '{:.0f}'.format(veloc_vent)
	temperatura = '{:.0f}'.format(temp)
	print(temperatura,velocidade,humidade)

if __name__ == "__main__":
	main()
'''

# import csv
#
# with open('c:/Users/jailson/PycharmProjects/TESTES/ecopol/files/exemplo.csv', 'w',encoding='UTF8',newline='') as csvfile:
#         writer = csv.writer(csvfile, delimiter=',')
#         writer.writerow(['25', '230', '80' ])


# Pre-requisite - Import the writer class from the csv module
from csv import writer

# The data assigned to the list
list_data = ['05-05-2023','23', '20', '70']

# Pre-requisite - The CSV file should be manually closed before running this code.

# First, open the old CSV file in append mode, hence mentioned as 'a'
# Then, for the CSV file, create a file object
with open('c:/Users/jailson/PycharmProjects/TESTES/ecopol/files/file.csv', 'a', newline='') as f_object:
    # Pass the CSV  file object to the writer() function
    writer_object = writer(f_object)
    # Result - a writer object
    # Pass the data in the list as an argument into the writerow() function
    writer_object.writerow(list_data)
    # Close the file object
    f_object.close()