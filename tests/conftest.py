import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fast_zero.app import app
from fast_zero.models import table_registry

# A fixture is reusable setup logic for tests.


@pytest.fixture  # Create a fixture to create a test client and reuse it across tests
def client():
    return TestClient(app)


@pytest.fixture  # create a fixture to with a memory database engine & returns a session
def session():
    engine = create_engine('sqlite:///:memory:')  # setup the connection to the database / the engine is a bridge between the code and the db
    table_registry.metadata.create_all(engine)  # creates the database structure (tables) based on the metadata in table_registry

    with Session(engine) as session:  # start a session that is a temporary connection to the database / "with" stmt make the session closes
        yield session  # transform this fixture in a generator and return the session

    table_registry.metadata.drop_all(engine)  # drop the database
