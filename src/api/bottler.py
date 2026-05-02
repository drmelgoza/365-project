from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator
from typing import List
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)


class PotionMixes(BaseModel):
    potion_type: List[int] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="Must contain exactly 4 elements: [r, g, b, d]",
    )
    quantity: int = Field(
        ..., ge=1, le=10000, description="Quantity must be between 1 and 10,000"
    )

    @field_validator("potion_type")
    @classmethod
    def validate_potion_type(cls, potion_type: List[int]) -> List[int]:
        if sum(potion_type) != 100:
            raise ValueError("Sum of potion_type values must be exactly 100")
        return potion_type

# update your ml to subtract the liquid used up and add the potions you just mixed
# each potion mix object has a quantity and an amnt for each of r, g, b.
# multiply r, g, b values each by the quantity and subtract that from the stock
# add quantity into each value based on the type and quantity

@router.post("/deliver/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def post_deliver_bottles(potions_delivered: List[PotionMixes], order_id: int):
    """
    Delivery of potions requested after plan. order_id is a unique value representing
    a single delivery; the call is idempotent based on the order_id.
    """
    red_ml_cost = sum((potion.potion_type[0] * potion.quantity) for potion in potions_delivered)
    green_ml_cost = sum((potion.potion_type[1] * potion.quantity) for potion in potions_delivered)
    blue_ml_cost = sum((potion.potion_type[2] * potion.quantity) for potion in potions_delivered)
    dark_ml_cost = sum((potion.potion_type[3] * potion.quantity) for potion in potions_delivered)

    transaction_id = 0

    with db.engine.begin() as connection:
        result_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO transactions (time)
                VALUES (CURRENT_TIMESTAMP)
                returning id
                """
            )
        ).one()

        transaction_id = result_id.id

    #iterate through every delivered potion
    for potion_mix in potions_delivered:
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT id
                    FROM potions
                    WHERE mix[1] = :red
                    AND mix[2] = :green
                    AND mix[3] = :blue
                    AND mix[4] = :dark
                    """
                ),
                [{
                    "red": potion_mix.potion_type[0],
                    "green": potion_mix.potion_type[1],
                    "blue": potion_mix.potion_type[2],
                    "dark": potion_mix.potion_type[3],
                }]
            ).one()

            potion_id = result.id

        with db.engine.begin() as connection:
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO potion_ledger (transaction_id, potion_id, change)
                    VALUES (:transaction_id, :potion_id, :change)
                    """
                ),
                [{
                    "transaction_id": transaction_id,
                    "potion_id": potion_id,
                    "change": potion_mix.quantity
                }]
            )

    #update the global_inventory resources
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO ml_ledger 
                (transaction_id, change_red, change_green, change_blue, change_dark)
                VALUES 
                (:transaction_id, :red_ml_cost, :green_ml_cost, :blue_ml_cost, :dark_ml_cost)
                """
            ),
            [{
                "transaction_id": transaction_id,
                "red_ml_cost": (-1 * red_ml_cost),
                "green_ml_cost": (-1 * green_ml_cost),
                "blue_ml_cost": (-1 * blue_ml_cost),
                "dark_ml_cost": (-1 * dark_ml_cost)
            }],
        )

    print(f"potions delivered: {potions_delivered} order_id: {order_id}")


def create_bottle_plan(
    red_ml: int,
    green_ml: int,
    blue_ml: int,
    dark_ml: int,
    maximum_potion_capacity: int,
    current_potion_inventory: List[PotionMixes],
) -> List[PotionMixes]:
    #get remaining amount of potions possible
    remaining_potions = maximum_potion_capacity - sum(potion_type.quantity for potion_type in current_potion_inventory)
    remaining_mls = [red_ml, green_ml, blue_ml, dark_ml]

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, sku, mix
                FROM potions
                ORDER BY id ASC
                """
            )
        ).all()
        potions = [potion._asdict() for potion in result]
        formulas = {potion["sku"]: potion["mix"] for potion in potions}

    quantities = {}
    previous_sum = -1
    current_sum = 0
    #loop occurs only while potions are being added to the quantities dictionary
    while previous_sum < current_sum:
        if remaining_potions > 0:
            for potion in potions:
                current_sku = potion["sku"]
                current_formula = formulas[current_sku]
                is_possible = True
                for i in range(0, 4):
                    if current_formula[i] > remaining_mls[i]:
                        is_possible = False
                if is_possible:
                    for i in range(0, 4):
                        remaining_mls[i] -= current_formula[i]
                    if current_sku not in quantities:
                        quantities[current_sku] = 1
                    else:
                        quantities[current_sku] += 1
                    remaining_potions -= 1
        previous_sum = current_sum
        current_sum = sum(quantities.values())

    mixes = []
    for sku in quantities.keys():
        mixes.append(PotionMixes(potion_type=formulas[sku], quantity=quantities[sku]))

    return mixes

@router.post("/plan", response_model=List[PotionMixes])
def get_bottle_plan():
    """
    Gets the plan for bottling potions.
    Each bottle has a quantity of what proportion of red, green, blue, and dark potions to add.
    Colors are expressed in integers from 0 to 100 that must sum up to exactly 100.
    """
    #query database to retrieve ml numbers, capacity, and inventory
    with db.engine.begin() as connection:
        row = connection.execute(
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

        #store values from database
        red_ml = row.red
        green_ml = row.green
        blue_ml = row.blue
        dark_ml = row.dark

    #query database for potion ingredients and potion quantities.
    #only return potions that are in-stock.
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT mix, COALESCE(SUM(change), 0) as quantity
                FROM potions
                JOIN potion_ledger on potions.id = potion_ledger.potion_id
                GROUP BY potions.id, potions.mix
                HAVING COALESCE(SUM(change), 0) > 0
                """
            )
        ).all()
        potions = [potion._asdict() for potion in result]

    inventory = []
    for potion in potions:
        formula = potion["mix"]
        mix = PotionMixes(potion_type=formula, quantity=potion["quantity"])
        inventory.append(mix)

    return create_bottle_plan(
        red_ml=red_ml,
        green_ml=green_ml,
        blue_ml=blue_ml,
        dark_ml=dark_ml,
        maximum_potion_capacity=50,
        current_potion_inventory=inventory,
    )


if __name__ == "__main__":
    print(get_bottle_plan())
