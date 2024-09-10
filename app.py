from flask import Flask, render_template, request,redirect
import mysql.connector
import numpy as np
import joblib 
import pymysql
import pandas as pd
import pickle

popular_df = joblib.load(open('popular.pkl', 'rb'))
pt = joblib.load(open('pt.pkl', 'rb'))
books = joblib.load(open('books.pkl', 'rb'))
similarity_scores = joblib.load(open('similarity_scores.pkl', 'rb'))
df = pd.read_csv("BooksDataset\\books_data.csv")
df['Title']=df['Title'].str.upper()
titles=df['Title']
titles=list(titles)
app = Flask(__name__, static_folder='static')

# Establishing Database Connection
try:
    connection = mysql.connector.connect(
        host='localhost',
        database='book',
        user='root',
        password='king'
    )

    if connection.is_connected():
        print('Connected to MySQL database')
except mysql.connector.Error as error:
    print("Error connecting to MySQL database:", error)

# Function to check if user already exists
def user_exists(username, email):
    cursor = connection.cursor()
    query = "SELECT * FROM login WHERE username = %s OR email_id = %s"
    cursor.execute(query, (username, email))
    result = cursor.fetchone()
    cursor.close()  # Closing cursor
    return result is not None

# Function to check if login credentials are valid
def login_exist(username, password):
    cursor = connection.cursor()
    query = "SELECT * FROM login WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    cursor.close()  # Closing cursor
    return result is not None

@app.route('/')
def register():
    return render_template('register.html')

@app.route('/submit', methods=['POST'])
def submit():
    username = request.form['username']
    email_id = request.form['email']
    password = request.form['password']
 
    if user_exists(username, email_id):
        return '''
        <script>
            alert('User already exists! Registration failed.');
            window.location.href = '/';
        </script>
        '''
    else:
        cursor = connection.cursor()
        query = "INSERT INTO login(username, email_id, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, email_id, password))
        connection.commit()
        cursor.close()  # Closing cursor
        return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if login_exist(username, password):
            return render_template('index.html',
                               book_name = list(popular_df['Book-Title'].values),
                               author=list(popular_df['Book-Author'].values),
                               image=list(popular_df['Image-URL-M'].values),
                               votes=list(popular_df['num_rating'].values),
                               rating=list(popular_df['avg_rating'].values)
                           )

        else:
            return '''
            <script>
                alert('User Not Found! Login failed.');
                window.location.href = '/login';
            </script>
            '''
    else:
        return render_template('login.html')

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/search_result', methods=['POST'])
def search_result():
    book_name = request.form.get('user_input')
    book_name=book_name.upper() 
    if book_name not in titles:
        # If no matching books found, display an alert message
        return '''
            <script>
                    alert('Book Not Found!.');
                    window.location.href = '/search';
                </script>
                '''
    else:
            # Convert the result to a dictionary
        filtered_df = df[df['Title'] == book_name]
        book_details = filtered_df.iloc[0].to_dict()
        return render_template('search_result.html', book_details=book_details)

@app.route('/sugg')
def sugg():
    return render_template('sugg.html')

@app.route('/send', methods=['POST'])
def send():
    try:
        cursor = connection.cursor()
        name = request.form['username']
        email_id = request.form['email']
        suggestion = request.form['suggestion']

        # Define the MySQL query to insert data into the database
        query = "INSERT INTO suggestion(Name, email_id, suggestion) VALUES (%s, %s, %s)"

        # Execute the query with provided data
        cursor.execute(query, (name, email_id, suggestion))

        # Commit the transaction
        connection.commit()

        # Close the cursor and MySQL connection
        cursor.close()
        connection.close()

        # Render a JavaScript response to display a popup message
        return '''
        <script>
            alert('Thanks for your suggestion, ''' + name + '''!');
            window.location.href = '/sugg';
        </script>
        '''
    except Exception as e:
        print("Error:", e)
        return "An error occurred while processing your request."


@app.route('/recommend_books', methods=['POST'])
def recommend():
    try:
        user_input = request.form.get('user_input')
        user_input=user_input
        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

            data.append(item)

        print(data)

        return render_template('recommend.html', data=data)

    except Exception as e:
        return '''
            <script>
                alert('Book Not Found!.');
                window.location.href = '/recommend';
            </script>
            '''


if __name__ == '__main__':
    app.run(debug=True)
