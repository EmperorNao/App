import pymysql


class Database:

    def __init__(self, config):

        self.config = config.get_settings()
        self.connection = pymysql.connect(host=self.config["host"],
                                     user=self.config["user"],
                                     password=self.config["password"],
                                     db=self.config["database"],
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

    def get_connection(self):

        return self.connection

    def select_all(self, table_name):

        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * from %s" % (table_name))
            result = cursor.fetchall()

        return result

    def execute(self, query, args=None):

        with self.connection.cursor() as cursor:
            cursor.execute(query, args)
            result = cursor.fetchall()
            self.connection.commit()

        return result
