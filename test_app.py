import pytest
import os
import tempfile
from app import app, init_db
import app as app_module


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    app_module.DB_PATH = db_path
    app.config['TESTING'] = True

    with app.test_client() as client:
        init_db()
        yield client

    os.unlink(db_path)


def test_get_todos_empty(client):
    response = client.get('/todos')
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_todo(client):
    response = client.post('/todos', json={'title': 'Test todo', 'description': 'A test'})
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == 'Test todo'
    assert data['description'] == 'A test'
    assert data['done'] == False
    assert 'id' in data


def test_create_todo_missing_title(client):
    response = client.post('/todos', json={'description': 'No title here'})
    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_get_todo_by_id(client):
    create_response = client.post('/todos', json={'title': 'Fetch me'})
    todo_id = create_response.get_json()['id']

    response = client.get(f'/todos/{todo_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == todo_id
    assert data['title'] == 'Fetch me'


def test_get_todo_not_found(client):
    response = client.get('/todos/9999')
    assert response.status_code == 404
    assert 'error' in response.get_json()


def test_update_todo(client):
    create_response = client.post('/todos', json={'title': 'Update me'})
    todo_id = create_response.get_json()['id']

    response = client.put(f'/todos/{todo_id}', json={'title': 'Updated', 'description': 'New desc', 'done': True})
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Todo updated'


def test_update_todo_not_found(client):
    response = client.put('/todos/9999', json={'title': 'Ghost', 'description': '', 'done': False})
    assert response.status_code == 404
    assert 'error' in response.get_json()


def test_delete_todo(client):
    create_response = client.post('/todos', json={'title': 'Delete me'})
    todo_id = create_response.get_json()['id']

    response = client.delete(f'/todos/{todo_id}')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Todo deleted'


def test_delete_todo_not_found(client):
    response = client.delete('/todos/9999')
    assert response.status_code == 404
    assert 'error' in response.get_json()
