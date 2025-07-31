from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import hashlib
app = Flask(__name__)
# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'keerthi@888'
app.config['MYSQL_DB'] = 'medical'
mysql = MySQL(app)
# Helper function to hash passwords
# def hash_password(password):
# return hashlib.sha256(password.encode()).hexdigest()
# Route to register a user
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    confirm_password=data.get('confirm_password)')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    # hashed_password = hash_password(password)
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("INSERT INTO users (name, email, password,confirm_password) VALUES (%s, %s, %s.%s)", (username, email, password,confirm_password))
        mysql.connection.commit()
        return jsonify({'message': 'User registered successfully', 'status' : '200'}), 201
    except MySQLdb.IntegrityError:
        return jsonify({'error': 'Username already exists',  'status' : '401'}), 409
    finally:
        cursor.close()
# Route to login a user
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE name = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return jsonify({'status':200, 'message': 'Login successful', 'user': {'id': user['uid'], 'username': user['name']}})
    else:
        return jsonify({'error': 'Invalid username or password'}), 401
@app.route('/edit_profile/<int:uid>', methods=['GET'])
def edit_profile(uid):
    data = request.get_json()
    new_name = data.get('name')
    new_email = data.get('email')
    new_password = data.get('password')
    if not new_name and not new_email and not new_password:
        return jsonify({'error': 'No fields provided for update'}), 400
    cursor = mysql.connection.cursor()
    try:
        update_fields = []
        values = []
        if new_name:
            update_fields.append("name = %s")
            values.append(new_name)
        if new_email:
            update_fields.append("email = %s")
            values.append(new_email)
        if new_password:
            update_fields.append("password = %s")
            values.append(new_password)

        values.append(uid)

        query = f"UPDATE users SET {', '.join(update_fields)} WHERE uid = %s"
        cursor.execute(query, values)
        mysql.connection.commit()

        # Optional: show updated user info
        cursor.execute("SELECT uid, name, email FROM users WHERE uid = %s", (uid,))
        updated_user = cursor.fetchone()
        print(updated_user[0])
        return jsonify({
            'message': 'Profile updated successfully',
            'updated_user': {
                'uid': updated_user[0],
                'name': updated_user[1],
                'email': updated_user[2]
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
@app.route('/delete_profile/<int:uid>', methods=['DELETE'])
def delete_profile(uid):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE uid = %s", (uid,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_data = {
            'uid': user[0],
            'name': user[1],
            'email': user[2],
            'password': user[3]
        }

        cursor.execute("DELETE FROM users WHERE uid = %s", (uid,))
        mysql.connection.commit()

        return jsonify({
            'message': 'User deleted successfully',
            'deleted_user': user_data
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
