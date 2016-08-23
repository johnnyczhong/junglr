#prog_name: connections_test.py
#purpose: test connections to riot api and aws db when initializing new box
#	in my case, I'm using both my local Mac and c9 for development.

from config import api_key, aws_host, aws_db, aws_user, aws_pass
from db_helper import Connect, Fetch
from champ_api import Hash_Get_Single_Champ_Info

# conn = Connect()
# query = 'select champ_name from champ_data where champ_id = 254 limit 1;'
# print(Fetch(query, conn))

print(Hash_Get_Single_Champ_Info(254))
