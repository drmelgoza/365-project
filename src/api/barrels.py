from dataclasses import dataclass
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator
from typing import List
from random import randint

import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str
    ml_per_barrel: int = Field(gt=0, description="Must be greater than 0")
    potion_type: List[float] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="Must contain exactly 4 elements: [r, g, b, d] that sum to 1.0",
    )
    price: int = Field(ge=0, description="Price must be non-negative")
    quantity: int = Field(ge=0, description="Quantity must be non-negative")

    @field_validator("potion_type")
    @classmethod
    def validate_potion_type(cls, potion_type: List[float]) -> List[float]:
        if len(potion_type) != 4:
            raise ValueError("potion_type must have exactly 4 elements: [r, g, b, d]")
        if not abs(sum(potion_type) - 1.0) < 1e-6:
            raise ValueError("Sum of potion_type values must be exactly 1.0")
        return potion_type


class BarrelOrder(BaseModel):
    sku: str
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")

#alter class to include ml summaries
@dataclass
class BarrelSummary:
    gold_paid: int


def calculate_barrel_summary(barrels: List[Barrel]) -> BarrelSummary:
    return BarrelSummary(gold_paid=sum(b.price * b.quantity for b in barrels))


#TODO: Use ledgering to get barrel posting to function
@router.post("/deliver/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def post_deliver_barrels(barrels_delivered: List[Barrel], order_id: int):
    """
    Processes barrels delivered based on the provided order_id. order_id is a unique value representing
    a single delivery; the call is idempotent based on the order_id.
    """
    print(f"barrels delivered: {barrels_delivered} order_id: {order_id}")

    delivery = calculate_barrel_summary(barrels_delivered)

    new_id = 0
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO transactions (time)
                VALUES (CURRENT_TIMESTAMP)
                RETURNING id
                """
            ),
        ).one()
        new_id = result.id

    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO gold_ledger (transaction_id, change)
                VALUES (:new_id, :gold_paid)
                """
            ),
            [{"new_id": new_id,
              "gold_paid":(-1 * delivery.gold_paid)
            }],

        )
    red_total = 0
    green_total = 0
    blue_total = 0
    dark_total = 0
    for barrel in barrels_delivered:
        ml_total = barrel.ml_per_barrel * barrel.quantity
        if barrel.potion_type[0] == 1:
            red_total += ml_total
        elif barrel.potion_type[1] == 1:
            green_total += ml_total
        elif barrel.potion_type[2] == 1:
            blue_total += ml_total
        else :
            dark_total += ml_total

    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO ml_ledger (transaction_id, change_red, change_green, change_blue, change_dark)
                VALUES (:transaction_id, :red, :green, :blue, :dark)
                """
            ),
            [{"transaction_id": new_id,
              "red": red_total,
              "green": green_total,
              "blue": blue_total,
              "dark": dark_total
            }],
        )


def create_barrel_plan(
    gold: int,
    max_barrel_capacity: int,
    current_red_ml: int,
    current_green_ml: int,
    current_blue_ml: int,
    current_dark_ml: int,
    wholesale_catalog: List[Barrel],
) -> List[BarrelOrder]:
    print(
        f"gold: {gold}, max_barrel_capacity: {max_barrel_capacity}, current_red_ml: {current_red_ml}, current_green_ml: {current_green_ml}, current_blue_ml: {current_blue_ml}, current_dark_ml: {current_dark_ml}, wholesale_catalog: {wholesale_catalog}"
    )

    #choose a random type of barrel based on the color indexes
    #color mappings: red: 0, green: 1, blue: 2
    #color mapping works by color due to Barrel Object's potion type indexes
    #hard programmed for now to not include dark barrels
    remaining_gold = gold
    catalog_quantities = {barrel.sku:barrel.quantity for barrel in wholesale_catalog}
    barrels = []
    #purchase at most two barrels at once to allow for mixing
    for i in range(0, 2):
        rand_barrel_type = randint(0, 2)

        # find smallest affordable barrel of the randomly chosen type
        rand_barrel = min(
            (barrel for barrel in wholesale_catalog if (barrel.potion_type[rand_barrel_type] == 1 and barrel.price <= remaining_gold)),
            key=lambda b: b.price,
            default=None,
        )

        # choose which potions to call from the database
        # get ml total and get min from those values
        num_potions = 0
        if rand_barrel:
            with db.engine.begin() as connection:
                result = connection.execute(
                    sqlalchemy.text(
                            """
                            SELECT COALESCE(SUM(change), 0) as qty
                            FROM potion_ledger
                            JOIN potions ON potion_ledger.potion_id = potions.id
                            WHERE mix[:barrel_type] > 0
                            """
                    ),
                    [{"barrel_type": rand_barrel_type}]
                ).one()

                num_potions = result.qty

        #make sure not too many potions exist with the barrel's ml type
        #and that the barrel type has stock remaining
            if num_potions < 10 and (catalog_quantities[rand_barrel.sku] > 0):
                barrels.append(BarrelOrder(sku=rand_barrel.sku, quantity=1))
                catalog_quantities[rand_barrel.sku] -= 1
                remaining_gold -= rand_barrel.price

    # return an empty list if no affordable barrel is found
    return barrels


@router.post("/plan", response_model=List[BarrelOrder])
def get_wholesale_purchase_plan(wholesale_catalog: List[Barrel]):
    """
    Gets the plan for purchasing wholesale barrels. The call passes in a catalog of available barrels
    and the shop returns back which barrels they'd like to purchase and how many.
    """
    print(f"barrel catalog: {wholesale_catalog}")

    #retrieve inventory quantities for gold and mls
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT COALESCE(SUM(change), 0) as gold
                FROM gold_ledger
                """
            )
        ).one()

        gold = result.gold

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT COALESCE(SUM(change_red), 0) as red, 
                       COALESCE(SUM(change_green), 0) as green, 
                       COALESCE(SUM(change_blue), 0) as blue, 
                       COALESCE(SUM(change_dark), 0) as dark
                FROM ml_ledger
                """
            )
        ).one()

        red = result.red
        green = result.green
        blue = result.blue
        dark = result.dark

    return create_barrel_plan(
        gold=gold,
        max_barrel_capacity=10000,
        current_red_ml=red,
        current_green_ml=green,
        current_blue_ml=blue,
        current_dark_ml=dark,
        wholesale_catalog=wholesale_catalog,
    )
