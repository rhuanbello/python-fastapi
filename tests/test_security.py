from http import HTTPStatus

from jwt import decode

from fast_zero.security import create_access_token
from fast_zero.settings import Settings

settings = Settings()  # type: ignore


def test_jwt():
    data = {'sub': 'test@test.com'}
    token = create_access_token(data)

    result = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert result['sub'] == data['sub']
    assert result['exp']


def test_get_token_with_invalid_token(client, user):
    response = client.delete(
        '/users/1',
        headers={'Authorization': 'Bearer token-invalido'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Could not validate credentials',
    }
