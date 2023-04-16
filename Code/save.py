if current_round == 1: #and gameid<=2:
        symptoms = round_1_symptoms
        duration = round_1_duration
        current_round+=1
        a["GameData"][gameid].append(current_round)
        print(a)
        participant = db.session.query(Participant).filter_by(id=i_d).first()
        participant.participant_id = json.dumps(a)
        db.session.commit()

    elif current_round == 2:
        symptoms = round_2_symptoms
        duration = round_2_duration
        current_round+=1
        a["GameData"][gameid].append(current_round)
        print(a)
        participant = db.session.query(Participant).filter_by(id=i_d).first()
        participant.participant_id = json.dumps(a)
        db.session.commit()
    elif current_round == 3:
        symptoms = round_3_symptoms
        duration = round_3_duration
        current_round+=1
        a["GameData"][gameid].append(current_round)
        print(a)
        participant = db.session.query(Participant).filter_by(id=i_d).first() 
        participant.participant_id = json.dumps(a)
        db.session.commit()
    elif gameid<=2 and current_round==4:
        symptoms = round_4_symptoms
        duration = round_4_duration
        current_round+=1

    if current_round>4 and gameid !=3:
        current_round = 1
        gameid+=1
    elif gameid>2:
        partid +=1
        gameid =0
        return render_template('Questionaire.html')
    print(session["participantid"])
    data = request.form.get('submit')
    # sym= symptoms
    # print(data)
    # currData = {"current_Rd": , "symptoms": symptoms, "partID": partid, "gameid" : gameid}
    return render_template('round.html', round_num=round_num, symptoms=symptoms, duration=duration, form = form)
