# FastAPI Docs

Library /tiangolo/fastapi has been redirected to this library: /fastapi/fastapi.

---

# SQLAlchemy Docs

### Setup SQLAlchemy ORM and Session for Examples

Source: https://github.com/sqlalchemy/sqlalchemy/blob/main/doc/build/core/operators.rst

This comprehensive Python setup script initializes a SQLAlchemy engine, defines database schemas using both `MetaData` (Core) and `declarative_base` (ORM), establishes one-to-many relationships, creates tables, and populates sample data. It also starts a database session, preparing the environment for demonstrating SQL expression operators.

```python
from sqlalchemy import column, select
from sqlalchemy import create_engine
engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
from sqlalchemy import MetaData, Table, Column, Integer, String, Numeric
metadata_obj = MetaData()
user_table = Table(
    "user_account",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(30)),
    Column("fullname", String),
)
from sqlalchemy import ForeignKey
address_table = Table(
    "address",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("user_id", None, ForeignKey("user_account.id")),
    Column("email_address", String, nullable=False),
)
metadata_obj.create_all(engine)
from sqlalchemy.orm import declarative_base
Base = declarative_base()
from sqlalchemy.orm import relationship
class User(Base):
    __tablename__ = "user_account"

    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    fullname = Column(String)

    addresses = relationship("Address", back_populates="user")

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user_account.id"))

    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"
conn = engine.connect()
from sqlalchemy.orm import Session
session = Session(conn)
session.add_all(
    [
        User(
            name="spongebob",
            fullname="Spongebob Squarepants",
            addresses=[Address(email_address="spongebob@sqlalchemy.org")],
        ),
        User(
            name="sandy",
            fullname="Sandy Cheeks",
            addresses=[
                Address(email_address="sandy@sqlalchemy.org"),
                Address(email_address="squirrel@squirrelpower.org"),
            ],
        ),
        User(
            name="patrick",
            fullname="Patrick Star",
            addresses=[Address(email_address="pat999@aol.com")],
        ),
        User(
            name="squidward",
            fullname="Squidward Tentacles",
            addresses=[Address(email_address="stentcl@sqlalchemy.org")],
        ),
        User(name="ehkrabs", fullname="Eugene H. Krabs"),
    ]
)
session.commit()
conn.begin()
```

--------------------------------

### Install SQLAlchemy Manually from Source Distribution

Source: https://github.com/sqlalchemy/sqlalchemy/blob/main/doc/build/intro.rst

Installs SQLAlchemy from a source distribution using the `setup.py` script. This method is platform-agnostic and will attempt to build Cython extensions if available, falling back to a pure Python installation otherwise.

```bash
python setup.py install
```

--------------------------------

### Manually Build SQLAlchemy Cython Extensions from Source

Source: https://github.com/sqlalchemy/sqlalchemy/blob/main/doc/build/intro.rst

Detailed steps to manually build and install SQLAlchemy, including its Cython extensions, from a source distribution. This process requires navigating to the source directory, installing Cython, and then using `setup.py` to build extensions and install the package.

```bash
# cd into SQLAlchemy source distribution
cd path/to/sqlalchemy

# install cython
pip install cython

# optionally build Cython extensions ahead of install
python setup.py build_ext

# run the install
python setup.py install
```

--------------------------------

### Install SQLAlchemy with AsyncIO Support

Source: https://github.com/sqlalchemy/sqlalchemy/blob/main/doc/build/intro.rst

Installs SQLAlchemy along with its asynchronous I/O support, which depends on the `greenlet` project. This command ensures `greenlet` is included as a dependency for asyncio functionality.

```bash
pip install sqlalchemy[asyncio]
```

--------------------------------

### Build SQLAlchemy Source/Wheel Distributions with `build`

Source: https://github.com/sqlalchemy/sqlalchemy/blob/main/doc/build/intro.rst

Demonstrates how to use the `build` tool (a PEP 517 compliant frontend) to create source and wheel distributions of SQLAlchemy from its source directory. This method requires installing the `build` package first.

```bash
# cd into SQLAlchemy source distribution
cd path/to/sqlalchemy

# install build
pip install build

# build source / wheel dists
python -m build
```

--------------------------------

### Define SQLAlchemy ORM models and fixture data in Python

Source: https://github.com/sqlalchemy/sqlalchemy/blob/main/doc/build/orm/queryguide/_plain_setup.rst

This Python snippet defines several SQLAlchemy ORM models (User, Address, Order, Item) with relationships using DeclarativeBase, creates a SQLite in-memory database engine, and populates it with initial fixture data for demonstration purposes. It establishes the schema and base data used for subsequent querying examples in the guide.

```python
from typing import List
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy import Table
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session


class Base(DeclarativeBase):
    pass
class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    fullname: Mapped[Optional[str]]
    addresses: Mapped[List["Address"]] = relationship(back_populates="user")
    orders: Mapped[List["Order"]] = relationship()

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"
class Address(Base):
    __tablename__ = "address"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    email_address: Mapped[str]
    user: Mapped[User] = relationship(back_populates="addresses")

    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"
order_items_table = Table(
    "order_items",
    Base.metadata,
    Column("order_id", ForeignKey("user_order.id"), primary_key=True),
    Column("item_id", ForeignKey("item.id"), primary_key=True),
)

class Order(Base):
    __tablename__ = "user_order"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    items: Mapped[List["Item"]] = relationship(secondary=order_items_table)
class Item(Base):
    __tablename__ = "item"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
Base.metadata.create_all(engine)
conn = engine.connect()
session = Session(conn)
session.add_all(
    [
        User(
            name="spongebob",
            fullname="Spongebob Squarepants",
            addresses=[Address(email_address="spongebob@sqlalchemy.org")],
        ),
        User(
            name="sandy",
            fullname="Sandy Cheeks",
            addresses=[
                Address(email_address="sandy@sqlalchemy.org"),
                Address(email_address="squirrel@squirrelpower.org"),
            ],
        ),
        User(
            name="patrick",
            fullname="Patrick Star",
            addresses=[Address(email_address="pat999@aol.com")],
        ),
        User(
            name="squidward",
            fullname="Squidward Tentacles",
            addresses=[Address(email_address="stentcl@sqlalchemy.org")],
        ),
        User(name="ehkrabs", fullname="Eugene H. Krabs"),
    ]
)
session.commit()
conn.begin()
```

--------------------------------

### SQLAlchemy Window Function Basic Setup

Source: https://github.com/sqlalchemy/sqlalchemy/blob/main/doc/build/changelog/migration_07.rst

Illustrates the initial setup for using SQLAlchemy's window function construct. It imports necessary components and defines a table, then begins a select statement to apply an aggregate function in a window context.

```python
from sqlalchemy.sql import table, column, select, func

empsalary = table("empsalary", column("depname"), column("empno"), column("salary"))

s = select(
        [
            empsalary,
            func.avg(empsalary.c.salary)
```

--------------------------------

### Define SQLAlchemy ORM Models and Populate Database with Sample Data

Source: https://github.com/sqlalchemy/sqlalchemy/blob/main/doc/build/orm/queryguide/_deferred_setup.rst

This Python code defines `User` and `Book` ORM models using SQLAlchemy's DeclarativeBase, including column types like `LargeBinary` and `Text`, and establishes a one-to-many relationship. It then initializes an in-memory SQLite database, creates the defined tables, and populates them with sample user and book data, committing the changes to the database. This setup is used as fixture data for ORM query examples.

```python
from typing import List
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy import LargeBinary
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session


class Base(DeclarativeBase):
    pass
class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    fullname: Mapped[Optional[str]]
    books: Mapped[List["Book"]] = relationship(back_populates="owner")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"
class Book(Base):
    __tablename__ = "book"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    title: Mapped[str]
    summary: Mapped[str] = mapped_column(Text)
    cover_photo: Mapped[bytes] = mapped_column(LargeBinary)
    owner: Mapped["User"] = relationship(back_populates="books")

    def __repr__(self) -> str:
        return f"Book(id={self.id!r}, title={self.title!r})"
engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
Base.metadata.create_all(engine)
conn = engine.connect()
session = Session(conn)
session.add_all(
    [
        User(
            name="spongebob",
            fullname="Spongebob Squarepants",
            books=[
                Book(
                    title="100 Years of Krabby Patties",
                    summary="some long summary",
                    cover_photo=b"binary_image_data",
                ),
                Book(
                    title="Sea Catch 22",
                    summary="another long summary",
                    cover_photo=b"binary_image_data",
                ),
                Book(
                    title="The Sea Grapes of Wrath",
                    summary="yet another summary",
                    cover_photo=b"binary_image_data",
                ),
            ],
        ),
        User(
            name="sandy",
            fullname="Sandy Cheeks",
            books=[
                Book(
                    title="A Nut Like No Other",
                    summary="some long summary",
                    cover_photo=b"binary_image_data",
                ),
                Book(
                    title="Geodesic Domes: A Retrospective",
                    summary="another long summary",
                    cover_photo=b"binary_image_data",
                ),
                Book(
                    title="Rocketry for Squirrels",
                    summary="yet another summary",
                    cover_photo=b"binary_image_data",
                ),
            ],
        ),
    ]
)
session.commit()
session.close()
conn.begin()
```

--------------------------------

### Check Installed SQLAlchemy Version

Source: https://github.com/sqlalchemy/sqlalchemy/blob/main/doc/build/intro.rst

Illustrates how to programmatically check the installed version of SQLAlchemy from a Python interactive prompt. It imports the `sqlalchemy` module and accesses its `__version__` attribute to display the current version.

```python
import sqlalchemy
sqlalchemy.__version__  # doctest: +SKIP
```

--------------------------------

### Generate SQLAlchemy `Sequence` DDL Across Versions and Explicitly

Source: https://github.com/sqlalchemy/sqlalchemy/blob/main/doc/build/changelog/whatsnew_20.rst

These Python examples demonstrate how SQLAlchemy's `Sequence` construct generates DDL for creating database sequences. It covers the default `CREATE SEQUENCE` behavior in SQLAlchemy 1.3/2.0, the temporary `START WITH 1` default in 1.4, and the recommended explicit `start=1` parameter to ensure consistent DDL generation across all SQLAlchemy versions and database backends.

```python
# SQLAlchemy 1.3 (and 2.0) behavior
from sqlalchemy import Sequence
from sqlalchemy.schema import CreateSequence
print(CreateSequence(Sequence("my_seq")))
# DDL output: CREATE SEQUENCE my_seq
```

```python
# SQLAlchemy 1.4 (only) behavior, adding START WITH 1 by default
from sqlalchemy import Sequence
from sqlalchemy.schema import CreateSequence
print(CreateSequence(Sequence("my_seq")))
# DDL output: CREATE SEQUENCE my_seq START WITH 1
```

```python
# All SQLAlchemy versions: Explicitly setting start=1 for consistency
from sqlalchemy import Sequence
from sqlalchemy.schema import CreateSequence
print(CreateSequence(Sequence("my_seq", start=1)))
# DDL output: CREATE SEQUENCE my_seq START WITH 1
```