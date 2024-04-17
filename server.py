import socket
from urllib.parse import unquote_plus
import psycopg2

# Function to handle user registration
def register(username, password):
    try:
        conn = psycopg2.connect(
            dbname="lms",
            user="postgres",
            password="dheerajpostgres",
            host="localhost"
        )
        cur = conn.cursor()

        # Check if the username already exists
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            return False
        else:
            # Insert new user into the database
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            return True
    except psycopg2.Error as e:
        print("Error while connecting to PostgreSQL:", e)
        return False
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()

# Function to handle user login
def login(username, password):
    try:
        conn = psycopg2.connect(
            dbname="expense_tracker",
            user="postgres",
            password="dheerajpostgres",
            host="localhost"
        )
        cur = conn.cursor()

        # Check if the user exists in the database
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()

        if user:
            return True, "Login successful"
        else:
            return False, "Invalid username or password"
    except psycopg2.Error as e:
        print("Error while connecting to PostgreSQL:", e)
        return False, "Error logging in"
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()

# Other functions...

# Initialize the server
host = "127.0.0.1"
port = 2003
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(5)

print(f"Server is listening on http://{host}:{port}")

# Main server loop
while True:
    client_socket, client_addr = server_socket.accept()

    # Receive data from the client
    request = client_socket.recv(1024).decode()

    # Get the first line of the request
    first_line = request.split('\r\n')[0]

    # Split the first line into method and path
    if first_line:
        try:
            method, path = first_line.split()[:2]
        except ValueError:
            # If there are not enough values to unpack, close the connection and continue to the next iteration
            client_socket.close()
            continue
    else:
        # If the first line is empty, close the connection and continue to the next iteration
        client_socket.close()
        continue

    # Extracting parameters from the request
    params = {}
    if method == 'POST':
        params = dict(x.split('=') for x in request.split('\r\n')[-1].split('&'))

    # Route handling
    if method == 'GET' and path == '/':
        # Redirect to index.html
        response = b"HTTP/1.1 302 Found\r\nLocation: /index.html\r\n\r\n"
        client_socket.send(response)

    elif method == 'GET' and path == '/index.html':
        # Serve the index page HTML file
        with open('index.html', 'rb') as file:
            content = file.read()
            response = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + content
            client_socket.send(response)

    elif method == 'POST' and path == '/register':
        # Perform user registration
        if 'username' in params and 'password' in params:
            email = unquote_plus(params['username'])
            password = unquote_plus(params['password'])
            if register(email, password):
                response = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body>Registration successful</body></html>\r\n"
            else:
                response = b"HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/html\r\n\r\n<html><body>Registration failed</body></html>\r\n"
        else:
            response = b"HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n\r\n<html><body>Missing email or password</body></html>\r\n"
        client_socket.send(response)

    # Other route handling...

    # Close the client socket
    client_socket.close()
