import psycopg2 as pg2
import csv

host = os.environ['host']
database = os.environ['database']
user_database = os.environ['username']
password = os.environ['password']

with open('file.csv', newline='') as f:
    reader = csv.reader(f)
    data = list(reader)


class AngelMortal():
    def __init__(self, username, angel):
        self.username = username
        self.angel = angel
        self.mortal = None


AngelMortalDict = {}
usernameToIdDict = {}


def createDict():
    for line in data:
        username = line[0]
        angel = line[1]
        newAngelMortal = AngelMortal(username, angel)
        if newAngelMortal not in AngelMortalDict:
            AngelMortalDict[username] = newAngelMortal

    print(AngelMortalDict)


def pairMortal():
    for key, value in AngelMortalDict.items():
        mortal = key
        account = value
        angel = account.angel
        account_2 = AngelMortalDict[angel]
        account_2.mortal = mortal


def getFromDatabase():  # get the id and username after registration on the bot
    conn = pg2.connect(host=host, database=database,
                       user=user_database,
                       password=password)
    cur = conn.cursor()
    select_id_username = '''
                SELECT id,username FROM accounts
                '''
    cur.execute(select_id_username)
    data = cur.fetchall()
    for key, value in data:
        usernameToIdDict[value] = key


def insertIntoDatabase():
    conn = pg2.connect(host=host, database=database,
                       user=user_database,
                       password=password)
    cur = conn.cursor()
    for username, data in AngelMortalDict.items():
        try:
            # print('inserting')
            username = usernameToIdDict[username]
            # print(username)
            angel = usernameToIdDict[data.angel]
            # print(angel)
            mortal = usernameToIdDict[data.mortal]
            # print(mortal)
            
            updateDatabase = '''
            UPDATE list
            SET angel = %s
                ,mortal = %s
                WHERE self = %s
            '''
            cur.execute(updateDatabase, (angel, mortal, username))
            # print('inserted')
        except:
            continue
    conn.commit()
    print('completed')


getFromDatabase()
createDict()
pairMortal()
insertIntoDatabase()

''''''

'''SELECT n.username AS self, a.username AS angel, m.username AS mortal FROM list AS l, accounts AS a, accounts AS m, accounts AS n
WHERE l.self = n.id AND l.angel = a.id AND l.mortal = m.id'''
