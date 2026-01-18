# /home/driblades/Documents/BD2/b2da1/clientes/core/dtos.py
from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class NovoClienteDTO:
    username: str
    password: str
    email: str
    nome_completo: str
    # Campos opcionais:
    telefone: Optional[str] = None
    nif: Optional[str] = None
    morada: Optional[str] = None
    codigo_postal: Optional[str] = None
    localidade: Optional[str] = None
    data_nascimento: Optional[date] = None