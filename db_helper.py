#db helper functions
# doesn't seem to function on c9.io. not sure why, but will resolve on c9 later.

from pgdb import connect
from config import aws_db, aws_host, aws_user, aws_pass

# init connect with db
# everything is an object!
# pipe to db; has methods to read and write.
class Connection():
    def __init__(self):
        try:
            self.connection = connect(database=aws_db, host=aws_host, user=aws_user, password=aws_pass)
        except:
            self.connection = False

    def Commit(self, query):
        committed = False    
        try:
            with self.connection.cursor() as c:
                c.execute(query)
                self.connection.commit()
                committed = True
        except:
            self.connection.rollback()
        return committed

    def Fetch(self, query, amt = 1):
        row = None
        with self.connection.cursor() as c:
            c.execute(query)
            if type(amt) == int:
                row = c.fetchmany(amt)
            elif amt == 'all':
                row = c.fetchall()
        return row

