from enum import Enum
from pydantic import BaseModel, Field, HttpUrl

from fastapi import Body, FastAPI, Query, Path


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


# Path Parameters and Query parameters
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


# This should be called as "http://127.0.0.1:8000/items/?skip=0&limit=10"
# @app.get("/items/")
# async def read_item(skip: int = 0, limit: int = 10):
#     return fake_items_db[skip : skip + limit]


# optional_param param is optional
# needy, a required str.
# skip, an int with a default value of 0.
# limit, an optional int.
# @app.get("/items/{item_id}")
# async def read_user_item(
#     item_id: str, needy: str, skip: int = 0, limit: int | None = None
# ):
#     item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
#     return item


# @app.get("/items/{item_id}")
# async def read_item(item_id: int):
#     return {"item_id": item_id}


# /users/me must be declared before the one for /users/{user_id} Otherwise,
# the path for /users/{user_id} would match also for /users/me, "thinking" 
# that it's receiving a parameter user_id with a value of "me".
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


# Path parameters containing paths
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


# Multiple path and query parameters
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


# Request Body
class Image(BaseModel):
    url: HttpUrl
    name: str

class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None
    tags: set[str] = set()
    images: list[Image] | None = None

class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]

class User(BaseModel):
    username: str
    full_name: str | None = None

@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer

@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


@app.put("/items/{item_id}")
async def update_item(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
    item: Item, 
    user: User, 
    importance: Annotated[int, Body(gt=0)],
):
    """
        Expected Body:
        {
            "item": {
                "name": "Foo",
                "description": "The pretender",
                "price": 42.0,
                "tax": 3.2
            },
            "user": {
                "username": "dave",
                "full_name": "Dave Grohl"
            },
            "importance": 5
        }
    """
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results

# Request body + path + query parameters
# * If the parameter is also declared in the path, it will be used as a path parameter.
# * If the parameter is of a singular type (like int, float, str, bool, etc)
#   it will be interpreted as a query parameter.
# * If the parameter is declared to be of the type of a Pydantic model,
#   it will be interpreted as a request body.
@app.get("/items/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="The ID of the item to get", gt=0, le=1000)],
    size: Annotated[float, Query(gt=0, lt=10.5)],
    q: Annotated[str | None, Query(alias="item-query")] = None,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    results.update({"size": size})
    return results


# http://127.0.0.1:8000/items/?no-pythonic-name=fixedquery&r=required_param&s=some1&s=some2
@app.get("/items/")
async def read_items(    
    r: Annotated[
        str, Query(min_length=3, max_length=50, pattern="^required_param$")
    ],
    p: Annotated[
        str | None, Query(min_length=3, max_length=50, pattern="^fixedquery$")
    ] = "default_value",
    q: Annotated[
        str | None, Query(title="Query string",
                          description="Query string for the items to search in the database that have a good match",
                          alias="no-pythonic-name",
                          min_length=3, max_length=50, pattern="^fixedquery$")
    ] = None,
    s: Annotated[list[str], Query()] = ["optional_1", "optional_2"],
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if p:
        results.update({"p": p})
    if q:
        results.update({"q": q})
    results.update({"r": r})
    results.update({"s": s})

    return results