from datetime import datetime, timezone

from typing import Optional
from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from fastapi_pagination import Page
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi_pagination import paginate

from workout_api.atleta.models import AtletaModel
from workout_api.atleta.schemas import AtletaIn, AtletaOut, AtletaSimplified, AtletaUpdate
from workout_api.categoria.models import CategoriaModel
from workout_api.categoria.schemas import CategoriaOut
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout_api.centro_treinamento.schemas import CentroTreinamentoOut
from workout_api.contrib.dependencies import DatabaseDependency

router = APIRouter()


@router.post(
    "/",
    summary="Criar novo atleta",
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut,
)
async def post(
    db_session: DatabaseDependency, atleta_in: AtletaIn = Body(...)
) -> AtletaOut:
    # 
    categoria_nome = atleta_in.categoria.nome
    centro_treinamento_nome = atleta_in.centro_treinamento.nome

    categoria: list[CategoriaOut] = (
        (
            await db_session.execute(
                select(CategoriaModel).filter_by(nome=categoria_nome)
            )
        )
        .scalars()
        .first()
    )

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A categoria {categoria_nome} não foi encontrada.",
        )

    centro_treinamento: CentroTreinamentoOut = (
        (
            await db_session.execute(
                select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_nome)
            )
        )
        .scalars()
        .first()
    )

    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"O centro de treinamento {centro_treinamento_nome} não foi encontrado.",
        )

    try:
        atleta_out = AtletaOut(
            id=uuid4(),
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            **atleta_in.model_dump(),
        )
        atleta_model = AtletaModel(
            **atleta_out.model_dump(exclude={"categoria", "centro_treinamento"})
        )
        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id

        db_session.add(atleta_model)

        try:
            await db_session.commit()

        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                detail=f"Já existe um atleta cadastrado com o cpf: {atleta_model.cpf}",
            )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao inserir os dados no banco.",
        )

    return atleta_out


@router.get(
    "/",
    summary="Consultar todos os atletas",
    status_code=status.HTTP_200_OK,
    response_model=Page[AtletaSimplified],
)
async def query(
    db_session: DatabaseDependency,
    nome: Optional[str] = None,
    cpf: Optional[str] = None,
) -> Page[AtletaSimplified]:
    atleta_nome = nome
    atleta_cpf = cpf

    if atleta_nome:
        query = [
            atleta
            for atleta in await db_session.scalars(
                select(AtletaModel).filter_by(nome=atleta_nome).limit(10).offset(0)
            )
        ]

    elif atleta_cpf:
        query = [
            atleta
            for atleta in await db_session.scalars(
                select(AtletaModel).filter_by(cpf=atleta_cpf).limit(10).offset(0)
            )
        ]

    else:
        query = [
            atleta
            for atleta in await db_session.scalars(
                select(AtletaModel).limit(10).offset(0)
            )
        ]
    
    return paginate(query)


@router.get(
    "/{id}",
    summary="Consultar atleta por ID",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def query(id: UUID4, db_session: DatabaseDependency) -> AtletaOut:
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado no id: {id}",
        )

    return atleta


@router.patch(
    "/{id}",
    summary="Editar um atleta por ID",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def get(
    id: UUID4, db_session: DatabaseDependency, atleta_up: AtletaUpdate = Body(...)
) -> AtletaOut:
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado no id: {id}",
        )

    atleta_update = atleta_up.model_dump(exclude_unset=True)

    for key, value in atleta_update.items():
        setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)

    return atleta


@router.delete(
    "/{id}",
    summary="Deletar atleta por ID",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def get(id: UUID4, db_session: DatabaseDependency) -> None:
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado no id: {id}",
        )

    await db_session.delete(atleta)
    await db_session.commit()
