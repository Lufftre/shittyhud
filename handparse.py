import re
import db

def parse_hand(hand):
    state     = 'prepreflop'
    hand_dict = {
        'prepreflop' : [],
        'preflop'    : [],
        'flop'       : [],
        'turn'       : [],
        'river'      : [],
        'summary'    : []}

    for line in hand:
        line = line.strip()
        if '** Dealing down cards **' in line:
            state = 'preflop'
        elif '** Dealing flop **' in line:
            state = 'flop'
        elif '** Dealing turn **' in line:
            state = 'turn'
        elif '** Dealing river **' in line:
            state = 'river'
        elif '** Summary **' in line:
            state = 'summary'
        else:
            hand_dict[state].append(line) 

    players = [None]*10
    for line in hand_dict['prepreflop']:
        match = re.match('Seat (\d+): ([\w.-]*)', line)
        if match:
            seat   = int(match.group(1))
            player = match.group(2)
            players[seat-1] = player

    try:
        hero_hand = hand_dict['preflop'].pop(0)
    except:
        hero_hand = None
    for action in hand_dict['preflop']:
        action = action.split()
        if len(action) == 2:
            db.add_hand(action[0], False)
        elif len(action) == 3:
            if action[1] == 'calls':
                db.add_hand(action)
            db.add_hand(action[0], True)
    return players