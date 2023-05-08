#Importing the packages
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import time, json, random
import pandas as pd
from forms import submitform

# Defining the Flask App
app = Flask(__name__)

##secret config key for login safety
app.config['SECRET_KEY'] = '83c97881e8dd561fe803894acdf47605'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SESSION_TYPE'] = 'sqlalchemy'

#Instaniating the Database
db = SQLAlchemy(app)
app.config['SESSION_SQLALCHEMY'] = db

#This is an attempt to store data within session
sess = Session(app)

#Getting Session Id
def getUniqueID():
    '''This functions stores data of the current tab with 
    the timstamp so that every time a new tab is opened, the game starts itself up'''
    ip_address = request.remote_addr
    timestamp = (int(time.time() * 10000)) #int(time.time())
    user_id = f"{ip_address}-{timestamp}"
    return user_id


def get_participants():
    '''This is just to extract the ParticipantID'''
    # Query the database for all Participant objects and extract the participant_id field
    json_list = [participant.participant_id for participant in Participant.query.all()]
    participant_ids = [str(json.loads(json_string)['uniqueID']).split(': ')[-1] for json_string in json_list]

    # Return the participant_ids list as a JSON object
    return participant_ids
with app.app_context():
    db.create_all()

class Participant(db.Model):
    '''This is the database schema containing two columns
    id: Unique ID for everypartcipant (Same as the ParticipantId FROM the CSV)
    ParticipantID (String): Large string containing the timestamp of when a participant opned a new tab with 
                            updated game and roundID they are currently in 
                            Example== {"uniqueID": "127.0.0.1-16816895163045", 
                            "GameData": [[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]]}
                            where each list for a unique GameID'''
    id = db.Column(db.Integer, primary_key=True)
    # participant_id = db.Column(db.Integer)
    participant_id = db.Column(db.String(80))
    def __repr__(self):
        return f"Participant('{self.id}', '{self.participant_id}')"

with app.app_context():
    db.create_all()

#Storing session data
app.permanent_session_lifetime = timedelta(days=5)
 
#Importing the CSVs from the local stroage
df = pd.read_csv('Lab Study Games-Copy2.csv')
df_guess = pd.read_csv('Guess.csv')


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

## Define all the global variable to keep track of the current round, gameid and guesses
current_round = 1
partid = 0
gameid = 0
sym = ''
session_id = 3
guess = []
gametracker =0

#Dictionary that basically gets added in to the database to the column PartcipantID
participant_data = {
  "uniqueID": session_id,
  "GameData": []
}

#Index Route
@app.route('/')
def index():
    # Redirect to the first round
    global partid, i_d, participant_data, gameid, current_round
    session_id = getUniqueID()
    participant_data["uniqueID"] = session_id
    #Checks if id already present in the data
    part = Participant.query.filter_by(id=i_d).first()
    print("1. Checkid and part_id", partid, i_d)
    if part:
        #If Id is present then commit to database
        if (participant_data["uniqueID"] not in get_participants()):
            gameid =0 
            current_round=1
            participant_data["GameData"]= []
            partid +=1
            i_d+=1
            print("2. Id Incremented", i_d)
            participant = Participant(id = i_d, participant_id=json.dumps(participant_data))
            db.session.add(participant)
            db.session.commit()
            print("3. DB COMITTED")
            return redirect(url_for('home'))

    #Commit for the first ID
    participant = Participant(id = 0, participant_id=json.dumps(participant_data))
    print(participant)
    db.session.add(participant)
    db.session.commit()
    print("First participant comitted")
    return redirect(url_for('round', round_num=1))

#Route for final page
@app.route("/Questionaire")
def Questionaire():
    return render_template('Questionaire.html')


def gameidchange():
    '''If all the rounds of a game have finished, updates gameID
    Else: makes gameID= 0'''
    global current_round, gameid, partid
    if current_round>4 and gameid !=2:
        current_round = 1
        gameid+=1
    elif gameid>2:
        partid +=1
        gameid =0
        
def update_rd():
    '''this currently just commits the new data, i.e., the round and thhe game in 
    which the participant is in into the database'''
    global current_round, participant_data, guess
    # participant_data["GameData"][gameid].append(current_round)
    participant_data["GameData"].append(str(gameid)+'|'+str(current_round))
    participant = db.session.query(Participant).filter_by(id=i_d).first() 
    participant.participant_id = json.dumps(participant_data)
    db.session.commit() 
    current_round+=1
    gameidchange()

#This is triggered everytime a person presses submit in the Round
@app.route("/getData", methods=["POST"])
def GetData():
    '''This function contains the main piece of code for storing te data provided as 
    guesses within the ROUNDS by the Participant in the dataset
    DB_GUESS'''
    global guess, df_guess, gameid, gametracker, current_round, participant_data
    guess.append(request.form['Guess_1'])
    guess.append(request.form['Guess_2'])
    guess.append(request.form['Guess_3'])

    #Concats all the 3 guesses for a round together
    value = str(current_round)+":"+request.form['Guess_1']+';'+request.form['Guess_2']+';'+request.form['Guess_3']
    part = Participant.query.filter_by(id=i_d).first()
    print("1. Checkid and part_id", partid, i_d)
    if part:
         if (participant_data["uniqueID"] in get_participants()):
            gameid_and_currentrds = json.loads(part.participant_id)['GameData']
            if len(gameid_and_currentrds)>=1:
                gameid = int(gameid_and_currentrds[len(gameid_and_currentrds)-1].split('|')[0])
                current_round= int(gameid_and_currentrds[len(gameid_and_currentrds)-1].split('|')[1])
                if (gameid<3 and current_round<4):
                    current_round+=1
                elif (gameid<2 and current_round==4):
                    gameid+=1
                    current_round=1
                elif (gameid ==2 and current_round==4):
                    gameid=0
                    current_round=1
                    return render_template('Questionaire.html')               

    if i_d in list(df_guess['Participant ID'].values) and gametracker == gameid:
        # If it does contain id, update the existing row with the current round's guess
        row_index = df_guess.loc[(df_guess['Participant ID'] == i_d) & (df_guess['Game ID'] == gameid)].index[0]
        #Storing the guess
        df_guess.at[row_index, f'Round {current_round} Guess'] = (
           value
        )
        
        print('show', type(df_guess['Participant ID'].values))
    else:
        # If it doesn't, create a new row with the participant ID and round 1 guess
        gametracker = gameid
        new_row = {'Participant ID': i_d, 'Game ID': gametracker, f'Round {current_round} Guess': value}
        #Guess storing
        df_guess = df_guess.append(new_row, ignore_index=True)
    update_rd()
    return redirect(url_for('round', round_num=current_round))

##################################################
#Important
#This is the dataframe that stores the guesses
#Please run this code when you need to store it into a csv
# df_guess.to_csv('myguess.csv', index=False)
##################################################

@app.route('/round/<int:round_num>', methods=['GET', 'POST'])
def round(round_num):
    '''This route, round contains the crux of the logic
        First, the id from the database is matched wit the participant ID to pick up the
        symptoms for a particular participant using masking in line 205, ensuring a new game
        wit new symptoms is always picked. 
        Then based on the round, symtoms are passed on to be represented into the website. 
    '''
    form = submitform()
    global current_round, partid, gameid, participant_data, i_d, df_guess

    # Attempt to save session Data
    session.permanent = True
    session["participantid"] = partid

    #The masking of the dataframe to only pick data for a specific Participant and Game ID
    mask = (df["Participant ID"] == i_d) & (df["Game ID"] == gameid) 
    round_1_symptoms = df.loc[mask, "Round 1"]
    round_2_symptoms = df.loc[mask, "Round 1"]
    round_3_symptoms = df.loc[mask, "Round 2"]
    round_4_symptoms = df.loc[mask, "Round 3"]
    game_tool = df.loc[mask, "Website Choice"].values[0]
    
    #Round_num is the round number that goes to te html template
    round_num = current_round

    # Get the symptoms and countdown duration for the current round
    if current_round == 1 and gameid<=2:
        symptoms = round_1_symptoms
        duration = round_1_duration
        game = game_tool
        # update_rd()
        
    elif current_round == 2:
        symptoms = round_2_symptoms
        duration = round_2_duration
        game = game_tool
        # update_rd()

    elif current_round == 3:
        symptoms = round_3_symptoms
        duration = round_3_duration
        game = game_tool
        # update_rd()

    elif gameid<=2 and current_round==4:
        symptoms = round_4_symptoms
        duration = round_4_duration
        game = game_tool

    #Changes the gameID when gameID and round_num out of bounds and returns the final page
    if gameid == 2 and round_num == 5:
        gameidchange()
        return render_template('Questionaire.html')
    else:
        return render_template('round.html', round_num=round_num, symptoms=symptoms, duration=duration, form = form, game= game)

@app.route('/data')
def get_data():
    currData = {"current_Rd": current_round, "symptoms": sym, "partID": partid, "gameid" : gameid}
    return jsonify(currData)
@app.route("/home")
def home():
    return render_template('home.html')



if __name__ == '__main__':
    app.run(debug=True)  #host='0.0.0.0')
