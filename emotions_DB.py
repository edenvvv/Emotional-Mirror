import sqlite3
from emotion_class import Emotion
from datetime import datetime
import datetime as DateTime


def create_if_not_exists():
    """
    Create database table (if not exist)
    """
    conn = sqlite3.connect('emotions.db')
    curs = conn.cursor()
    curs.execute("""CREATE TABLE IF NOT EXISTS emotions (
                emotionID INTEGER,
                emotion text,
                date text,
                time text
                )""")
    conn.close()


def insert_emotion(emo):
    """
    insert emotion to the database
    @param emo: Emotion object
    """
    conn = sqlite3.connect('emotions.db')
    curs = conn.cursor()
    create_if_not_exists()
    with conn:
        curs.execute("INSERT INTO emotions VALUES (:emotionID, :emotion, :date, :time)",
                     {'emotionID': emo.emotionID, 'emotion': emo.emotion, 'date': emo.date, 'time': emo.time})
    conn.close()


def get_emo_by_id(emo_id):
    """
    get emotion by id
    @param emo_id: ID of The emotion
    @return: All values where the emotionID field is the same as emo_id
    """
    conn = sqlite3.connect('emotions.db')
    curs = conn.cursor()
    curs.execute("SELECT * FROM emotions WHERE emotionID=:emotionID", {'emotionID': emo_id})
    return curs.fetchall()


def get_emo_by_date(date):
    """
    get emotion by date
    @param date: date of The emotion
    @return: All values where the date field is the same as the given date
    """
    conn = sqlite3.connect('emotions.db')
    curs = conn.cursor()
    curs.execute("SELECT * FROM emotions WHERE date=:date", {'date': date})
    return curs.fetchall()


def get_most_recently_emo(date):
    """
    get the most recently emotion
    @param date: date of The emotion
    @return: the most recently emotion
    """
    conn = sqlite3.connect('emotions.db')
    curs = conn.cursor()
    create_if_not_exists()
    curs.execute("SELECT emotion FROM emotions WHERE date=:date ORDER BY time DESC ", {'date': date})
    re_val = curs.fetchone()
    conn.close()
    if re_val:
        return re_val[0]
    else:
        return None


def analyser(date):
    """
    get all the emotion IDs emotions from the last days
    @param date: date of The emotion
    @return: all emotions from the last days
    """
    conn = sqlite3.connect('emotions.db')
    curs = conn.cursor()
    curs.execute("SELECT emotionID,date FROM emotions WHERE date-2<=:date ", {'date': date})
    return curs.fetchall()


def report_analyser(date):
    """
    get all the emotions from the last days
    @param date: date of The emotion
    @return: all emotions from the last days
    """
    conn = sqlite3.connect('emotions.db')
    curs = conn.cursor()
    curs.execute("SELECT emotion,date FROM emotions WHERE date-2<=:date ", {'date': date})
    return curs.fetchall()


def remove_emo(emo):
    """
    Delete the given emotion
    @param emo: Emotion object
    """
    conn = sqlite3.connect('emotions.db')
    curs = conn.cursor()
    with conn:
        curs.execute("DELETE from emotions WHERE emotionID = :emotionID AND "
                     "emotion = :emotion AND date = :date AND time = :time",
                     {'emotionID': emo.emotionID, 'emotion': emo.emotion, 'date': emo.date, 'time': emo.time})
    conn.close()


def db_unpack():
    """
    Unpack the data from the last days to individual days
    @return: the individual days
    """
    date_time = datetime.now()
    date = date_time.date()
    data = analyser(date)
    date = DateTime.date.today()

    today = list(filter(lambda record: record[1] == str(date), data))
    yesterday = list(filter(lambda record: record[1] == str(date - DateTime.timedelta(days=1)), data))
    day_before_yesterday = list(filter(lambda record: record[1] == str(date - DateTime.timedelta(days=2)), data))

    return today, yesterday, day_before_yesterday


def depression_analyser():
    """
    Analyse the last days to detect depression (based on sadness)
    @return: True if detect characteristics that can be interpreted as depressive, False otherwise
    """
    today, yesterday, day_before_yesterday = db_unpack()

    today_sadness = list(filter(lambda record: record[0] == 3, today))
    yesterday_sadness = list(filter(lambda record: record[0] == 3, yesterday))
    day_before_yesterday_sadness = list(filter(lambda record: record[0] == 3, day_before_yesterday))

    if len(day_before_yesterday) == 0 or len(yesterday) == 0 or len(today) == 0:
        return None  # not enough data

    relative_day_before_yesterday = len(day_before_yesterday_sadness) / len(day_before_yesterday)
    if relative_day_before_yesterday >= 0.25:
        relative_yesterday = len(yesterday_sadness) / len(yesterday)
        if relative_yesterday >= (relative_day_before_yesterday+0.01) or relative_yesterday >= 0.95:
            relative_today = len(today_sadness) / len(today)
            if relative_today >= (relative_yesterday+0.01) or relative_today >= 0.95:
                return True
            return False
        return False
    return False


def manic_depression_analyser():
    """
    Analyse the last days to detect manic depression (based on sadness and happy, when sadness > happy)
    @return: True if detect characteristics that can be interpreted as manic depression, False otherwise
    """
    today, yesterday, day_before_yesterday = db_unpack()

    today_sadness = list(filter(lambda record: record[0] == 3, today))
    yesterday_sadness = list(filter(lambda record: record[0] == 3, yesterday))
    day_before_yesterday_sadness = list(filter(lambda record: record[0] == 3, day_before_yesterday))

    today_happiness = list(filter(lambda record: record[0] == 1, today))
    yesterday_happiness = list(filter(lambda record: record[0] == 1, yesterday))
    day_before_yesterday_happiness = list(filter(lambda record: record[0] == 1, day_before_yesterday))

    if len(day_before_yesterday) == 0 or len(yesterday) == 0 or len(today) == 0:
        return None  # not enough data

    relative_day_before_yesterday = (len(day_before_yesterday_sadness) + len(day_before_yesterday_happiness)) / len(day_before_yesterday)
    if (relative_day_before_yesterday >= 0.5) and (len(day_before_yesterday_sadness) > len(day_before_yesterday_happiness)):
        relative_yesterday = (len(yesterday_sadness) + len(yesterday_happiness)) / len(yesterday)
        if (relative_yesterday >= relative_day_before_yesterday) and (len(yesterday_sadness) > len(yesterday_happiness)):
            relative_today = (len(today_sadness) + len(today_happiness)) / len(today)
            if (relative_today >= relative_yesterday) and (len(today_sadness) > len(today_happiness)):
                return True
            return False
        return False
    return False


def anxiety_analyser():
    """
    Analyse the last days to detect anxiety (based on surpriseness)
    @return: True if detect characteristics that can be interpreted as anxiety, False otherwise
    """
    today, yesterday, day_before_yesterday = db_unpack()

    today_surpriseness = list(filter(lambda record: record[0] == 4, today))
    yesterday_surpriseness = list(filter(lambda record: record[0] == 4, yesterday))
    day_before_yesterday_surpriseness = list(filter(lambda record: record[0] == 4, day_before_yesterday))

    if len(day_before_yesterday) == 0 or len(yesterday) == 0 or len(today) == 0:
        return None  # not enough data

    relative_day_before_yesterday = len(day_before_yesterday_surpriseness) / len(day_before_yesterday)
    if relative_day_before_yesterday >= 0.2:
        relative_yesterday = len(yesterday_surpriseness) / len(yesterday)
        if relative_yesterday >= (relative_day_before_yesterday+0.01) or relative_yesterday >= 0.9:
            relative_today = len(today_surpriseness) / len(today)
            if relative_today >= (relative_yesterday+0.01) or relative_today >= 0.9:
                return True
            return False
        return False
    return False


def emotion_report():
    """
    Find the emotion with the max predictions in each of the last days
    @return: most frequent emotion in each of the last days
    """
    date_time = datetime.now()
    date = date_time.date()
    data = report_analyser(date)
    date = DateTime.date.today()

    today = list(filter(lambda record: record[1] == str(date), data))
    yesterday = list(filter(lambda record: record[1] == str(date - DateTime.timedelta(days=1)), data))
    day_before_yesterday = list(filter(lambda record: record[1] == str(date - DateTime.timedelta(days=2)), data))

    today = list(map(lambda record: record[0], today))
    yesterday = list(map(lambda record: record[0], yesterday))
    day_before_yesterday = list(map(lambda record: record[0], day_before_yesterday))

    if today:
        today_report = max(set(today), key=today.count)  # find most frequent element
    else:
        today_report = None
    if yesterday:
        yesterday_report = max(set(yesterday), key=yesterday.count)
    else:
        yesterday_report = None
    if day_before_yesterday:
        day_before_yesterday_report = max(set(day_before_yesterday), key=day_before_yesterday.count)
    else:
        day_before_yesterday_report = None

    return today_report, yesterday_report, day_before_yesterday_report


# Demo:
"""
conn = sqlite3.connect('emotions.db')
curs = conn.cursor()

emo_1 = Emotion('1', '15:30')
emo_2 = Emotion('2', '04:23')

insert_emotion(emo_1)
insert_emotion(emo_2)

emps = get_emo_by_id('sad')
emps += get_emo_by_id('happy')
print(emps)

remove_emo(emo_1)
emps = get_emo_by_id('sad')
emps += get_emo_by_id('happy')
print(emps)

conn.close()
"""
