import ConfigParser
import re
import os.path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
# -------------------------------------------------
import db

class TrackedTable:

    def __init__(self, src_path):
        self.name = os.path.split(src_path)[1]
        self.src_path = src_path
        self.file = open(src_path)
        self.file.readlines()
        print 'Added Table ' + self.name

    def update(self):
        history   = self.file.readlines()
        state     = 'prepreflop'
        players   = []
        last_hand = {
            'prepreflop' : [],
            'preflop'    : [],
            'flop'       : [],
            'turn'       : [],
            'river'      : [],
            'summary'    : []}


        for line in history:
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
                last_hand[state].append(line) 


        for line in last_hand['prepreflop']:
            match = re.match('Seat \d+: ([\w.-]*)', line)
            if match:
                player = match.group(1)
                players.append(player)

        hero_hand = last_hand['preflop'].pop(0)
        for action in last_hand['preflop']:
            action = action.split()
            if len(action) == 2:
                db.add_hand(action[0], False)
            elif len(action) == 3:
                db.add_hand(action[0], True)

        # refresh_gui(players)
        print '+' + '-'*40 + '+'
        print '| ' + self.name + ' '*(39 - len(self.name)) + '|'
        print '+' + '-'*40 + '+'
        for player in players:
            stats = db.get_playerstats(player)
            try:
                print '{}: {} {} {}%'.format(player,stats[2],stats[3], 100*stats[3]/stats[2])
            except Exception:
                print 'N/A'

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path in tables:
            tables[event.src_path].update()
        else:
            tables[event.src_path] = (TrackedTable(event.src_path))
        return

if __name__ == '__main__':
    config = ConfigParser.SafeConfigParser()
    config.read('shittyhud.conf')
    hero_dir = config.get('general', 'hero_dir')

    tables = {}

    observer = Observer()
    observer.schedule(MyHandler(), "C:\Users\cyka\AppData\Roaming\PacificPoker\HandHistory\Lufftre")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
