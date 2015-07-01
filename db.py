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
                                'VIP INT)')
        dbh.commit()

def add_hand(name,vip=False):
    with db_open() as dbh:
        cursor = dbh.cursor()
        cursor.execute('SELECT * FROM players WHERE(NAME=?)', [name])
        result = cursor.fetchone()
        if result:
            dbh.execute('UPDATE players SET HANDS=?, VIP=? WHERE (NAME=?)', [result[2]+1, result[3]+vip, name])
        else:
            dbh.execute('INSERT INTO players VALUES(NULL,?,1,?)',[name,int(vip)])
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
