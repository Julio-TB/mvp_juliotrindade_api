from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union

from  model import Base, Comentario


class Pessoa(Base):
    __tablename__ = 'pessoa'

    id = Column("pk_pessoa", Integer, primary_key=True)
    nome = Column(String(140), unique=True)
    cpf = Column(String, unique=True)
    tipo = Column(String(140))
    #quantidade = Column(Integer)
    #valor = Column(Float)
    data_nasc = Column(DateTime)
    #data_insercao = Column(DateTime, default=datetime.now())

    # Definição do relacionamento entre a pessoa e o comentário.
    # Essa relação é implicita, não está salva na tabela 'pessoa',
    # mas aqui estou deixando para SQLAlchemy a responsabilidade
    # de reconstruir esse relacionamento.
    comentarios = relationship("Comentario")

    def __init__(self, nome:str, cpf:str, tipo:str,
                 data_nasc:Union[DateTime, None] = None):
        """
        Cria uma Pessoa

        Arguments:
            nome: nome da pessoa
            cpf: CPF da pessoa
            tipo: categoria da pessoa cadastrada, Pesquisador ou Bolsista
            data_nasc: data de nascimento da pessoa
        """
        self.nome = nome
        self.cpf = cpf
        self.tipo = tipo

        # se não for informada, será o data exata da inserção no banco
        if data_nasc:
            self.data_nasc = data_nasc

    def adiciona_comentario(self, comentario:Comentario):
        """ Adiciona um novo comentário ao Produto
        """
        self.comentarios.append(comentario)

