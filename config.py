class Config:

    def __init__(self, host='localhost', user='root', password='password', db_name=None, filename=None):

        self.config = {"host": host,
                  "user": user,
                  "password": password,
                  "database": db_name}

        if filename:
            with open(filename) as f:
                for line in f:
                    kv = line.strip("\n").split("=")
                    key = [0].strip()
                    value = kv[1].strip()
                    if key in self.c.keys():
                        self.c[key] = value

    def get_settings(self):

        return self.config
