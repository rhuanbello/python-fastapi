from http import HTTPStatus

from tests.conftest import TodoFactory


def test_create_todo(client, token):
    response = client.post('/todos', headers={'Authorization': f'Bearer {token}'}, json={'title': 'test', 'description': 'test', 'state': 'draft'})

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'title': 'test',
        'description': 'test',
        'state': 'draft',
    }


def test_list_todos_should_return_5_todos(session, client, user, token):
    expected_todos = 5

    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))  # bulk is an session.add() but for multiple objects
    session.commit()

    response = client.get('/todos', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_pagination_should_return_2_todos(session, client, user, token):
    expected_todos = 2

    session.bulk_save_objects(TodoFactory.create_batch(7, user_id=user.id))
    session.commit()

    response = client.get('/todos', params={'offset': 5, 'limit': 2}, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_filter_title_should_return_5_todos(session, client, user, token):
    expected_todos = 5

    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id, title='Test todo 1'))
    session.bulk_save_objects(TodoFactory.create_batch(2, user_id=user.id, title='Test todo 2'))
    session.commit()

    response = client.get('/todos', params={'title': 'Test todo 1'}, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_filter_description_should_return_5_todos(session, client, user, token):
    expected_todos = 5

    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id, description='description todo 1'))
    session.bulk_save_objects(TodoFactory.create_batch(2, user_id=user.id, description='description todo 2'))
    session.commit()

    response = client.get('/todos', params={'description': 'description todo 1'}, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_filter_state_should_return_5_todos(session, client, user, token):
    expected_todos = 5

    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id, state='draft'))

    session.commit()

    response = client.get('/todos', params={'state': 'draft'}, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_filter_combined_should_return_5_todos(session, client, user, token):
    expected_todos = 5

    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id, title='Test todo 1', description='description todo 1', state='draft'))
    session.bulk_save_objects(TodoFactory.create_batch(2, user_id=user.id, title='Test todo 2', description='description todo 2', state='draft'))
    session.commit()

    response = client.get(
        '/todos', params={'title': 'Test todo 1', 'description': 'description todo 1', 'state': 'draft'}, headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_delete_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()

    response = client.delete(f'/todos/{todo.id}', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Todo deleted'}


def test_delete_todo_not_found(client, token):
    response = client.delete('/todos/1', headers={'Authorization': f'Bearer {token}'})
    assert response.json() == {'detail': 'Todo not found'}


def test_patch_todo_title(session, client, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        json={'title': 'teste!'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'teste!'


def test_patch_todo_description(session, client, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        json={'description': 'teste!'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['description'] == 'teste!'


def test_patch_todo_state(session, client, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        json={'state': 'doing'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['state'] == 'doing'


def test_patch_todo_not_found(client, token):
    response = client.patch('/todos/1', headers={'Authorization': f'Bearer {token}'}, json={'title': 'Test todo'})
    assert response.json() == {'detail': 'Todo not found'}
