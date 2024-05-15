import typing
from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from fastapi_pagination import Page, paginate
from pydantic import UUID4
from workout_api.categoria.models import CategoriaModel
from workout_api.categoria.schemas import CategoriaIn, CategoriaOut
from workout_api.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select

router = APIRouter()


@router.post(
    "/",
    summary="Criar nova categoria",
    status_code=status.HTTP_201_CREATED,
    response_model=CategoriaOut,
)
async def post(
    db_session: DatabaseDependency, categoria_in: CategoriaIn = Body(...)
) -> CategoriaOut:
    categoria_out = CategoriaOut(id=uuid4(), **categoria_in.model_dump())
    categoria_model = CategoriaModel(**categoria_out.model_dump())

    db_session.add(categoria_model)
    await db_session.commit()

    return categoria_out


@router.get(
    "/",
    summary="Consultar todas as categorias",
    status_code=status.HTTP_200_OK,
    response_model=Page[CategoriaOut],
)
async def query(db_session: DatabaseDependency) -> Page[CategoriaOut]:
    return paginate(
        [
            categoria
            for categoria in await db_session.scalars(
                select(CategoriaModel).limit(10).offset(0)
            )
        ]
    )


@router.get(
    "/{id}",
    summary="Consultar categoria por ID",
    status_code=status.HTTP_200_OK,
    response_model=CategoriaOut,
)
async def query(id: UUID4, db_session: DatabaseDependency) -> CategoriaOut:
    categoria: CategoriaOut = (
        (await db_session.execute(select(CategoriaModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria não encontrado no id: {id}",
        )

    return categoria
