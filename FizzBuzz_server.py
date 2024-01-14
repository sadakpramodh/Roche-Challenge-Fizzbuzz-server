from flask import Flask, request, jsonify, render_template
import collections
import sqlite3
import datetime
import logging

log_filename = f'logs/{datetime.datetime.now().strftime("%Y-%m-%d")}.log'

logging.basicConfig(filename=log_filename, 
                    format='%(asctime)s %(message)s',
                    filemode='a')

logger = logging.getLogger()



app = Flask(__name__)

# Datebase configuration

def get_db():
    """
    Returns a connection to the database.
    """
    path = 'databases/stats.db'
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    
    return db

def init_db():
    db = get_db()
    c = db.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS stats
        (id INTEGER PRIMARY KEY, int1 INT, int2 INT, str1 TEXT, str2 TEXT, `limit` INT, count INT DEFAULT 0)
    ''')
    db.commit()
    logger.info(f'Database initiated @ {datetime.datetime.now()}')

init_db()

stats = collections.Counter() 

def input_validation(int1, int2, str1, str2, limit):
    """
    Validates the input parameters.
    int1, int2: positive integers
    str1, str2: strings
    limit: positive integer
    Returns a dictionary containing the validated parameters.
    Raises a ValueError if any of the parameters are invalid.
    
    """
    if int1 <= 0 or int2 <= 0 or limit <= 0:
        raise ValueError("Invalid parameters, Negative numbers not accepted")
    if int1 > int2:
        int1, int2 = int2, int1
    if len(str1) == 0 or len(str2) == 0:
        raise ValueError("Invalid parameters, strings having length 0 characters")
    if len(str1) > 40 or len(str2) > 40:
        raise ValueError("Invalid parameters, strings having length 40 characters")
    if limit > 1000:
        raise ValueError("Invalid parameters, limit is morethan 1000")
    
    return {
        "int1": int1,
        "int2": int2,
        "str1": str1, 
        "str2": str2,
        "limit": limit
    }

def fizzbuzz_logic(int1, int2, str1, str2, limit):
    """
    Performs the FizzBuzz logic.
    int1, int2: positive integers
    str1, str2: strings
    limit: positive integer
    Returns a list of strings containing the FizzBuzz output.
    """
    output = list()
    for i in range(1, limit+1):
        if i % int1 == 0 and i % int2 == 0:
            output.append(str1 + str2)
        elif i % int1 == 0:
            output.append(str1)
        elif i % int2 == 0:
            output.append(str2)
        else:
            output.append(str(i))


    # store the stats to db
    db = get_db()
    c = db.cursor()
    c.execute('''
        INSERT OR IGNORE INTO stats (int1, int2, str1, str2, `limit`) 
        VALUES (?, ?, ?, ?, ?)
    ''', (int1, int2, str1, str2, limit))
    c.execute('''
        UPDATE stats 
        SET count = count + 1
        WHERE int1 = ? AND int2 = ? AND str1 = ? AND str2 = ? AND `limit` = ?
    ''', (int1, int2, str1, str2, limit))
    db.commit()
    logger.info(f'FizzBuzz request @ {datetime.datetime.now()}')
    return output

def fizzbuzz_response(list):
    """
    Returns a String response containing the FizzBuzz output.

    eg: “1,2,fizz,4,buzz,fizz,7,8,fizz,buzz,11,fizz,13,14,fizzbuzz,16,..."
    """
    string = ""
    for i in list:
        string += i+","
    return string[:-1]

@app.route('/fizzbuzz')
def fizzbuzz():
    try:
        int1 = int(request.args.get('int1'))
        int2 = int(request.args.get('int2'))
        str1 = request.args.get('str1')
        str2 = request.args.get('str2')
        limit = int(request.args.get('limit'))
    
        validated  = input_validation(int1, int2, str1, str2, limit)
        output = fizzbuzz_logic(validated['int1'],validated['int2'],validated['str1'],validated['str2'],validated['limit'])
        return fizzbuzz_response(output)
        
    except Exception as e:
        logger.error(f'Invalid parameters - {e} @ {datetime.datetime.now()}')
        return f"Invalid parameters - {e}", 400
    

@app.route('/stats')
def statistics():
    try:
        db = get_db()
        most_frequent = db.execute('SELECT * FROM stats ORDER BY count DESC LIMIT 1').fetchone() 
        logger.info(f'Most frequent requested @ {datetime.datetime.now()}')
        return jsonify({
            "int1": most_frequent["int1"],
            "int2": most_frequent["int2"],
            "str1": most_frequent["str1"],
            "str2": most_frequent["str2"],
            "limit": most_frequent["limit"],
            "count": most_frequent["count"]
        })

    except Exception as e:
        return f"Error retrieving statistics: {e}", 500
    
    
@app.route('/')
def homepage():
    try:
        return render_template('homepage.html')
    except Exception as e:
        return f"Something went wrong: {e}", 500

if __name__ == '__main__':
    app.run()
