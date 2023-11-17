import motor.motor_asyncio
import os


#Conectando com a bibliotecar motor
connection = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])

database_alunos = connection.alunos
collection_alunos = database_alunos["information"]

#Chave da API do Bing maps
bing_maps_key = os.environ["BMAPS_URL"]

#GOOGLE MAPS API KEY
gmaps_api_key = os.environ["GMAPS_URL"]