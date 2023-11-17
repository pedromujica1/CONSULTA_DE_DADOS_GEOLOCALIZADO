from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import folium, polyline
from schemas.api_requests import route_data,get_addr,get_coordinates,school_info
from routes.router import router
from fastapi.middleware.cors import CORSMiddleware

#Adicionar chave do BING maps
#python3 -m uvicorn main:api --reload
#127.0.0.0/docs para testar o GET

description= """
Aplicação REST para auxiliar instituições de ensino da identificação de dados sobre os endereços de seus estudantes. 📍🗺️

## Funções Básicas

Ver **dados** de acordo com o CEP do aluno e Instituição de Ensino.
Ver **mapa** da rota entre os dois pontos.

## Integração com banco de dados

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).
* **Delete users** (_not implemented_).
* **Update users** (_not implemented_).
"""

app = FastAPI(
    title="API REST para consulta de dados geolocalizados",
    description=description,
    summary="Trabalho de Conclusão de Curso desenvolvido no IFPR Cascavel",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Pedro Miotto Mujica & Pedro Henrique Shroeder Bolfe",
        "url": "https://ifpr.edu.br/cascavel/",
        "email": "",
    },
    license_info={
        "name": "sem licença ainda",
        "url": "https://ifpr.edu.br/cascavel/",
    },
    )

#ALLOWING CORS
#PERMITINDO REQUISIÇÕES PARA O FRONTEND
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#ROTA DE BOAS VINDAS
@app.get("/",tags=['Welcome'])
def welcome():
    return {"status_code": "200",
            "description": "IT WORKS!"}

#ROTA PARA RETORNAR DADOS DE ACORDO COM O CEP INFORMADO
@app.get("/car_data/{cep_aluno}/{numero_addr1}/{nome_instituicao_ensino}/{cep_instituicao}/{numero_addr2}",tags=['Mostrar dados de acordo com CEP'])
async def get_data_by_cep(cep_aluno:str,numero_addr1:str,nome_instituicao_ensino:str,cep_instituicao:str,numero_addr2:str):

    #function to get address data that returns a string address format
    #função que consulta a api ViaCep e retorna uma string no formato de endereço
    addr_ini = await get_addr(cep_aluno,numero_addr1)
    addr_end = await get_addr(cep_instituicao,numero_addr2)

    #function to validate the school
    #VERIFICA SE O ENDEREÇO PERTENCE A UMA ESCOLA OU UNIVERSIDADE
    tipos_escola = await school_info(addr_end,nome_instituicao_ensino)

    if tipos_escola[0] == "request_failed":
        return {"Requisição não encontrou instituição de ensino"}
    
    #GETTING COORDINATES FROM THE ADDRESS
    #RETIRANDO AS COORDENADAS DOS ENDEREÇOS
    coordinates = await get_coordinates(addr_ini,addr_end)

    #Defining long and lat variables
    #ARMAZENANDO VARIAVEIS DE LATITUDE E LONGITUDE
    origin_lat, origin_long = coordinates[0], coordinates[1]
    dest_lat, dest_long = coordinates[2], coordinates[3]

    #OSRM request that returns the response in json 
    #RETORNANDO BODY DO REQUEST DA API EM JSON
    OSRM_response = await route_data(origin_long, origin_lat, dest_long, dest_lat)

    #Getting distance data and creating variables
    distance_data = OSRM_response['routes'][0]
    distanceMetters= distance_data['distance']
    distanceKm = distanceMetters/1000

    #Getting duration data in seconds
    durationSeconds = OSRM_response['routes'][0]['duration']
    durationMin = durationSeconds/60

    #displaying data
    #MOSTRANDO DADOS EM STRING
    description1 = f'{durationMin:.0f} mins'
    description2 = f'{distanceKm:.0f} Km'

    formatted_addr = f'{nome_instituicao_ensino.upper()}, {addr_end}'

    #Output
    data = {'endereco_ini': addr_ini, 
            'coordenadas_inicio':[origin_lat, origin_long],
            'endereco_instituicao':formatted_addr,           
            'coordenadas_destino': [dest_lat, dest_long],
            'tipos_instituicao': tipos_escola,
            'duracao_minutos': durationMin,
            'descricao_durcao': description1,
            'distancia_km': distanceKm,
            'descricao_distancia': description2}   
    return data

#ROTA PARA RETORNAR HTML DA ROTA INFORMADA
@app.get("/rota",tags=['Mostrar mapa da rota'], response_class=HTMLResponse)
async def display_map(long_org, lat_org, long_dest, lat_dest):
    
    #GETS THE OSRM RESPONSE BODY
    #RETORNA O JSON DA REQUISÇÃO DE ROTAS DA OSRM
    OSRM_response = await route_data(long_org, lat_org,long_dest,lat_dest)

    #Decodes the polyline string response into coordinates
    geocoded_routes = polyline.decode(OSRM_response['routes'][0]['geometry'])

    follium_map = folium.Map(location=[(float(lat_org) + float(lat_dest))/2, 
                             (float(long_org) + float(long_dest))/2], 
                   zoom_start=13)

    folium.PolyLine(
        geocoded_routes,
        weight=8,
        color='blue',
        opacity=0.6
    ).add_to(follium_map)

    folium.Marker(
        location=[lat_org,long_org],
        icon=folium.Icon(icon='play', color='green')
    ).add_to(follium_map)

    folium.Marker(
        location=[lat_dest,long_dest],
        icon=folium.Icon(icon='stop', color='red')
    ).add_to(follium_map)
    
    #Turns follium object into an html string
    map_response= follium_map.get_root().render()
    
    return HTMLResponse(content=map_response, status_code=200)

#INCLUINDO OPERAÇÕES CRUD
#Including router for CRUD operations
app.include_router(router)