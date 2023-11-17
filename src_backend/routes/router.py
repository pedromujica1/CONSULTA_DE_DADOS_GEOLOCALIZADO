#Importing libraries and methods
from fastapi import APIRouter
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

#Importing collections,models and keys
from connections.connections import collection_alunos
from model.alunos import Aluno,Aluno_Dados,coordenadas
from schemas.api_requests import geo_data

router = APIRouter(tags=["OPERAÇÕES CRUD (CREATE,READ,DELETE,UPDATE)"])

#GET
#Retorna o aluno de acordo com o respectivo ID
@router.get("/aluno/{id}",response_description="Ler aluno por ID")
async def dados_aluno(id:str):
  aluno = await collection_alunos.find_one({"_id": ObjectId(id)})
  if aluno:
      aluno['_id'] = str(aluno['_id'])
      return JSONResponse(content=aluno)
  return {"O ID não foi encontrado": "Tente novamente"}

#POST
#Cadastra aluno na base de dados
@router.post("/novo_aluno",response_description="Adicinar novo aluno")
async def adicionar_aluno(aluno:Aluno):
  
  #Transforma em um dicionário
  aluno_dict = dict(aluno)
  
  #Retirando inputs do usuário
  nome_aluno = aluno_dict["name"]
  endereco_aluno = aluno_dict["addr_aluno"]
  endereco_localEstudo = aluno_dict["addr_instituicao"]
  
  data = await geo_data(endereco_aluno,endereco_localEstudo) #Retirando dados

  distancia_km = data["distancia_km"] #Retirando distância dos dados recebidos da função
  tempo_minutos=data["duracao_minutos"]
  coordenadas_ini = data["coordenadas_inicio"]
  coordenadas_fim = data["coordenadas_destino"]
  
  #Adicionando dados na classe
  novo_aluno = Aluno_Dados(nome=nome_aluno,addr_aluno=endereco_aluno,addr_instituicao=endereco_localEstudo,coordenadas_aluno=[coordenadas(latitude=coordenadas_ini[0],longitude=coordenadas_ini[1])], coordenadas_instituicao=[coordenadas(latitude=coordenadas_fim[0],longitude=coordenadas_fim[1])],distancia_KM=distancia_km,duracaoMinutos=tempo_minutos)
  
  #Transformando em JSON
  aluno_dict = jsonable_encoder(novo_aluno)
  
  #INSERINDO DADOS NO BANCO DE DADOS
  insert_aluno = await collection_alunos.insert_one(aluno_dict)
  
  if insert_aluno:
    return {"Operação realizada": "Aluno cadastratado com sucesso!"}
  return {"Não foi possível encontrar o aluno": "Tente novamente"}  
  
#PUT
#Atualiza dados do aluno
@router.put("/atualizar/{id}")
async def atualizar_aluno(id: str, aluno_atualizado:Aluno):
  
  update_aluno = dict(aluno_atualizado)
  #Retirando inputs do usuário
  nome_aluno = update_aluno ["name"]
  endereco_aluno = update_aluno ["addr_aluno"]
  endereco_localEstudo = update_aluno ["addr_instituicao"]
  
  #Retirando dados
  data = await geo_data(endereco_aluno,endereco_localEstudo)
  
  #Retirando distância dos dados recebidos da função
  distancia_km = data["distancia_km"]
  tempo_minutos=data["duracao_minutos"]
  coordenadas_ini = data["coordenadas_inicio"]
  coordenadas_fim = data["coordenadas_destino"]
  
  #Adicionando dados na classe
  updated_aluno = Aluno_Dados(nome=nome_aluno,addr_aluno=endereco_aluno,addr_instituicao=endereco_localEstudo,coordenadas_aluno=[coordenadas(latitude=coordenadas_ini[0],longitude=coordenadas_ini[1])], coordenadas_instituicao=[coordenadas(latitude=coordenadas_fim[0],longitude=coordenadas_fim[1])],distancia_KM=distancia_km,duracaoMinutos=tempo_minutos)
  
  #Transformando em JSON
  updated_dict = jsonable_encoder(updated_aluno)
  
  updated_aluno= await collection_alunos.find_one_and_update({"_id" : ObjectId(id)}, {"$set": updated_dict})
  
  if updated_aluno:
    return {"Operação realizada.":"Aluno atualizado com sucesso!"}
  return {"Não foi possível atualizar o aluno":"Tente novamente"}
  
#DELETE
#Deleta aluno no BD por ID
@router.delete("/deletar/{id}")
async def deletar_aluno(id: str):
  aluno_deletado= await collection_alunos.find_one_and_delete({"_id": ObjectId(id)})
  if aluno_deletado:
    return {"Aluno deletado com sucesso"}
  return {"Não foi possível deletar o aluno":"Tente novamente"}