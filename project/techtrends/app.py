import sqlite3

from flask import Flask, render_template, request, url_for, redirect, flash
import logging
import sys 
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    # session["db_connection_count"] = session["db_connection_count"] + 1

    f = open("db_connection_count.txt", "r")
    db_connection_count = int(float(f.read()))
    f.close()

    f = open("db_connection_count.txt", "w")
    db_connection_count = db_connection_count  + 1
    f.write(str(db_connection_count))
    f.close()

    return connection

def log(x): 
    stdout_fileno = sys.stdout
    now = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    stdout_fileno.write('INFO:app:' + str(now) +', ' + str(x) + ' \n')

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def healthy():
    app.logger.info('health-check')
    return "result: OK - healthy", 200

@app.route('/metrics')
def metrics():

    log('Getting post counter')
    connection = get_db_connection()
    postCounter = connection.execute('SELECT COUNT(id) FROM posts').fetchone()
    connection.close()
    log('Finish post counter')

    log('Getting connection counter')
    connectionCounter = get_db_connection()
    log('Finish connection counter')

    return {"db_connection_count": connectionCounter, "post_count": postCounter[0]}, 200

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
