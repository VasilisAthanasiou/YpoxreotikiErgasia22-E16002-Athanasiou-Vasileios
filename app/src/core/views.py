from flask import Flask, render_template, redirect, url_for, request, session
from .dbhandler import users, notes
from _datetime import datetime
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
                              {"_id": 1, "uname": 1, "category": 1})  # Find user matching input fields
        if user:  # If a user was found
            # Extract data using regex
            session['username'] = re.search("'uname':\s'(\w+)'", str(user)).group(1)
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

# -------------------------------------------------- Create Admin View ----------------------------------------------------------------------- #


@app.route('/create-admin', methods=['GET', 'POST'])
def create_admin():
    error = None
    if session['user_category'] == 'administrator':
        if request.method == 'POST':
            res, error = create_user('administrator')
            if res:
                return redirect(url_for('home'))

    return render_template('create-admin.html', error=error)

# -------------------------------------------------------------------------------------------------------------------------------------------- #

# -------------------------------------------------- Note View ------------------------------------------------------------------------------ #


@app.route('/note', methods=['GET', 'POST'])
def note():
    if session['username']:
        if not session['note_title'] is None:
            error = None
            return render_template('note.html', error=error)
        else:
            return redirect(url_for('home'))
    else:
        error = 'You must be logged in to use this feature'
        return render_template('home.html', error=error)

# -------------------------------------------------------------------------------------------------------------------------------------------- #


# -------------------------------------------------- Create Note View ----------------------------------------------------------------------- #

@app.route('/create-note', methods=['GET', 'POST'])
def create_note():
    error = None
    if session['username']:
        if request.method == 'POST':
            title = '{}'.format(request.form['title'])
            date = '{}'.format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            content = '{}'.format(request.form['content'])
            keywords = '{}'.format(request.form['keywords'])

            are_filled = title != '' and content != '' and keywords != ''

            if are_filled:
                print("Will try to create note")
                if not notes.find_one({'username': session['username'], 'title': title}):  # Search if note already exists
                    print("Note of same title and username wasn't found")
                    if request.form['submit_button'] == 'Create':  # Check if the user clicked the Insert button
                        notes.insert_one({'username': session['username'], 'title': title, 'date': date, 'content': content, 'keywords': keywords})  # Add note into database
                    return redirect(url_for('home'))
                else:
                    error = 'Note with the same title already exists for this user.'
            else:
                error = 'Please fill all fields'
        return render_template('create-note.html', error=error)

    return redirect(url_for('home'))


# -------------------------------------------------------------------------------------------------------------------------------------------- #


# -------------------------------------------------- User Home View -------------------------------------------------------------------------- #


@app.route('/', methods=['GET', 'POST'])
def home():
    text_results = None
    error = None

    if request.method == 'GET':
        # Get search query from search bar
        query = request.args.get('search')
        option = request.args.get('search-option')
        # Execute query
        if query:
            try:
                if session['username']:
                    text_results, error = search_note(query, option)
                    if not error:
                        return redirect(url_for('note'))
                else:
                    error = 'You need to log in first to use this feature!'
            except KeyError:
                session['username'] = None
                error = 'You need to log in first to use this feature!'

    return render_template('home.html', text_results=text_results, error=error)

# -------------------------------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------ Other methods ----------------------------------------------------------------------------------- #


def create_user(category='user'):
    error = None
    are_filled = request.form['email'] and request.form['uname'] and request.form['fullname'] and request.form['password']
    if are_filled:
        if not users.find_one({'email': '{}'.format(request.form['email'])}):  # Search for accounts using the same email or username
            if not users.find_one({'uname': '{}'.format(request.form['uname'])}):
                # Insert the new user to the database
                users.insert_one({'email': '{}'.format(request.form['email']), 'password': '{}'.format(request.form['password']),
                              'uname': '{}'.format(request.form['uname']), 'fullname': '{}'.format(request.form['fullname']), 'category': category})
                return True, None
            return False, 'An account with the same username already exists.'
        return False, 'An account with the same email already exists.'
    else:
        error = 'Please fill out all the fields'
    return False, error


def search_note(query, option):
    """
    Takes in a query and performs mongodb's text search on it.
    :param query: Query provided by the user
    :param option : Decides whether to search for a title or a keyword
    :return:
    """
    error = None
    if option == "keyword":  # Check if keyword search is enabled
        text_results = notes.find({"keywords": {"$elemMatch": query}})
        print(text_results)
    else:  # Search using title
        text_results = notes.find_one({'$and': [{'username': session['username']}, {'title': query}]})
        if text_results is None:
            error = 'No note matching your search criteria was found.'
            session['note_id'] = None
            session['note_title'] = None
            session['note_date'] = None
            session['note_content'] = None
            session['note_keywords'] = ''
            return None, error

        session['note_id'] = re.search("'_id':\sObjectId\('(.+)'\)", str(text_results)).group(1)
        session['note_title'] = re.search("['\"]title['\"]:\s['\"](.+)['\"],\s'date'", str(text_results)).group(1)
        session['note_date'] = re.search("['\"]date['\"]:\s['\"](.+)['\"],\s['\"]content['\"]", str(text_results)).group(1)
        session['note_content'] = re.search("['\"]content['\"]:\s['\"](.+)',\s'keywords", str(text_results)).group(1)
        session['note_keywords'] = re.search("['\"]keywords['\"]:\s['\"](.+)'", str(text_results)).group(1)
    return text_results, error

# ---------------------------------------------------------------------------------------------------------------------------------------------- #




