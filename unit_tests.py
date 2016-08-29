#test cases

import unittest
from config import my_summ_id
from db_connections import player_data_CRUD

class player_data_test_case(unittest.TestCase):
	#standard method
	def setUp(self):
		self.test_summ_id = 123
		self.initial_api_summ_hash = {'id' : 123, 'name' : 'test_name', 'revisionDate' : 111111111 }
		self.final_api_summ_hash = {'id' : 123, 'name' : 'test_name1', 'revisionDate' : 999999999 }

	def test_player_CRUD_actions(self):
		self.test_CRUD = player_data_CRUD(self.test_summ_id)
		self.assertEqual(self.test_CRUD.Read_Summ_Row(), [])
		self.assertEqual(self.test_CRUD.Update_Create(self.initial_api_summ_hash), 'create')
		self.assertEqual(self.test_CRUD.Read_Summ_Row()[0].revision_date, 111111111)
		self.assertEqual(self.test_CRUD.Update_Create(self.final_api_summ_hash), 'update')
		self.assertEqual(self.test_CRUD.Read_Summ_Row()[0].revision_date, 999999999)

	def tearDown(self):
	#delete row
		self.test_CRUD.Delete_Summ_Row()
	#check row if row exists

class api_call_test_case()

if __name__ == '__main__':
	unittest.main()