from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__, static_folder='static')

# Establish MySQL connection
try:
    connection = mysql.connector.connect(
        host='localhost',
        database='book',  # Adjust the database name accordingly
        user='root',
        password='king'
    )

    if connection.is_connected():
        print('Connected to MySQL database')
except mysql.connector.Error as error:
    print("Error connecting to MySQL database:", error)

@app.route('/')
def sugg():
    return render_template('trail.html')

@app.route('/send', methods=['POST'])
def send():
    try:
        cursor = connection.cursor()
        name = request.form['username']
        email_id = request.form['email']
        suggestion = request.form['suggestion']

        # Define the MySQL query to insert data into the database
        query = "INSERT INTO suggestion (Name, email_id, suggestion) VALUES (%s, %s, %s)"

        # Execute the query with provided data
        cursor.execute(query, (name, email_id, suggestion))

        # Commit the transaction
        connection.commit()

        # Close the cursor
        cursor.close()

        # Redirect to the home page after successful submission
        return redirect('/')
    except Exception as e:
        print("Error:", e)
        return "An error occurred while processing your request."

if __name__ == '__main__':
    app.run(debug=True)
