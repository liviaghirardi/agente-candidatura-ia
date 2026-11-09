from typing import List, Optional
from pydantic import BaseModel

class Formacao(BaseModel):
    instituicao: str
    curso: str
    status: str
    ano_conclusao: str

class Experiencia(BaseModel):
    empresa: str
    cargo: str
    periodo: str
    bullets: List[str]

class Projeto(BaseModel):
    nome: str
    descricao: str
    tecnologias: List[str]

class Curso(BaseModel):
    nome: str
    instituicao: str
    carga_horaria: str

class Idioma(BaseModel):
    idioma: str
    nivel: str

class PerfilCandidato(BaseModel):
    nome: str
    cargo_desejado: str
    resumo: str
    formacao: List[Formacao]
    experiencias: List[Experiencia]
    projetos: List[Projeto]
    habilidades: List[str]
    cursos: List[Curso]
    idiomas: List[Idioma]
    