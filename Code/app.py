from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import time, json, random
import pandas as pd
from forms import submitform


app = Flask(__name__)

##secret config key for login safety
app.config['SECRET_KEY'] = '83c97881e8dd561fe803894acdf47605'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SESSION_TYPE'] = 'sqlalchemy'


db = SQLAlchemy(app)
app.config['SESSION_SQLALCHEMY'] = db

sess = Session(app)

#Getting Session Id
def getUniqueID():
    ip_address = request.remote_addr
    timestamp = (int(time.time() * 10000)) #int(time.time())
    user_id = f"{ip_address}-{timestamp}"
    return user_id


def get_participants():
    # Query the database for all Participant objects and extract the participant_id field
    json_list = [participant.participant_id for participant in Participant.query.all()]
    participant_ids = [str(json.loads(json_string)['uniqueID']).split(': ')[-1] for json_string in json_list]

    # Return the participant_ids list as a JSON object
    return participant_ids
with app.app_context():
    db.create_all()

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # participant_id = db.Column(db.Integer)
    participant_id = db.Column(db.String(80))
    # s =db.Column(db.String(500))
    def __repr__(self):
        return f"Participant('{self.id}', '{self.participant_id}')"

with app.app_context():
    db.create_all()

#Storing session data
app.permanent_session_lifetime = timedelta(days=5)
 

df = pd.read_csv('Lab Study Games-Copy1.csv')


# Define the countdown duration for each round
round_1_duration = 180
round_2_duration = 180
round_3_duration = 180
round_4_duration = 180

# Define a global variable to keep track of the current round
with app.app_context():
    latest_participant = Participant.query.order_by(Participant.id.desc()).first()
    if latest_participant is not None:
        i_d = latest_participant.id
    else:
        i_d = 0
current_round = 1
partid = 0
gameid = 0
sym = ''
session_id = 3

a = {
  "uniqueID": session_id,
  "GameData": [[],[],[]]
}

@app.route('/')
def index():
    # Redirect to the first round
    global partid, i_d, a, gameid, current_round
    session_id = getUniqueID()
    a["uniqueID"] = session_id
    part = Participant.query.filter_by(id=i_d).first()
    print("1. Checkid and part_id", partid, i_d)
    if part:
        if (a["uniqueID"] not in get_participants()):
            gameid =0 
            current_round=1
            a["GameData"]= [[],[],[]]
            partid +=1
            i_d+=1
            print("2. Id Incremented", i_d)
            participant = Participant(id = i_d, participant_id=json.dumps(a))
            db.session.add(participant)
            db.session.commit()
            print("3. DB COMITTED")
            return redirect(url_for('home'))

    # participant = Participant(id = 0, participant_id=partid)
    participant = Participant(id = 0, participant_id=json.dumps(a))
    print(participant)
    db.session.add(participant)
    db.session.commit()
    print("First participant comitted")
    return redirect(url_for('round', round_num=1))

@app.route("/Questionaire")
def Questionaire():
    return render_template('Questionaire.html')

def gameidchange():
    global current_round, gameid, partid
    if current_round>4 and gameid !=2:
        current_round = 1
        gameid+=1
    elif gameid>2:
        partid +=1
        gameid =0
        
def update_rd(round_num, symptoms, duration, form):
    global current_round, a
    a["GameData"][gameid].append(current_round)
    # current_round+=1
    print(a)
    participant = db.session.query(Participant).filter_by(id=i_d).first() 
    participant.participant_id = json.dumps(a)
    db.session.commit() 
    current_round+=1
    gameidchange()

@app.route('/round/<int:round_num>', methods=['GET', 'POST'])
def round(round_num):
    '''
    '''
    form = submitform()
    global current_round, partid, gameid, a, i_d
    # Session data 
    session.permanent = True
    session["participantid"] = partid
    # print(gameid)
    # Define the symptoms for each round
    # mask = (df["Participant ID"] == (session["participantid"]+3))

    
    mask = (df["Participant ID"] == i_d) & (df["Game ID"] == gameid) 
    round_1_symptoms = df.loc[mask, "Round 1"]
    round_2_symptoms = df.loc[mask, "Round 1"]
    round_3_symptoms = df.loc[mask, "Round 2"]
    round_4_symptoms = df.loc[mask, "Round 3"]
    # print(session["participantid"])
    
    round_num = current_round

    print(current_round, round_num)
    # Check if the requested round number is valid
    # if round_num < 1 or round_num > 4:
    #     return redirect(url_for('index'))

    # Check if the current round is valid
    # if round_num != current_round:
    #     return redirect(url_for('round', round_num=current_round))

    # Get the symptoms and countdown duration for the current round
    if current_round == 1 and gameid<=2:
        symptoms = round_1_symptoms
        duration = round_1_duration
        update_rd(round_num, symptoms, duration, form)

    elif current_round == 2:
        symptoms = round_2_symptoms
        duration = round_2_duration
        update_rd(round_num, symptoms, duration, form)
    elif current_round == 3:
        symptoms = round_3_symptoms
        duration = round_3_duration
        update_rd(round_num, symptoms, duration, form)
    elif gameid<=2 and current_round==4:
        symptoms = round_4_symptoms
        duration = round_4_duration
        # current_round+=1
        update_rd(round_num, symptoms, duration, form)

    # if current_round>4 and gameid !=3:
    #     current_round = 1
    #     gameid+=1
    # elif gameid>2:
    #     partid +=1
    #     gameid =0
    #     return render_template('Questionaire.html')

    print(session["participantid"])
    data = request.form.get('submit')
    if gameid == 2 and round_num == 5:
        gameidchange()
        return render_template('Questionaire.html')
    else:
        return render_template('round.html', round_num=round_num, symptoms=symptoms, duration=duration, form = form)

@app.route('/data')
def get_data():
    currData = {"current_Rd": current_round, "symptoms": sym, "partID": partid, "gameid" : gameid}
    return jsonify(currData)
@app.route("/home")
def home():
    return render_template('home.html')

# @app.route("/Questionaire")
# def Questionaire():
#     return render_template('Questionaire.html')


if __name__ == '__main__':
    app.run(debug=True,  host='0.0.0.0')
