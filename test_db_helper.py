#test_db_helper

import db_helper

create = "insert into player_data values (2, 'test2', 2);"
read = "select * from player_data where summ_id = 2;"
update = "update player_data set summ_name = 'test3', revision_date = 3 where summ_id = 2;"
delete = "delete from player_data where summ_id = 2;"

conn = db_helper.Connect()
if conn != False:
	print('connection to db success')

if db_helper.Commit(conn, create):
	print('row created')

row1 = db_helper.Fetch(conn, read)
if row1 != None:
	print(row1)
	print('read successful')

if db_helper.Commit(conn, update):
	row2 = db_helper.Fetch(conn, read)
	if row1 != row2:
		print(row2)
		print('read check for update success')

if db_helper.Commit(conn, delete):
	if db_helper.Fetch(conn, read) == None:
		print('row deleted')
