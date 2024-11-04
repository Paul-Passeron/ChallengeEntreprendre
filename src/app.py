from flask import Flask, render_template, redirect, url_for, request, g

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

users = [
  ("paul.passeron", "Python123"),
  ("clement.leveque", "DataScIIEnce123" )
]


def valid_login(user, passwr):
  for (l, p) in users:
    if user == l and passwr == p:
      return True
  return False
  
current_username = None




@app.route('/login', methods=['POST', 'GET'])
def login():
  global current_username
  fallback = render_template('login.html')
  if request.method != 'POST':
    return fallback
  usr = request.form['username']
  psw = request.form['password']
  couldCounnect = valid_login(usr, psw)
  if not couldCounnect:
    return fallback
  current_username = usr
  return redirect(url_for('account'))
  

@app.route('/dossier_sante')
def mds():
  return render_template('dossier_sante.html')

@app.route('/account/')
def account():
  if current_username is None:
    return redirect(url_for('login'))
  return render_template('account.html', person=current_username)

def is_connected():
  return not (current_username is None)

@app.context_processor
def inject_is_connected():
  return dict(is_connected=is_connected)