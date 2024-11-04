from flask import Flask, render_template, redirect, url_for, request

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
  


@app.route('/login', methods=['POST', 'GET'])
def login():
  fallback = render_template('login.html')
  if request.method != 'POST':
    return fallback
  usr = request.form['username']
  psw = request.form['password']
  couldCounnect = valid_login(usr, psw)
  if not couldCounnect:
    return fallback
  return render_template('account.html', person=usr)
  


@app.route('/account/')
@app.route('/account/<name>')
def account(name=None):
  if name is None:
    return redirect(url_for('login'))
  return render_template('account.html', person=name)