from pydantic import BaseModel
from typing import Optional

class coordenadas(BaseModel):
  latitude:float
  longitude:float

class Aluno_Dados(BaseModel):
  nome: str 
  addr_aluno: str 
  addr_instituicao:str 
  coordenadas_aluno: list[coordenadas] | None = None
  coordenadas_instituicao:list[coordenadas] | None = None
  distancia_KM:float
  duracaoMinutos:float
  
  
class Aluno(BaseModel):
  name:Optional[str]
  addr_aluno:Optional[str]
  addr_instituicao:Optional[str]
  