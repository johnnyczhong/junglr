#db helper functions

from pgdb import connect

# init connect with db
def Connect():
    try:
        connection = connect(database='junglr', host='localhost:5432', user='johnny')
    except:
        connection = False
    return connection

#used for create and update queries
#returns true if successful
def Commit(conn, query):
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
def Fetch(conn, query, amt = 1):
    row = None
    with conn.cursor() as c:
        c.execute(query)
        if type(amt) == int:
            row = c.fetchmany(amt)
        elif amt == 'all':
            row = c.fetchall()
    return row