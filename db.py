import sqlite3

def db_open():
    dbh = sqlite3.connect('shitty.db')
    dbh.text_factory = str
    return dbh

def create_table():
    with db_open() as dbh:
        dbh.execute('CREATE TABLE IF NOT EXISTS players('
                                'ID INTEGER PRIMARY KEY,'
                                'NAME CHAR(64) UNIQUE,'
                                'HANDS INT,'
                                'LIMP INT,'
                                'PFRAISE INT)')
        dbh.commit()

def add_hand(name, action=0):
    with db_open() as dbh:
        if action == 1:
            limp, pfraise = 1,0
        elif action == 2:
            limp, pfraise = 0,1
        else:
            limp, pfraise = 0,0

        cursor = dbh.cursor()
        cursor.execute('SELECT * FROM players WHERE(NAME=?)', [name])
        result = cursor.fetchone()
        if result:
            dbh.execute('UPDATE players SET HANDS=?, LIMP=?, PFRAISE=? WHERE (NAME=?)',
                [result[2]+1, result[3]+limp, result[4]+pfraise, name])
        else:
            dbh.execute('INSERT INTO players VALUES(NULL,?,1,?,?)',[name,limp,pfraise])
        dbh.commit()

def get_playerstats(name):
    with db_open() as dbh:
        cursor = dbh.cursor()
        cursor.execute('SELECT * FROM players WHERE(NAME=?)', [name])
        result = cursor.fetchone()
    return result

def list_table():
    '''
    Returns a list containing the tables records
    '''
    with db_open() as dbh:
        cursor = dbh.cursor()
        cursor.execute('SELECT * FROM players')
        result = cursor.fetchall()
    print result
