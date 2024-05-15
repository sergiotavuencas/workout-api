from typing import Annotated
from pydantic import UUID4, Field

from workout_api.contrib.schemas import BaseSchema


class Categoria(BaseSchema):
    nome: Annotated[
        str,
        Field(description="Nome da categoria", example="Musculação", max_length=10),
    ]


class CategoriaIn(Categoria):
    pass


class CategoriaOut(Categoria):
    id: Annotated[UUID4, Field(description="Identificador da categoria")]
