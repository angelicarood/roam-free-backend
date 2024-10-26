from flask import Flask, request, jsonify
from psycopg2 import connect, sql
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
from flask_cors import CORS

# Load environment variables
load_dotenv()


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Connect to PostgreSQL database
def get_db_connection():
    conn = connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    email = data.get('email')
    print("Received POST request with email:", email)  # Debug print

    if not email:
        return jsonify({"message": "Email is required"}), 400

    try:
        # Insert subscriber into the database
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        insert_query = sql.SQL("INSERT INTO subscribers (email) VALUES (%s) RETURNING *")
        cursor.execute(insert_query, (email,))
        new_subscriber = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        print("Successfully inserted:", new_subscriber)  # Debug print

        return jsonify({
            "message": "Subscription successful!",
            "subscriber": new_subscriber
        }), 201

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debug print
        if 'unique constraint' in str(e).lower():
            return jsonify({"message": "Email already subscribed"}), 400
        return jsonify({"message": "An error occurred", "error": str(e)}), 500


# Test route to confirm POST requests work
@app.route('/api/test', methods=['POST'])
def test_post():
    return jsonify({"message": "POST request successful!"}), 200

@app.route('/ping', methods=['GET'])
def ping():
    print("Ping route hit!")  # Add this line
    return jsonify({"message": "pong"}), 200



# Run the server
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5010, debug=True)


