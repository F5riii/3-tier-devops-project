from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)


def get_db_connection():
    connection = psycopg2.connect(
        host="localhost",
        database="devops_app",
        user="devops_user",
        password="devops_password"
    )

    return connection


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy"
    })


@app.route("/users", methods=["GET"])
def users():

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, name FROM users ORDER BY id;"
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    users_list = []

    for row in rows:
        users_list.append({
            "id": row[0],
            "name": row[1]
        })

    return jsonify({
        "users": users_list
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)