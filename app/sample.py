from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
import json
import redis

# App
application = Flask(__name__)

# connect to MongoDB
mongoClient = MongoClient('mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] +
                          '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_AUTHDB'])
db = mongoClient[os.environ['MONGODB_DATABASE']]

# connect to Redis
redisClient = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=os.environ.get(
    "REDIS_PORT", 6379), db=os.environ.get("REDIS_DB", 0))

# connect to game collection in mongo db
collection_game = db.game

@application.route('/')
def index():
    body = '<h1>MongoDB Exercise - Array</h1>'
    body += '<h2>Alphabet Guessing Game v1.0</h2>'
    body += '<button> <a href="/Start/">Start</a></button>'
    game = collection_game.find_one()
    if game == None:
        mydict = {
            "question": ["_","_","_","_"], 
            "char_remain": ["*","*","*","*"], 
            "answer": [], 
            "index": 0, 
            "point": 100,
            "count": 0
            }
        collection_game.insert_one(mydict)
    return body

@application.route('/Start/')
def start():
    body = '<h2>Welcome to my Guessing Game</h2>'
    game = collection_game.find_one()
    if game != None:
        body = '<h1>Make a question!</h1>'
        body += '<br></br>'
        question_text = ' '.join(game['question'])
        body += 'Question :' + question_text
        body += '<br></br>'
        body += '<a href="/A/"><button>A</button></a>'
        body += '<a href="/B/"><button>B</button></a>'
        body += '<a href="/C/"><button>C</button></a>'
        body += '<a href="/D/"><button>D</button></a>'
        if game['index'] == 4:
            body = '<h1>Make a question!</h1>'
            body += 'Question created!'
            body += '<br></br>'
            body += '<a href="/play/"><button> Press to go</button></a>'
            return body
    return body

@application.route('/A/')
def A():
    game = collection_game.find_one()
    if game['index'] < 4:
        make_question(game, 'A')
        return start()
    if game['index'] >= 4:
        insert_answer(game, 'A')
        return play()

@application.route('/B/')
def B():
    game = collection_game.find_one()
    if game['index'] < 4:
        make_question(game, 'B')
        return start()
    if game['index'] >= 4:
        insert_answer(game, 'B')
        return play()

@application.route('/C/')
def C():
    game = collection_game.find_one()
    if game['index'] < 4:
        make_question(game, 'C')
        return start()
    if game['index'] >= 4:
        insert_answer(game, 'C')
        return play()

@application.route('/D/')
def D():
    game = collection_game.find_one()
    if game['index'] < 4:
        make_question(game, 'D')
        return start()
    if game['index'] >= 4:
        insert_answer(game, 'D')
        return play()


def make_question(game,alphabet):
    index_now = game["index"]
    collection_game.update_one({}, {"$set": {"question." + str(index_now) : alphabet}})
    index_now += 1
    collection_game.update_one({}, {"$set": {"index" : index_now}})

def insert_answer(game,alphabet):
    index_now = game["index"]
    current_count = game["count"]
    current_count += 1
    if game['question'][index_now - 4] == alphabet:
        collection_game.update_one({}, {"$set": {"answer." + str(index_now - 4) : alphabet}})
        index_now += 1
        collection_game.update_one({}, {"$set": {"index" : index_now}})
        collection_game.update_one({}, { "$set": { 'char_remain.' + str(index_now - 4): "" }})
    collection_game.update_one({}, {"$set": {"count": current_count}})

def point_game(game):
    point = game["point"]
    current_count = game["count"]
    point = point - ((current_count-4)*5)
    if point < 0:
        point = 0
        collection_game.update_one({"point": 100}, {"$set": {"point" : point}})
        return point
    else:
        collection_game.update_one({"point": 100}, {"$set": {"point" : point}})
        return point

@application.route('/play/')
def play():
    collection_game = db.game
    game = collection_game.find_one()
    if game['question'] == game['answer']:
        return gameover()
    ans_text = ' '.join(game['answer'])
    char_remain_text = ' '.join(game['char_remain'])
    body = '<h2>Alphabet Guessing Game V.1.0</h2>'
    body += "Please Choose Question to guess."
    body += '<br> <br> '
    body += 'Answer: ' + ans_text
    body += '<br>'
    body += 'Characters remaining: ' + char_remain_text
    body += '<br> <br>'
    body += 'Choose:  <a href="/A"><button> A </button></a>' 
    body += '<a href="/B"><button> B </button></a>'
    body += '<a href="/C"><button> C </button></a>'
    body += '<a href="/D"><button> D </button></a>'
    body += '<br> <br>'
    body += 'Your trying: ' + str(game["count"] )+ ' times'
    return body

@application.route('/gameover')
def gameover():
    collection_game = db.game
    game = collection_game.find_one()
    body = '<h2>Congratulations! </h2>'
    body += '<br> <br> '
    body += '<b>Your points: </b>' + str(point_game(game))
    body += '<br> <br> '
    body += '<b>Trying count: </b>' + str(game['count'])
    body += '<br> <br>'
    body += '<a href="/again"><button> Try again </button></a>'
    return body

@application.route('/again')
def again():
    collection_game = db.game
    mydict = {
        "question": ["-","-","-","-"], 
        "char_remain": ["*","*","*","*"], 
        "answer": [], 
        "index": 0,
        "point": 100,
        "count":0, 
    }
    collection_game.update_one({}, {"$set": mydict})
    return index()

if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("FLASK_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("FLASK_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)