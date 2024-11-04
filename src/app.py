from flask import Flask, render_template

app = Flask(__name__)

# app.config.from_object('config')

@app.route('/')
def index():
  return render_template('index.html')


@app.route('/login')
def login():
  return render_template('login.html')

def fib(n):
  if n < 2: return 1
  return fib(n - 1) + fib(n-2)

@app.route('/account/')
@app.route('/account/<name>')
def account(name=None):
  return render_template('account.html', person=name)