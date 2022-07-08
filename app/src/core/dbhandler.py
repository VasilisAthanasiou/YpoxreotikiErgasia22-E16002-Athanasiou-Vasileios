from pymongo import MongoClient, errors
from bson.objectid import ObjectId

try:
    client = MongoClient('mongodb:27017', username='admin', password='admin')
except Exception as e:
    print(e)
    pass

# Use Digital Notes database
db = client["DigitalNotes"]
users = db["users"]

if not users.find_one({'email': 'admin@mail.com'}):  # Search for accounts using the same email
    users.insert_one({'email': 'admin@mail.com', 'password': 'admin', 'uname': 'admin', 'category': 'administrator'})

notes = db["notes"]
if not notes.find_one({'username': 'admin'}, {'title': 'admin-note'}):
    note_id = notes.insert_one({'username': 'admin', 'title': 'admin-note', 'date': 'none', 'content': 'This is the default note', 'keywords': ""})


