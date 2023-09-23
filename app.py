from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote

from sqlalchemy.exc import IntegrityError

from model import Session, Pessoa, Comentario
from logger import logger
from schemas import *
from flask_cors import CORS

info = Info(title="Minha API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
pessoa_tag = Tag(name="Pessoa", description="Adição, visualização e remoção de pessoas à base")
comentario_tag = Tag(name="Comentario", description="Adição de um comentário à uma pessoa cadastrado na base")


@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')


@app.post('/pessoa', tags=[pessoa_tag],
          responses={"200": PessoaViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_pessoa(form: PessoaSchema):
    """Adiciona uma nova Pessoa à base de dados

    Retorna uma representação das pessoas e comentários associados.
    """
    pessoa = Pessoa(
        nome=form.nome,
        cpf=form.cpf,
        tipo=form.tipo)
    logger.debug(f"Adicionanda pessoa de nome: '{pessoa.nome}'")
    try:
        # criando conexão com a base
        session = Session()
        # adicionando pessoa
        session.add(pessoa)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        logger.debug(f"Adicionada pessoa de nome: '{pessoa.nome}'")
        return apresenta_pessoa(pessoa), 200

    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "Pessoa de mesmo nome já salvo na base :/"
        logger.warning(f"Erro ao adicionar pessoa '{pessoa.nome}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logger.warning(f"Erro ao adicionar pessoa '{pessoa.nome}', {error_msg}")
        return {"mesage": error_msg}, 400


@app.get('/pessoas', tags=[pessoa_tag],
         responses={"200": ListagemPessoasSchema, "404": ErrorSchema})
def get_pessoas():
    """Faz a busca por todas as Pessoa cadastradas

    Retorna uma representação da listagem de pessoas.
    """
    logger.debug(f"Coletando pessoas ")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    pessoas = session.query(Pessoa).all()

    if not pessoas:
        # se não há pessoas cadastradas
        return {"pessoas": []}, 200
    else:
        logger.debug(f"%d pessoas econtrados" % len(pessoas))
        # retorna a representação de pessoa
        print(pessoas)
        return apresenta_pessoas(pessoas), 200


@app.get('/pessoa', tags=[pessoa_tag],
         responses={"200": PessoaViewSchema, "404": ErrorSchema})
def get_pessoa(query: PessoaBuscaSchema):
    """Faz a busca por uma Pessoa a partir do id da pessoa

    Retorna uma representação das pessoas e comentários associados.
    """
    pessoa_id = query.id
    logger.debug(f"Coletando dados sobre pessoa #{pessoa_id}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    pessoa = session.query(Pessoa).filter(Pessoa.id == pessoa_id).first()

    if not pessoa:
        # se a pessoa não foi encontrada
        error_msg = "Pessoa não encontrada na base :/"
        logger.warning(f"Erro ao buscar pessoa '{pessoa_id}', {error_msg}")
        return {"mesage": error_msg}, 404
    else:
        logger.debug(f"Pessoa econtrada: '{pessoa.nome}'")
        # retorna a representação de pessoa
        return apresenta_pessoa(pessoa), 200


@app.delete('/pessoa', tags=[pessoa_tag],
            responses={"200": PessoaDelSchema, "404": ErrorSchema})
def del_pessoa(query: PessoaBuscaSchema):
    """Deleta uma Pessoa a partir do nome de pessoa informado

    Retorna uma mensagem de confirmação da remoção.
    """
    pessoa_nome = unquote(unquote(query.nome))
    print(pessoa_nome)
    logger.debug(f"Deletando dados sobre pessoa #{pessoa_nome}")
    # criando conexão com a base
    session = Session()
    # fazendo a remoção
    count = session.query(Pessoa).filter(Pessoa.nome == pessoa_nome).delete()
    session.commit()

    if count:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Deletada pessoa #{pessoa_nome}")
        return {"mesage": "Pessoa removida", "id": pessoa_nome}
    else:
        # se o pessoa não foi encontrada
        error_msg = "Pessoa não encontrada na base :/"
        logger.warning(f"Erro ao deletar pessoa #'{pessoa_nome}', {error_msg}")
        return {"mesage": error_msg}, 404


@app.post('/cometario', tags=[comentario_tag],
          responses={"200": PessoaViewSchema, "404": ErrorSchema})
def add_comentario(form: ComentarioSchema):
    """Adiciona de um novo comentário à uma pessoa cadastrada na base identificado pelo id

    Retorna uma representação das pessoas e comentários associados.
    """
    pessoa_id  = form.pessoa_id
    logger.debug(f"Adicionando comentários a pessoa #{pessoa_id}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca pelo pessoa
    pessoa = session.query(Pessoa).filter(Pessoa.id == pessoa_id).first()

    if not pessoa:
        # se pessoa não encontrado
        error_msg = "Pessoa não encontrada na base :/"
        logger.warning(f"Erro ao adicionar comentário a pessoa '{pessoa_id}', {error_msg}")
        return {"mesage": error_msg}, 404

    # criando o comentário
    texto = form.texto
    comentario = Comentario(texto)

    # adicionando o comentário a pessoa
    pessoa.adiciona_comentario(comentario)
    session.commit()

    logger.debug(f"Adicionado comentário a pessoa #{pessoa_id}")

    # retorna a representação de pessoa
    return apresenta_pessoa(pessoa), 200
