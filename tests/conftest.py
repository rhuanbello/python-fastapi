import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry
from fast_zero.security import get_password_hash

# A fixture is reusable setup logic for tests.


@pytest.fixture  # Create a fixture to create a test client and reuse it across tests
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override

        yield client


@pytest.fixture  # create a fixture to with a memory database engine & returns a session
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )  # setup the connection to the database / the engine is a bridge between the code and the db
    table_registry.metadata.create_all(engine)  # creates the database structure (tables) based on the metadata in table_registry

    with Session(engine) as session:  # start a session that is a temporary connection to the database / "with" stmt make the session closes
        yield session  # transform this fixture in a generator and return the session

    table_registry.metadata.drop_all(engine)  # drop the database


@pytest.fixture
def user(session):
    pwd = 'testtest'
    user = User(username='John Doe', email='john.doe@example.com', password=get_password_hash(pwd))

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = pwd

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )

    return response.json()['access_token']
