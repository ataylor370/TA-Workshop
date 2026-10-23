import pytest

from app import app, tasks


@pytest.fixture
def client():
    """Provide a Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_tasks():
    """Reset the in-memory task list before each test."""
    tasks.clear()
    tasks.extend([
        {"id": 1, "title": "Project-1 Report"},
        {"id": 2, "title": "Project-2 MMFs"}
    ])


def test_index(client):
    """Render the task tracker and priority controls."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Task Tracker" in response.data
    assert b'id="task-priority"' in response.data
    assert b'<option value="Low">Low</option>' in response.data
    assert b'<option value="Medium" selected>Medium</option>' in response.data
    assert b'<option value="High">High</option>' in response.data


def test_get_tasks_defaults_missing_priority_to_medium(client):
    """Return Medium for stored tasks without a priority."""
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert all(task['priority'] == 'Medium' for task in data)


@pytest.mark.parametrize('priority', ['Low', 'Medium', 'High'])
def test_add_task_accepts_supported_priorities(client, priority):
    """Create tasks with each supported priority value."""
    response = client.post(
        '/api/tasks',
        json={"title": f"{priority} task", "priority": priority}
    )
    assert response.status_code == 201
    assert response.get_json()['priority'] == priority


def test_add_task_defaults_missing_priority_to_medium(client):
    """Default a missing priority to Medium when creating a task."""
    response = client.post('/api/tasks', json={"title": "Default task"})
    assert response.status_code == 201
    assert response.get_json()['priority'] == 'Medium'


def test_add_task_defaults_empty_priority_to_medium(client):
    """Default an empty priority to Medium when creating a task."""
    response = client.post(
        '/api/tasks',
        json={"title": "Empty priority task", "priority": ""}
    )
    assert response.status_code == 201
    assert response.get_json()['priority'] == 'Medium'


def test_add_task_rejects_invalid_priority(client):
    """Reject priorities outside the supported values."""
    response = client.post(
        '/api/tasks',
        json={"title": "Invalid task", "priority": "Urgent"}
    )
    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_get_tasks_returns_stored_priority(client):
    """Return the stored priority for tasks that provide one."""
    tasks.append({"id": 3, "title": "High priority task", "priority": "High"})

    response = client.get('/api/tasks')

    assert response.status_code == 200
    data = response.get_json()
    high_task = next(task for task in data if task['id'] == 3)
    assert high_task['priority'] == 'High'


def test_add_task_success(client):
    """Create a task successfully when no priority is provided."""
    response = client.post('/api/tasks', json={"title": "Test new task"})
    assert response.status_code == 201
    assert response.get_json()['title'] == "Test new task"
    assert response.get_json()['priority'] == "Medium"
    get_response = client.get('/api/tasks')
    assert len(get_response.get_json()) == 3


def test_add_task_missing_title(client):
    """Reject task creation requests without a title."""
    response = client.post('/api/tasks', json={"wrong_key": "value"})
    assert response.status_code == 400
    assert "error" in response.get_json()
    response2 = client.post('/api/tasks', json={})
    assert response2.status_code == 400


def test_delete_task(client):
    """Delete an existing task."""
    response = client.delete('/api/tasks/1')
    assert response.status_code == 200
    get_response = client.get('/api/tasks')
    data = get_response.get_json()
    assert len(data) == 1
    assert data[0]['id'] == 2
