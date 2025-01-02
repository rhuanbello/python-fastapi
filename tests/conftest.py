import factory  # type: ignore
import factory.fuzzy  # type: ignore
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer  # type: ignore

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import Todo, TodoState, User, table_registry
from fast_zero.security import get_password_hash


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')  # Generate a unique username for each user (e.g. test1, test2, test3)
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')  # Generate a unique email for each user (e.g. test1@test.com)
    password = factory.LazyAttribute(lambda obj: f'{obj.username}+{obj.email}')  # Generate a unique password for each user(e.g. test1+test1@test.com)


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


@pytest.fixture  # Create a fixture to create a test client and reuse it across tests
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override

        yield client


@pytest.fixture(scope='session')  # Create a fixture to create a database engine
def engine():
    with PostgresContainer('postgres:16', driver='psycopg') as postgres:  # Create a Postgres container
        _engine = create_engine(postgres.get_connection_url())

        with _engine.begin():
            yield _engine  # Return the engine


@pytest.fixture  # create a fixture to with a memory database engine & returns a session
def session(engine):  # receives the engine fixture
    table_registry.metadata.create_all(engine)  # creates the database structure (tables) based on the metadata in table_registry

    with Session(engine) as session:  # start a session that is a temporary connection to the database / "with" stmt make the session closes
        yield session  # transform this fixture in a generator and return the session

    table_registry.metadata.drop_all(engine)  # drop the database


@pytest.fixture
def user(session):
    pwd = 'testtest'

    user = UserFactory(password=get_password_hash(pwd))

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = pwd

    return user


@pytest.fixture
def other_user(session):
    user = UserFactory()

    session.add(user)
    session.commit()
    session.refresh(user)

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
