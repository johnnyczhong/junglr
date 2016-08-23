#db helper functions
# doesn't seem to function on c9.io. not sure why, but will resolve on c9 later.

from pgdb import connect
from config import aws_db, aws_host, aws_user, aws_pass

# init connect with db
def Connect():
    try:
        connection = connect(database=aws_db, host=aws_host, user=aws_user, password=aws_pass)
    except:
        connection = False
    return connection

#used for create and update queries
#returns true if successful
def Commit(query, conn):
    committed = False    
    try:
        with conn.cursor() as c:
            c.execute(query)
            conn.commit()
            committed = True
    except:
        conn.rollback()
    return committed

#used for select queries
#returns row if successful, None if not
def Fetch(query, conn, amt = 1):
    row = None
    with conn.cursor() as c:
        c.execute(query)
        if type(amt) == int:
            row = c.fetchmany(amt)
        elif amt == 'all':
            row = c.fetchall()
    return row
