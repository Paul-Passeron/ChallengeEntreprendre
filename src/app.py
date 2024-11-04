from flask import Flask, render_template, redirect, url_for

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
  if name is None:
    return redirect(url_for('login'))
  return render_template('account.html', person=name)