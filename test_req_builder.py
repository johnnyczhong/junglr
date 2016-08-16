#test file

import req_builder
from config import my_summ_name

if req_builder.Int_Summ_Name_to_ID(my_summ_name) != 333035:
    print('Int_Summ_ID failure')

if type(req_builder.Get_Match_History(my_summ_name)) != dict:
    print('Get_Match_History failure')

if req_builder.S_CID_to_CName(113) != 'Sejuani':
    print('S_CID_to_CName failure')
