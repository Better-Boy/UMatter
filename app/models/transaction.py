from app import mysql, build_insert_query

class Transaction:

    def __init__(self, data):
        self.channel_id = data['channel_id'].strip()
        self.channel_name = data['channel_name'].strip()
        self.from_user_name = data['user_name'].strip()
        self.from_user_id = data["user_id"].strip()
        self.text = data["text"].strip()

    def execute_select_check_sum(self, query):
        cursor = mysql.cursor()
        cursor.execute(query)
        return cursor.fetchone()["day_total"]

    def execute_user_feed(self, query):
        cursor = mysql.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def insert(self, data):
        query = build_insert_query(data)
        cursor = mysql.cursor()
        res = cursor.execute(query)
        if res == 0:
            return False
        mysql.commit()
        return True

    def select(self, query):
        pass