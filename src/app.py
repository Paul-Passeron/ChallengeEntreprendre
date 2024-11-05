from flask import Flask, render_template, redirect, url_for, request, g
import sys
from datetime import datetime
import re

def test_email(your_pattern, email):
  pattern = re.compile(your_pattern)
  return re.match(pattern, email)

pattern = r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?" 

def email_validator(email):
  return test_email(pattern, email)

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/assistant')
def assistant():
  return render_template('assistant.html')    
    

class Hour:
  def __init__(self, hour: int, minute: int) -> None:
    self.hour = hour
    self.minute = minute
  
  def getHour(self) -> int:
    return self.hour
  
  def getMinute(self) -> int:
    return self.minute
  
  def numeric(self) -> int:
    return self.minute + (self.hour*60)

def strToHour(hour: str) -> Hour:
  hour = hour.split(":")
  return Hour(int(hour[0]), int(hour[1]))

class Rappel:
  def __init__(self, times_a_day: int, med: str, period: int, hours: list) -> None:
    self.times_a_day = times_a_day
    self.med = med
    self.period = period
    self.hours = hours
  
  def getTimeADay(self) -> str:
    return self.times_a_day
  
  def getMed(self) -> str:
    return self.med
  
  def getPeriod(self) -> int:
    return self.period
  
  def getHours(self) -> list:
    return self.hours
  
  def nextHour(self) -> Hour:
    if self.hours == []:
      return None
    else:
      now = strToHour(datetime.now().strftime("%H:%M")).numeric()
      sorted_hours = self.hours.sort(key=lambda x: x.numeric())
      for hour in sorted_hours:
        if hour.numeric() > now:
          return hour
      return None
  
  def __str__(self) -> str:
    return f"Rappel: {self.med} à prendre tous les {self.freq}"

class User:
  
  def __init__(self, email, firstname, name, password) -> None:
    self.email = email
    self.firstname = firstname
    self.name = name
    self.password = password
    self.rappels = []
    
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
  
  def addRappel(self, rappel: Rappel) -> None:
    self.rappels.append(rappel)

users = [
  User("paul.passeron@ensiie.eu", "Paul", "Passeron", "123456"),
  User("clement.leveque@ensiie.eu", "Clement", "Leveque", "0000")
]

users[1].addRappel(Rappel("5 jours", "doliprane"))

def valid_login(email, passwr):
  for user in users:
    if user.email == email and user.password == passwr:
      return True
  return False
  
current_user = None

def getRappels():
  if current_user is None:
    return None
  return current_user.rappels

@app.route('/login', methods=['POST', 'GET'])
def login():
  global users, current_user
  for user in users:
    print("Mail is ", user.getEmail())
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
  if current_user is None:
    return redirect(url_for('login'))
  return render_template('dossier_sante.html')

@app.route('/account')
def account():
  if current_user is None:
    return redirect(url_for('login'))
  return render_template('account.html')

@app.route('/rappels')
def rappels():
  if current_user is None:
    return redirect(url_for('login'))
  return render_template('rappels.html')


def is_email_valid(email):
  return email_validator(email)
  

def is_email_availaible(email):
  for user in users:
    if user.getEmail() == email:
      return False
  return True

  
@app.route('/signup', methods=['POST', 'GET'])
def signup():
  global users, current_user
  fallback = render_template("signup.html")
  if request.method != 'POST':
    return fallback
  name = request.form["name"]
  first_name = request.form["first_name"]
  mail = request.form["email"]
  pssw = request.form["password"]
  conf_pssw = request.form["confirm_password"]
  if pssw != conf_pssw:
    return fallback
  if not is_email_valid(mail):
    print("INVALID EMAIL")
    return fallback
  if not is_email_availaible(mail):
    print("UNAVAILABLE EMAIL")
    return fallback
  u = User(mail, first_name, name, pssw)
  users.append(u)
  return redirect(url_for('login'))
  
  
@app.route('/disconnect')
def disconnect():
  global current_user
  current_user = None
  return redirect(url_for('index'))

    
def getName():
  if current_user is None: return None
  return current_user.getPrintedName()


def is_connected():
  return not (current_user is None)

@app.context_processor
def inject_context():
  return dict(is_connected=is_connected, getName=getName, getRappels=getRappels)


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)