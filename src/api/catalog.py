from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Annotated
from src import database as db
import sqlalchemy

router = APIRouter()

#Don't change data definitions
class CatalogItem(BaseModel):
    sku: Annotated[str, Field(pattern=r"^[a-zA-Z0-9_]{1,20}$")]
    name: str
    quantity: Annotated[int, Field(ge=1, le=10000)]
    price: Annotated[int, Field(ge=1, le=500)]
    potion_type: List[int] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="Must contain exactly 4 elements: [r, g, b, d]",
    )


def create_catalog() -> List[CatalogItem]:
    #Get sku, current quantity, price, and mix
    #for all available potions
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT sku, name, COALESCE(SUM(change), 0) as quantity, price, mix
                FROM potions
                JOIN potion_ledger ON potions.id = potion_ledger.potion_id
                GROUP BY potions.id, sku, name, price, mix
                HAVING COALESCE(SUM(change), 0) > 0
                ORDER BY potions.id ASC
                """
            )
        ).all()
        potions = [potion._asdict() for potion in result]

    #use database potion attributes to create a
    #list of catalog item objects
    catalog_list = []
    for potion in potions:
        formula = [potion["mix"][0], potion["mix"][1], potion["mix"][2], potion["mix"][3]]
        catalog_list.append(CatalogItem(
                sku=potion["sku"],
                name=potion["name"],
                quantity=potion["quantity"],
                price=potion["price"],
                potion_type=formula
            )
        )

    return catalog_list


@router.get("/catalog/", tags=["catalog"], response_model=List[CatalogItem])
def get_catalog() -> List[CatalogItem]:
    """
    Retrieves the catalog of items. Each unique item combination should have only a single price.
    You can have at most 6 potion SKUs offered in your catalog at one time.
    """
    return create_catalog()
