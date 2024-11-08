from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
import requests
from datetime import datetime
import re
import os

from openai import OpenAI


with open("initial_prompt.txt", "r") as f:
    initial_prompt = f.read()


API_KEY = None
with open("apikey.txt", "r") as f:
    API_KEY = f.read()

os.environ["OPENAI_API_KEY"] = API_KEY


client = OpenAI(
    organization="org-O6T7cJpsdQioHt3dHsFDUrcB",
    project="proj_EssQBcivulQjZHA3bMqxGTDf"
)


def test_email(your_pattern, email):
    pattern = re.compile(your_pattern)
    return re.match(pattern, email)


pattern = r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?"


def email_validator(email):
    return test_email(pattern, email)


app = Flask(__name__)

# Assurez-vous que cela est bien défini
app.config['UPLOAD_FOLDER'] = 'static/uploads/documents'
app.config['ORDO_FOLDER'] = 'static/uploads/ordonnances'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16 Mo
app.secret_key = 'secret_key'


@app.route('/')
def index():
    return render_template('index.html')


def getMedicalInfos():
    global current_user
    if current_user is None:
        return None
    res = f"L'utilisateur s'appelle {current_user.getPrintedName()}.\n"
    res += f"Il est actuellement {datetime.now().strftime("%Hh%M")}"
    res += "L'utilisateur a les rappels suivant pour différents médicaments:\n"
    for rappel in getRappels():
        res += "- " + rappel.getMed() + "\n"
        res += "\t" + rappel.str() + "\n"

    return res


def ask_chatgpt(question):
    global messages
    prompt = {"role": "system", "content": initial_prompt}
    med_infos_prompt = {"role": "system", "content": getMedicalInfos()}
    last_message = {"role": "user", "content": question}
    messages_bot = [prompt, med_infos_prompt]
    messages_bot += [{"role": "user" if message.isUser() else "assistant",
                      "content": message.content} for message in messages]
    messages_bot.append(last_message)
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages_bot
    )
    return completion.choices[0].message.content


def appendQuestionAndAnswer(question):
    global messages
    messages.append(Message('user', question))
    answer = ask_chatgpt(question)  # Call the ChatGPT API
    messages.append(Message('bot', answer))  # Append the API response


@app.route('/assistant', methods=['POST', 'GET'])
def assistant():
    global messages, current_user
    if len(messages) > 0:
        return redirect(url_for('discussion'))
    if current_user is None:
        return redirect(url_for('login'))
    fallback = render_template('assistant.html')
    if request.method != 'POST':
        return fallback
    data = request.get_json()
    question = data.get('question')
    appendQuestionAndAnswer(question)
    return jsonify({"message": "first"}), 400


@app.route('/modified_profile')
def modified_profile():
    return render_template('modified_profile.html')


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

    def __str__(self) -> str:
        hour = ""
        minu = ""
        if self.hour < 10:
            hour = "0"
        if self.minute < 10:
            minu = "0"
        hour += str(self.hour)
        minu += str(self.minute)
        return hour + ":" + minu


def strToHour(hour: str) -> Hour:
    hour = hour.split(":")
    return Hour(int(hour[0]), int(hour[1]))


class Rappel:
    def __init__(self, med: str, period: int, hours: list) -> None:
        self.med = med
        self.period = period
        self.hours = hours

    def getMed(self) -> str:
        return self.med

    def getPeriod(self) -> int:
        return self.period

    def getHours(self) -> list:
        return self.hours

    def nextHour(self) -> Hour:
        now = strToHour(datetime.now().strftime("%H:%M")).numeric()
        min_h = float('inf')
        res = None
        min_overall = float('inf')
        res_overall = None
        for hour in self.hours:
            num = hour.numeric()
            if min_overall > num:
                min_overall = num
                res_overall = hour
            if num > now and min_h > num:
                min_h = num
                res = hour
        if res is None:
            return res_overall
        return res

    def strInfo(self) -> str:
        return f"Médicament à prendre {len(self.hours)} fois par jour pendant {self.period} jours"

    def strHours(self) -> str:
        return f"Heures de prise du médicament : {str([x.__str__() for x in self.hours])}"

    def strNextHour(self) -> str:
        return f"Prochaine prise du médicament : {self.nextHour().__str__()}"

    def str(self) -> str:
        return self.strInfo() + "\n" + self.strHours() + "\n" + self.strNextHour()


class User:

    def __init__(self, email: str, firstname: str, name: str, password: str, carte_vitale: str) -> None:
        self.email = email
        self.firstname = firstname
        self.name = name
        self.password = password
        self.rappels = []
        self.carte_vitale = carte_vitale

    def getEmail(self) -> str:
        return self.email

    def getFirstName(self) -> str:
        return self.firstname

    def getName(self) -> str:
        return self.name

    def getPassword(self) -> str:
        return self.password

    def getCarteVitale(self) -> str:
        return self.carte_vitale

    def getPrintedName(self) -> str:
        return self.getFirstName() + " " + self.getName()

    def addRappel(self, rappel: Rappel) -> None:
        self.rappels.append(rappel)


users = [
    User("paul.passeron@ensiie.eu", "Paul", "Passeron", "123456", "225654981"),
    User("clement.leveque@ensiie.eu", "Clement", "Leveque", "0000", "654981321")
]

users[1].addRappel(
    Rappel("Doliprane", 5, [Hour(12, 50), Hour(15, 30), Hour(20, 20)]))
users[1].addRappel(
    Rappel("Ondansetron", 3, [Hour(9, 00), Hour(15, 00), Hour(21, 00)]))

current_user = users[1]


class Message():
    def __init__(self, sender: str, content: str) -> None:
        self.sender = sender
        self.content = content

    def isUser(self):
        return self.sender == "user"

    def getContent(self):
        return self.content


def valid_login(email, passwr):
    for user in users:
        if user.email == email and user.password == passwr:
            return True
    return False


messages:  list[Message] = []


def getMessages():
    return messages


def getRappels():
    if current_user is None:
        return None
    return current_user.rappels


def getEmail() -> str:
    if current_user is None:
        return None
    return current_user.getEmail()


def getName() -> str:
    if current_user is None:
        return None
    return current_user.getName()


def getFirstName() -> str:
    if current_user is None:
        return None
    return current_user.getFirstName()


def getCarteVitale() -> str:
    if current_user is None:
        return None
    return current_user.getCarteVitale()


@app.route('/login', methods=['POST', 'GET'])
def login():
    global users, current_user
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
    return redirect(url_for('index'))


@app.route('/dossier_sante', methods=['GET', 'POST'])
def dossier_sante():
    if current_user is None:
        return redirect(url_for('login'))
    if request.method == 'POST':
        if 'document' not in request.files:
            return redirect(request.url)
        file = request.files['document']
        if file.filename == '':
            return redirect(request.url)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return redirect(url_for('dossier_sante'))

    documents = os.listdir(app.config['UPLOAD_FOLDER'])
    ordonnances = os.listdir(app.config['ORDO_FOLDER'])
    return render_template('dossier_sante.html', documents=documents, ordonnances=ordonnances)


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


@app.route('/add_rappel', methods=['POST', 'GET'])
def add_rappel():
    if current_user is None:
        return redirect(url_for('login'))
    fallback = render_template('add_rappel.html')
    if request.method != 'POST':
        return fallback
    med_name = request.form['med_name']
    period = request.form['period']
    timeInputs = request.form.getlist('timeInput[]')
    if not med_name or not period or not timeInputs:
        flash('Remplissez tous les champs pour ajouter un rappel')
        return fallback
    hours = []
    for h in timeInputs:
        hour = strToHour(h)
        hours.append(hour)
    r = Rappel(med_name,  period, hours)
    addRappelToUser(r)
    return redirect(url_for('rappels'))


@app.route('/data')
def data():
    if current_user is None:
        return redirect(url_for('login'))
    return render_template('data.html')


def addRappelToUser(r: Rappel):
    for user in users:
        if user.getEmail() == current_user.getEmail():
            user.addRappel(r)


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
        return fallback
    if not is_email_availaible(mail):
        return fallback
    u = User(mail, first_name, name, pssw)
    users.append(u)
    return redirect(url_for('login'))


@app.route('/update_profile', methods=['POST'])
def update_profile():
    global users, current_user
    if current_user is None:
        return redirect(url_for('login'))

    first_name = request.form['first_name']
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    carte_vitale = request.form.get('carte_vitale', '')  # Optionnel

    if first_name != "":
        current_user.firstname = first_name
    if name != "":
        current_user.name = name
    if email != "":
        current_user.email = email
    if password != "":
        current_user.password = password
    if carte_vitale != "":
        current_user.carte_vitale = carte_vitale
    flash('Profil mis à jour avec succès !')
    return redirect(url_for('modified_profile'))


@app.route('/disconnect')
def disconnect():
    global current_user
    current_user = None
    return redirect(url_for('index'))


def chatbot(question):
    if question is None or question == "":
        return "Je suis désolé, je n'ai pas compris votre question."
    return "Hello, World"


@app.route('/discussion', methods=['GET', 'POST'])
def discussion():
    fallback = render_template('discussion.html')
    if current_user is None:
        return redirect(url_for('login'))
    if len(messages) == 0:
        return redirect(url_for('assistant'))
    if request.method != 'POST':
        return fallback
    data = request.get_json()
    question = data.get('question')
    appendQuestionAndAnswer(question)
    return jsonify({"message": "discussion"}), 400


def getPrintedName():
    if current_user is None:
        return None
    return current_user.getPrintedName().upper()


def is_connected():
    return not (current_user is None)


@app.context_processor
def inject_context():
    return dict(is_connected=is_connected, getPrintedName=getPrintedName, getName=getName, getRappels=getRappels, getFirstName=getFirstName, getEmail=getEmail, getCarteVitale=getCarteVitale, getMessages=getMessages)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
