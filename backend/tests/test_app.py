from unittest.mock import MagicMock, patch

from app import app


def test_health():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "healthy"
    }


@patch("app.get_db_connection")
def test_get_users(mock_connection):
    mock_cursor = MagicMock()

    mock_cursor.fetchall.return_value = [
        (1, "Ahmed"),
        (2, "Mohamed")
    ]

    mock_connection.return_value.cursor.return_value = mock_cursor

    client = app.test_client()

    response = client.get("/users")

    assert response.status_code == 200

    assert response.get_json() == {
        "users": [
            {
                "id": 1,
                "name": "Ahmed"
            },
            {
                "id": 2,
                "name": "Mohamed"
            }
        ]
    }

    mock_cursor.execute.assert_called_once_with(
        "SELECT id, name FROM users ORDER BY id;"
    )


@patch("app.get_db_connection")
def test_get_user(mock_connection):
    mock_cursor = MagicMock()

    mock_cursor.fetchone.return_value = (1, "Ahmed")

    mock_connection.return_value.cursor.return_value = mock_cursor

    client = app.test_client()

    response = client.get("/users/1")

    assert response.status_code == 200

    assert response.get_json() == {
        "id": 1,
        "name": "Ahmed"
    }

    mock_cursor.execute.assert_called_once_with(
        "SELECT id, name FROM users WHERE id = %s;",
        (1,)
    )


@patch("app.get_db_connection")
def test_get_user_not_found(mock_connection):
    mock_cursor = MagicMock()

    mock_cursor.fetchone.return_value = None

    mock_connection.return_value.cursor.return_value = mock_cursor

    client = app.test_client()

    response = client.get("/users/999")

    assert response.status_code == 404

    assert response.get_json() == {
        "error": "User not found"
    }


@patch("app.get_db_connection")
def test_create_user(mock_connection):
    mock_cursor = MagicMock()

    mock_cursor.fetchone.return_value = (3, "Osama")

    mock_connection.return_value.cursor.return_value = mock_cursor

    client = app.test_client()

    response = client.post(
        "/users",
        json={
            "name": "Osama"
        }
    )

    assert response.status_code == 201

    assert response.get_json() == {
        "id": 3,
        "name": "Osama"
    }

    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO users (name) VALUES (%s) RETURNING id, name;",
        ("Osama",)
    )

    mock_connection.return_value.commit.assert_called_once()


@patch("app.get_db_connection")
def test_create_user_without_name(mock_connection):
    client = app.test_client()

    response = client.post(
        "/users",
        json={}
    )

    assert response.status_code == 400

    assert response.get_json() == {
        "error": "name is required"
    }

    mock_connection.assert_not_called()


@patch("app.get_db_connection")
def test_delete_user(mock_connection):
    mock_cursor = MagicMock()

    mock_cursor.fetchone.return_value = (1,)

    mock_connection.return_value.cursor.return_value = mock_cursor

    client = app.test_client()

    response = client.delete("/users/1")

    assert response.status_code == 200

    assert response.get_json() == {
        "message": "User deleted successfully"
    }

    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM users WHERE id = %s RETURNING id;",
        (1,)
    )

    mock_connection.return_value.commit.assert_called_once()


@patch("app.get_db_connection")
def test_delete_user_not_found(mock_connection):
    mock_cursor = MagicMock()

    mock_cursor.fetchone.return_value = None

    mock_connection.return_value.cursor.return_value = mock_cursor

    client = app.test_client()

    response = client.delete("/users/999")

    assert response.status_code == 404

    assert response.get_json() == {
        "error": "User not found"
    }

    mock_connection.return_value.commit.assert_called_once()