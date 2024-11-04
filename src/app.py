from flask import Flask, render_template, redirect, url_for, request, g

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

class User:
  
  def __init__(self, email, firstname, name, password):
    self.email = email
    self.firstname = firstname
    self.name = name
    self.password = password
    
  def getEmail(self):
    return self.email
  
  def getFirstName(self):
    return self.firstname
  
  def getName(self):
    return self.name
  
  def getPassword(self):
    return self.password
  
  def getPrintedName(self):
    return self.getFirstName() + " " + self.getName()
    
    


paulp = User("paul.passeron@ensiie.eu", "Paul", "Passeron", "123456")
clement = User("clement.leveque@ensiie.eu", "Clement", "Leveque", "0000")

users = [paulp, clement]

def valid_login(email, passwr):
  for user in users:
    if user.email == email and user.password == passwr:
      return True
  return False
  
current_user = None


@app.route('/login', methods=['POST', 'GET'])
def login():
  global current_user
  fallback = render_template('login.html')
  if request.method != 'POST':
    return fallback
  email = request.form['email']
  psw = request.form['password']
  couldCounnect = valid_login(email, psw)
  if not couldCounnect:
    return fallback
  current_user = None
  for u in users:
    if u.getEmail() == email:
      current_user = u
  return redirect(url_for('account'))
  

@app.route('/dossier_sante')
def mds():
  return render_template('dossier_sante.html')

@app.route('/account')
def account():
  if current_user is None:
    return redirect(url_for('login'))
  return render_template('account.html', person=current_user.getPrintedName())


@app.route('/signup', methods=['POST', 'GET'])
def signup():
  fallback = render_template('signup.html')
  if request.method != 'POST':
    return fallback
  mail = request.form("email")
  # TODO
  
    
def getName():
  if current_user is None: return None
  return current_user.getPrintedName()


def is_connected():
  return not (current_user is None)

@app.context_processor
def inject_context():
  return dict(is_connected=is_connected, getName=getName)