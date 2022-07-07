from core import views
import os
if __name__ == '__main__':
    views.app.secret_key = 'secret'
    views.app.run(host='0.0.0.0', debug=True)