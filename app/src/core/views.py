from flask import Flask, render_template, redirect, url_for, request, session
from .dbhandler import users
from bson.objectid import ObjectId
import re

app = Flask(__name__, template_folder='../templates')

# -------------------------------------------------- Sign Up View ---------------------------------------------------------------------------- #


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    error = None
    if request.method == 'POST':
        res, error = create_user()
        if res:
            return redirect(url_for('home'))

    return render_template('signup.html', error=error)

# -------------------------------------------------------------------------------------------------------------------------------------------- #

# -------------------------------------------------- Login View ------------------------------------------------------------------------------ #


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = users.find_one({'email': '{}'.format(request.form['email']), 'password': '{}'.format(request.form['password'])},
                              {"_id": 1, "name": 1, "category": 1})  # Find user matching input fields
        if user:  # If a user was found
            # Extract data using regex
            session['username'] = re.search("'name':\s'(\w+)'", str(user)).group(1)
            session['uid'] = re.search("'_id':\sObjectId\('(.+)'\)", str(user)).group(1)
            session['user_category'] = re.search("'category':\s'(.+)'", str(user)).group(1)
            return redirect(url_for('home'))
        else:
            error = 'Invalid Credentials'

    return render_template('login.html', error=error)

# -------------------------------------------------------------------------------------------------------------------------------------------- #

# -------------------------------------------------- Logout View ----------------------------------------------------------------------------- #


@app.route('/logout')
def logout():
    if session['username'] is not None:  # Check if user is logged in
        # Set all session fields to None
        session['username'] = None
        session['uid'] = None
        session['user_category'] = None
    return redirect(url_for('home'))

# -------------------------------------------------------------------------------------------------------------------------------------------- #

# -------------------------------------------------- Admin Page View ------------------------------------------------------------------------- #


@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    error = None
    if session['user_category'] == 'administrator':  # Make sure that only an admin account can access this page
        return render_template('admin-page.html')
    else:
        return redirect(url_for('home'))

# -------------------------------------------------------------------------------------------------------------------------------------------- #

# -------------------------------------------------- User Home View -------------------------------------------------------------------------- #


@app.route('/', methods=['GET', 'POST'])
def home():
    text_results = None
    error = None
    history_len = 0

    # try:
    #     history = users.find({'_id': ObjectId(session['uid'])}, {'movies_seen'})
    #     history = list(history)
    #     history = re.search('movies.{8}\[(.+)]}]', str(history))
    #     if history:
    #         history = history.group(1).split(',')
    #         history_len = len(history)
    # except KeyError:
    #     session['uid'] = None
    #     history = None

    # if request.method == 'GET':
    #     # Get search query from search bar
    #     query = request.args.get('search')
    #     # Execute query
    #     if query:
    #         try:
    #             if session['username']:
    #                 session['screening_datetimes'] = ''
    #                 text_results, error = searchMovie(query)
    #                 if not error:
    #                     return redirect(url_for('movie'))
    #             else:
    #                 error = 'You need to log in first to use this feature!'
    #         except KeyError:
    #             session['username'] = None
    #             error = 'You need to log in first to use this feature!'

    return render_template('home.html', text_results=text_results, error=error)

# -------------------------------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------ Other methods ----------------------------------------------------------------------------------- #


def create_user(category='user'):
    error = None
    are_filled = request.form['email'] and request.form['name'] and request.form['password']
    if are_filled:
        if not users.find_one({'email': '{}'.format(request.form['email'])}):  # Search for accounts using the same email
            # Insert the new user to the database
            users.insert_one({'email': '{}'.format(request.form['email']), 'password': '{}'.format(request.form['password']),
                          'name': '{}'.format(request.form['name']), 'category': category})
            return True, None
        error = 'An account with this email already exists.'
    else:
        error = 'Please fill out all the fields'
    return False, error

# ---------------------------------------------------------------------------------------------------------------------------------------------- #




