from pymongo import *
import psycopg2 as pg2


host = 'ec2-3-233-7-12.compute-1.amazonaws.com'
database = 'd5eq8q0mlqoblu'
user_database = 'iyuckjkrlerfwj'
password = 'd6917a96198a1a2e780212478ca10d22c6bae254a694be848a9ef3e66c77bb3a'


conn = pg2.connect(host= host, database= database, user= user_database,
                   password=password)
cur = conn.cursor()

account_create = '''
        CREATE TABLE accounts (
            id SERIAL PRIMARY KEY
            ,username varchar(50) UNIQUE
            , name varchar(50) NOT NULL
            , roomnumber varchar(10) NOT NULL
            ,chat_id INTEGER NOT NULL
            , gender varchar(50)
            , preference varchar(50)
            , key varchar(50)
        );
        '''

create_links = '''
        CREATE TABLE list (
            PK SERIAL PRIMARY KEY
            ,self INTEGER references accounts(id) NOT NULL
            ,angel INTEGER
            ,mortal INTEGER
        );
        '''

cur.execute(create_links)
conn.commit()

# query1 = '''
#         CREATE TABLE modules (
#             account_id integer references accounts(id)
#             ,faculty_id integer references faculty(faculty_id)
#             ,faculty_id integer references faculties(faculty_id)
#         );
#         '''

# query1 = '''
#         SELECT faculty_id FROM faculties
#         WHERE faculty_name = 'science'
#         '''
# query1 = '''
#         SELECT faculty_name, mod_name FROM all_modules
#         INNER JOIN faculties
#         ON all_modules.faculty_id = faculties.faculty_id
#         '''


# temp_dict = {}
# for key,value in data:
#     if key.upper() not in temp_list:
#         temp_list.append(key.upper())
# print(temp_list)

# faculty = []
# for key, value in data:
#     if key.upper() not in faculty:
#         faculty.append(key.upper())
#     if key not in temp_dict:
#         temp_dict[key.upper()] = []
#     temp_dict[key.upper()] = [value]

# # print(data)
# print(temp_dict)
# print(faculty)


# conn.commit()

# MONGODB = 'mongodb+srv://yeechern123:t3y9adg2@cluster0.h45sj.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
# cluster = MongoClient(MONGODB)
# db = cluster['Eusoff-Mods']
# collection = db['accounts']
# modules_collection = db['faculties']

# def initialise_account(user):
#     with open('data.json', 'r+') as f:
#         data = json.load(f)
#         username = str(user)
#         if username not in data['accounts']:
#             data['accounts'][username] = {}
#         data['accounts'][username]['roomnumber'] = newaccount.roomnumber
#         data['accounts'][username]['faculty'] = newaccount.faculty
#         data['accounts'][username]['course'] = newaccount.course
#         data['accounts'][username]['mods'] = newaccount.mods
#         f.seek(0)
#         json.dump(data, f, indent=4)
#
#
# def initialise_modules(user):
#     username = str(user)
#     with open('data.json', 'r+') as f:
#         data = json.load(f)
#         for fac in newaccount.mods:
#             for mod in newaccount.mods[fac]:
#                 if mod not in data['Faculties'][fac]:
#                     data['Faculties'][fac][mod] = []
#                 data['Faculties'][fac][mod].append('@' + username)
#         f.seek(0)
#         json.dump(data, f, indent=4)


''''''''''''''
account_create = '''
        CREATE TABLE accounts (
            id SERIAL PRIMARY KEY
            ,username varchar(50) UNIQUE
            , name varchar(50) NOT NULL
            , roomnumber varchar(10) NOT NULL
            ,faculty varchar(50) NOT NULL
            ,course varchar(50) NOT NULL
        );
        '''

create_faculty = '''
        CREATE TABLE faculties (
            id SERIAL PRIMARY KEY
            ,faculty_name varchar(50) NOT NULL
        );
        '''

create_modules = '''
        CREATE TABLE all_modules (
            mod_id SERIAL PRIMARY KEY
            ,mod_name varchar(50) NOT NULL
            ,faculty_id integer references faculties(faculty_id) UNIQUE (mod_name)
            ,link varchar(512)
        );
        '''

insert_faculties = '''
        INSERT INTO faculties(faculty_name)
        VALUES ('science')
        );
        '''