from connections.connections import bing_maps_key,gmaps_api_key
import httpx
import re

API_KEY = bing_maps_key
GMAPS_KEY = gmaps_api_key

async def async_request(url:str):
    async with httpx.AsyncClient() as client:
        res = await client.get(url, timeout=None)
        return res.json()
        

async def get_addr(cep, numero_addr):

    #verificação do CEP digitado
    #REGEX FOR THE CEP CODE
    regex = re.compile(r'^\d{5}-\d{3}|\d{8}$')

    if regex.match(cep):
    
        #Request URL from ViaCep api
        url = f"https://viacep.com.br/ws/{cep}/json/"
        
        #making the async request
        api_data =await async_request(url)

        #ADDRESS STRING FOR BOTH POINTS
        #STRING DOS ENDEREÇOS DE INICIO E FIM
        #EXEMPLO: AVENIDA DAS POMBAS, 2020 - FLORESTA, Cascavel - PR, 85814-800
        address= f"{api_data['logradouro']}, {numero_addr} - {api_data['bairro']}, {api_data['localidade']} - {api_data['uf']}, {api_data['cep']}"
        return address
    raise ValueError('CEP INVALIDO')
    
async def school_info(addr, institution):
    #FILTERS THE SEARCH WITH ONLY THE LOCATION TYPE
    #RETORNA SOMENTE O TIPO DO LOCAL
    fields = 'type' 
    query = f'{institution},{addr}'

    #Request URL
    #REQUEST PARAMETES
    #PARAMETROS DO REQUEST
    url = (
        f'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'
        f'?input={query}'
        f'&inputtype=textquery'
        f'&fields={fields}'
        f'&key={GMAPS_KEY}'
    )

    #Making the async request
    data = await async_request(url)
    #REQUEST BODY EXAMPLE: {'candidates': [{'types': ['school', 'point_of_interest', 'establishment']}], 'status': 'OK'}
    types_list = data['candidates'][0]['types']

    #VERFICANDO SE A STRING SCHOOL OU UNIVERSIDADE ESTÁ PRESENTE NA LISTA
    #VERYFING IF THE STRING IS IN THE LIST OF TYPES
    if 'school' in types_list or 'university' in types_list:
        return types_list
    return ["request_failed"]

#FUNÇÃO PARA RETORNAR COORDENADAS    '    
async def get_coordinates(addr_origin:str,addr_destination:str):
    #Bing Maps request URL to get locations 
    url_origin = f"https://dev.virtualearth.net/REST/v1/Locations?query={addr_origin}&key={API_KEY}"
    url_destination = f"https://dev.virtualearth.net/REST/v1/Locations?query={addr_destination}&key={API_KEY}"

    #Getting requests from url
    response_origin = await async_request(url_origin)
    response_dest = await async_request(url_destination)
    
    #Getting coordinates data from JSON
    origin = response_origin['resourceSets'][0]['resources'][0]['point']['coordinates']
    destination = response_dest['resourceSets'][0]['resources'][0]['point']['coordinates']

    #RETURNING COORDINATES FROM THE RESPONSE BODY
    #Salvando coordenadas da resposta na requisição em lista
    return [origin[0], origin[1], destination[0], destination[1]]

#OSRM request
async def route_data(long_org,lat_org,long_dest,lat_dest):
    
    #Formating lat/long strings for the request
    locations = '{},{};{},{}'.format(long_org,lat_org,long_dest,lat_dest)
    
    #URL for request
    url_osrm = "http://router.project-osrm.org/route/v1/driving/"
    
    full_request = url_osrm+locations
    
    #Reading OSRM DATA
    OSRM_data = await async_request(full_request)
    
    #Converting request response body result to json
    return OSRM_data

async def geo_data(addr_origin:str, addr_destination:str):

    #Bing Maps request URL to get locations
    coordinates = await get_coordinates(addr_origin, addr_destination)

    #OSRM url to get distance information
    OSRM_data =await route_data(coordinates[1], coordinates[0], coordinates[3], coordinates[2])

    #Getting distance data and creating variables
    distance_data = OSRM_data['routes'][0]
    distanceMetters= distance_data['distance']
    distanceKm = distanceMetters/1000

    #Getting duration data in seconds
    durationSeconds = OSRM_data['routes'][0]['duration']
    durationMin = durationSeconds/60
    
    #Output 
    data = {'coordenadas_inicio':[coordinates[0], coordinates[1]],            
            'coordenadas_destino': [coordinates[2], coordinates[3]],
            'duracao_minutos': durationMin,
            'distancia_km': distanceKm,}
            
    return data 