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

    def Execute_Query(self, query, amt = 1):
        self.query = query
        query_result = False
        fetch_type = ['select']
        commit_type = ['insert', 'update', 'delete']
        query_type = (self.query.strip().split())[0].lower()
        if query_type in fetch_type:
            query_result = self.Fetch(amt)
        elif query_type in commit_type:
            query_result = self.Commit()
        return query_result

    def Commit(self):
        committed = False    
        try:
            with self.connection.cursor() as c:
                c.execute(self.query)
                self.connection.commit()
                committed = True
        except:
            self.connection.rollback()
        return committed

    def Fetch(self, amt):
        row = None
        with self.connection.cursor() as c:
            c.execute(self.query)
            if type(amt) == int:
                row = c.fetchmany(amt)
            elif amt == 'all':
                row = c.fetchall()
        return row


class Query():
    def __init__(self, keyword, table, where = {}, subject = {}, limit = 1):
        self.keyword = keyword
        self.table = table
        self.where = where
        self.subject = subject
        self.limit = limit
        self.statement = self.build_statement()

    def build_statement(self):
        #statement = ''
        if self.keyword == 'insert':
            statement = self.build_insert()
        elif self.keyword == 'update':
            statement = self.build_update()
        elif self.keyword == 'delete':
            statement = self.build_delete()
        elif self.keyword == 'select':
            statement = self.build_read()
        return statement

    #construct where clause, joined by 'and'. used by delete, update, and read
    def where_clause(self):
        clause_list = []
        for k, v in self.where.items():
            clause_list.append('{0} = {1}'.format(k, repr(v)))
        clause = ' and '.join(clause_list)
        return clause

    #construct clause = {[column], [value]}. used by insert
    def insert_clause(self):
        cols, values = [], []
        clause_dict = {}
        for k, v in self.subject.items():
            cols.append(k), values.append(repr(v))
        clause_dict['cols'] = ','.join(cols)
        clause_dict['values'] = ','.join(values)
        return clause_dict

    #construct set clause, joined by ','. used by update.
    def set_clause(self):
        clause_list = []
        for k, v in self.subject.items():
            clause_list.append('{0} = {1}'.format(k, repr(v)))
        clause = ', '.join(clause_list)
        return clause

    def build_update(self):
        statement = 'update {} set '.format(self.table)
        statement += self.set_clause()
        statement += ' where '
        statement += self.where_clause()
        return statement + ';'

    def build_delete(self):
        statement = 'delete from {} where '.format(self.table)
        statement += self.where_clause()
        print(statement)
        return statement + ';'

    def build_insert(self):
        statement = 'insert into {} '.format(self.table)
        clause_dict = self.insert_clause()
        statement += '({0}) values ({1})'.format(clause_dict['cols'], clause_dict['values'])
        return statement + ';'

    def build_read(self):
        cols = self.subject if self.subject != {} else '*'
        statement = 'select {0} from {1} where '.format(cols, self.table)
        statement += self.where_clause()
        return statement + ';'












