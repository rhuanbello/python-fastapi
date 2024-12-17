from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'John Doe',
            'email': 'john.doe@example.com',
            'password': 'password123',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'John Doe',
        'email': 'john.doe@example.com',
    }


def test_read_users(client):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()  # convert the user_db to a user_schema
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Jane Doe',
            'email': 'jane.doe@example.com',
            'password': 'password123',
            'id': user.id,
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': 'Jane Doe',
        'email': 'jane.doe@example.com',
    }


def test_delete_user(client, user, token):
    response = client.delete('/users/1', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_wrong_user(client, user, token):
    response = client.delete('/users/2', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.FORBIDDEN
