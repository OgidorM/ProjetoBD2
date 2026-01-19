# /home/driblades/Documents/BD2/b2da1/clientes/core/exceptions.py

class ClienteServiceException(Exception):
    """Exceção genérica para erros na camada de serviço de clientes."""
    pass

class ClienteJaExisteException(ClienteServiceException):
    """Lançado quando tenta registrar um username que já existe."""
    pass