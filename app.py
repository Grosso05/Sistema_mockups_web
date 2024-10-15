from flask import Flask
from flask_login import LoginManager
from models import configure_db, test_db_connection, Users, db
import secrets
from users import users_blueprint
from routes import routes_blueprint
from logos import logos_blueprint
from customers import customers_blueprint
app = Flask(__name__)

app.config['SECRET_KEY'] = 'ef0591037a338ffa8ea682ad4c609465d2225dbd25ed598a'

login_manager = LoginManager(app)
login_manager.login_view = 'users.login'

configure_db(app)
test_db_connection(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, int(user_id))

app.register_blueprint(customers_blueprint)
app.register_blueprint(routes_blueprint)
app.register_blueprint(users_blueprint)
app.register_blueprint(logos_blueprint)
    

if __name__ == '__main__':
    app.run(debug=True) 
