# How to: Add a New API Endpoint

## Step-by-Step

### 1. Create the schema (`app/schemas/`)

```python
# app/schemas/order.py
from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    product: str
    quantity: int = Field(ge=1)
    price: float = Field(ge=0)


class OrderResponse(BaseModel):
    id: str
    product: str
    quantity: int
    price: float
    total: float
```

{%- if cookiecutter.use_database %}

### 2. Create the database model (`app/db/models/`)

```python
# app/db/models/order.py
{%- if cookiecutter.use_sqlalchemy %}
from sqlalchemy import Column, String, Integer, Float
from app.db.base import Base, TimestampMixin

class Order(TimestampMixin, Base):
    __tablename__ = "orders"
    id = Column(String, primary_key=True)
    product = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
{%- elif cookiecutter.use_sqlmodel %}
from sqlmodel import SQLModel, Field

class Order(SQLModel, table=True):
    __tablename__ = "orders"
    id: str = Field(primary_key=True)
    product: str
    quantity: int
    price: float
{%- endif %}
```

Don't forget to import it in `app/db/models/__init__.py`.

### 3. Create the repository (`app/repositories/`)

```python
# app/repositories/order.py
from app.repositories.base import BaseRepository
from app.db.models.order import Order

class OrderRepository(BaseRepository[Order]):
    model = Order
```

### 4. Create the service (`app/services/`)

```python
# app/services/order.py
from app.repositories.order import OrderRepository
from app.schemas.order import OrderCreate

class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repo = repository

    async def create_order(self, data: OrderCreate) -> dict:
        order = await self.repo.create({
            **data.model_dump(),
            "total": data.price * data.quantity,
        })
        await self.repo.session.flush()
        return order
```
{%- endif %}

### 5. Create the route (`app/api/routes/v1/`)

```python
# app/api/routes/v1/orders.py
from fastapi import APIRouter, status
from app.schemas.order import OrderCreate, OrderResponse
{%- if cookiecutter.use_jwt %}
from app.api.deps import CurrentUser
{%- endif %}

router = APIRouter()

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: OrderCreate,
{%- if cookiecutter.use_jwt %}
    current_user: CurrentUser,
{%- endif %}
):
    # Your logic here
    ...
```

### 6. Register the route

In `app/api/routes/v1/__init__.py`:

```python
from app.api.routes.v1 import orders

v1_router.include_router(orders.router, prefix="/orders", tags=["orders"])
```

### 7. Create and apply migration

```bash
make db-migrate    # Enter message: "Add orders table"
make db-upgrade
```

### 8. Test it

Visit `http://localhost:{{ cookiecutter.backend_port }}/docs` and try the new endpoint.
