from pymongo import MongoClient, errors

try:
    client = MongoClient('mongodb:27017', username='admin', password='admin')
except Exception as e:
    print(e)
    pass

# Use Digital Notes database
db = client.DigitalNotes
users = db.users
if not users.find_one({'email': 'admin@mail.com'}):  # Search for accounts using the same email
    users.insert_one({'email': 'admin@mail.com', 'password': 'admin', 'name': 'admin', 'category': 'administrator'})
