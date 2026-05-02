from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
import sqlalchemy
from src.api import auth
from enum import Enum
from typing import List, Optional
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)



class SearchSortOptions(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"


class SearchSortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class LineItem(BaseModel):
    line_item_id: int
    item_sku: str
    customer_name: str
    line_item_total: int
    timestamp: str


class SearchResponse(BaseModel):
    previous: Optional[str] = None
    next: Optional[str] = None
    results: List[LineItem]


@router.get("/search/", response_model=SearchResponse, tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: SearchSortOptions = SearchSortOptions.timestamp,
    sort_order: SearchSortOrder = SearchSortOrder.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.
    """
    return SearchResponse(
        previous=None,
        next=None,
        results=[
            LineItem(
                line_item_id=1,
                item_sku="1 oblivion potion",
                customer_name="Scaramouche",
                line_item_total=50,
                timestamp="2021-01-01T00:00:00Z",
            )
        ],
    )


cart_id_counter = 1
carts: dict[int, dict[str, int]] = {}


class Customer(BaseModel):
    customer_id: str
    customer_name: str
    character_class: str
    character_species: str
    level: int = Field(ge=1, le=20)


@router.post("/visits/{visit_id}", status_code=status.HTTP_204_NO_CONTENT)
def post_visits(visit_id: int, customers: List[Customer]):
    """
    Shares the customers that visited the store on that tick.
    """
    print(customers)
    pass


class CartCreateResponse(BaseModel):
    cart_id: int


@router.post("/", response_model=CartCreateResponse)
def create_cart(new_cart: Customer):
    """
    Creates a new cart for a specific customer.
    """

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT id
                FROM customers
                WHERE id = :id
                """
            ),
            [{"id": new_cart.customer_id}],
        ).all()

    if len(result) == 0:
        with db.engine.begin() as connection:
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO customers (id, name, class, species, level)
                    VALUES (:id, :name, :class, :species, :level)
                    """
                ),
                [{
                "id": new_cart.customer_id,
                "name": new_cart.customer_name,
                "class": new_cart.character_class,
                "species": new_cart.character_species,
                "level": new_cart.level
                }]
            )

    #TODO: Ensure Idempotency guard occurs here.
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO customer_carts (customer_id)
                VALUES (:customer_id)
                returning id
                """
            ),
            [{
            "customer_id": new_cart.customer_id,
            }]
        ).one()
        cart_id = result.id

    #if uniqueness constraint error return old cart id
    #else return the new id
    return CartCreateResponse(cart_id=cart_id)


class CartItem(BaseModel):
    quantity: int = Field(ge=1, description="Quantity must be at least 1")


@router.post("/{cart_id}/items/{item_sku}", status_code=status.HTTP_204_NO_CONTENT)
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    print(
        f"cart_id: {cart_id}, item_sku: {item_sku}, cart_item: {cart_item}, carts: {carts}"
    )

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT *
                FROM customer_carts
                WHERE id = :cart_id
                """
            ),
            [{"cart_id":cart_id}]
        ).all()

    if len(result) == 0:
        raise HTTPException(status_code=404, detail="Cart not found")

    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO cart_items (item_sku, customer_cart_id, quantity)
                VALUES (:new_item, :cart, :new_quantity)
                """
            ),
            [{"new_item": item_sku, "cart":cart_id, "new_quantity":cart_item.quantity}]
        )
    return status.HTTP_204_NO_CONTENT


class CheckoutResponse(BaseModel):
    total_potions_bought: int
    total_gold_paid: int


class CartCheckout(BaseModel):
    payment: str


@router.post("/{cart_id}/checkout", response_model=CheckoutResponse)
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """
    Handles the checkout process for a specific cart.
    """
    transaction_id = 0
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO transactions (time)
                VALUES (CURRENT_TIMESTAMP)
                returning id
                """
            )
        ).one()
        transaction_id = result.id

    customer_id = 0
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT id
                FROM customer_carts
                WHERE id = :cart_id
                """
            ),
            [{"cart_id":cart_id}]
        ).all()

    if len(result) == 0:
        raise HTTPException(status_code=404, detail="Cart not found")

    with db.engine.begin() as connection:
        cart_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT *
                FROM cart_items
                WHERE customer_cart_id = :cart_id
                """
            ),
            [{"cart_id":cart_id}]
        ).all()

        cart_result_list = [itm._asdict() for itm in cart_result]

    with db.engine.begin() as connection:
        potion_inventory = connection.execute(
            sqlalchemy.text(
                """
                SELECT sku, price
                FROM potions
                """
            )
        )
        potion_inventory_list = [potion._asdict() for potion in potion_inventory]

    potion_prices = {potion["sku"]:potion["price"] for potion in potion_inventory_list}
    cart_quantities = {itm["item_sku"]: itm["quantity"] for itm in cart_result_list}

    total_potions_bought = 0
    total_gold_paid = 0
    for key in cart_quantities.keys():
        total_potions_bought += cart_quantities[key]
        total_gold_paid += potion_prices[key] * cart_quantities[key]


    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO gold_ledger 
                (transaction_id, change)
                VALUES 
                (:transaction_id, :total_gold_paid)
                """
            ),
            [{"transaction_id": transaction_id,
              "total_gold_paid": total_gold_paid
            }],
        )

    for key in cart_quantities.keys():
        potion_cost = cart_quantities[key]
        with db.engine.begin() as connection:
            connection.execute(
                sqlalchemy.text(
                    """
                        INSERT INTO potion_ledger 
                        (transaction_id, potion_id, change)
                        SELECT :transaction_id, id, :change
                        FROM potions
                        WHERE sku = :key
                    """
                ),
                [{"transaction_id": transaction_id,
                  "change": -1 * potion_cost,
                  "key": key
                }],
            )

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT customer_id 
                FROM customer_carts
                WHERE id = :cart_id
                """
            ),
            [{"cart_id": cart_id}],
        ).one()

        customer_id = result.customer_id

    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO customer_transactions 
                (customer_id, transaction_id)
                VALUES 
                (:customer_id, :transaction_id)
                
                """
            ),
            [{"customer_id": customer_id,
              "transaction_id": transaction_id}],
        )

    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM cart_items
                WHERE customer_cart_id = :cart_id
                """
            ),
            [{"cart_id": cart_id}],
        )

    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM customer_carts
                WHERE id = :cart_id
                """
            ),
            [{"cart_id": cart_id}],
        )

    return CheckoutResponse(
        total_potions_bought=total_potions_bought, total_gold_paid=total_gold_paid
    )
