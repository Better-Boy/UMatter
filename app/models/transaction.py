from app import mysql, build_insert_query, logger

class Transaction:

    def __init__(self, data):
        self.channel_id = data['channel_id'].strip()
        self.channel_name = data['channel_name'].strip()
        self.from_user_name = data['user_name'].strip()
        self.from_user_id = data["user_id"].strip()
        self.text = data["text"].strip()

    def execute_select_check_sum(self, query):
        logger.debug("Running query %s for checking sum total points", query)
        try:
            cursor = mysql.cursor()
            cursor.execute(query)
            return True, cursor.fetchone()["day_total"]
        except Exception as e:
            logger.exception("Exception in getting the sum total for the day for the user.")
            return False, None

    def execute_user_feed(self, query):
        logger.debug("Executing query %s", query)
        try:
            cursor = mysql.cursor()
            cursor.execute(query)
            return True, cursor.fetchall()
        except Exception as e:
            logger.exception("Exception in running query %s", query)
            return False, None

    def insert(self, data):
        logger.debug("Inserting data to mysql")
        try:
            query = build_insert_query(data)
            cursor = mysql.cursor()
            cursor.execute(query)
            # if res == 0:
            #     return False
            mysql.commit()
            return True
        except Exception as e:
            logger.exception("Exception in inserting data to the mysql server")
            return False