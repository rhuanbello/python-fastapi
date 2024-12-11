from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.app import app


def test_read_root_must_return_ok_and_hello_world():
    client = TestClient(app)  # ARRANGE the test

    response = client.get('/')  # ACT to request the '/' route

    assert response.status_code == HTTPStatus.OK  # ASSERT the response is OK
    assert response.json() == {'message': 'Hello World'}  # ASSERT the response is correct
