import os

import psycopg2
from flask import Flask, jsonify, request , redirect

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "devops_app"),
        user=os.getenv("DB_USER", "devops_user"),
        password=os.getenv("DB_PASSWORD")
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy"
    }), 200


@app.route("/users", methods=["GET"])
def get_users():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, name FROM users ORDER BY id;"
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    users = [
        {
            "id": row[0],
            "name": row[1]
        }
        for row in rows
    ]

    return jsonify({
        "users": users
    }), 200


@app.route("/users/", methods=["GET"])
def users_with_slash():
    return redirect("/users")


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, name FROM users WHERE id = %s;",
        (user_id,)
    )

    row = cursor.fetchone()

    cursor.close()
    connection.close()

    if row is None:
        return jsonify({
            "error": "User not found"
        }), 404

    return jsonify({
        "id": row[0],
        "name": row[1]
    }), 200


@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({
            "error": "name is required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO users (name) VALUES (%s) RETURNING id, name;",
        (data["name"],)
    )

    user = cursor.fetchone()

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "id": user[0],
        "name": user[1]
    }), 201


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM users WHERE id = %s RETURNING id;",
        (user_id,)
    )

    deleted_user = cursor.fetchone()

    connection.commit()

    cursor.close()
    connection.close()

    if deleted_user is None:
        return jsonify({
            "error": "User not found"
        }), 404

    return jsonify({
        "message": "User deleted successfully"
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)