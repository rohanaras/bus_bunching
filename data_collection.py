def get_json(suffix):
    import urllib, json
    url_object = urllib.urlopen('http://api.pugetsound.onebusaway.org/api/where/' + suffix)
    return json.loads(url_object.read())


def test_sql(cnx):
    from datetime import datetime, date
    cursor = cnx.cursor()
    test_insert = ("INSERT INTO test (word, number, date) "
                   "VALUES (%(word_entry)s, %(number_entry)s, %(date_entry)s)")
    test_data = {
        'word_entry': 'TestData',
        'number_entry': 17,
        'date_entry': datetime.now().date()
    }
    cursor.execute(test_insert, test_data)
    cnx.commit()


def apiRequest():
    print('dummy')


def inputData():
    """
    currently puts data in a localhost db
    """
    import mysql.connector

    config = {
        'user': 'testUser',
        'password': 'anything',
        'host': '127.0.0.1',
        'database': 'TestOBA'
    }

    try:
        cnx = mysql.connector.connect(**config)
        test_sql(cnx)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cnx.close()


if __name__ == "__main__":
    inputData()
