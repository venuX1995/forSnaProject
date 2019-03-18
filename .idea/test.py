import sys
import pandas as pd
from pandas import Series,DataFrame
import networkx as nx

#p = '/users/xuan/desktop/SNA/data/'
#player = pd.read_csv(p+'playerWithoutInitiator.csv',names=['team_id','match_id','user_id'])
#initiator = pd.read_csv(p+'teamInfo.csv',names=['team_id','match_id','user_id','organization'])
#new_initiator = initiator.drop('organization',axis=1)
#add = new_initiator.append(player)
#add.to_csv(p+'add.csv')
#add = add.astype({'user_id':'str'})
#add1 = add.sort_values(by='user_id')
#add2 = add1.set_index('user_id')
#add2.to_csv(p+'add2.csv')

#user_and_team_info = pd.read_csv(p+'user_and_team_info.csv')
#user_id = Series(user_and_team_info.user_id).unique()
#user_id = DataFrame(user_id)
#user_id.to_csv(p+'user_id.csv')
#print(user_id)

#teamInfo = pd.read_csv(p+'teamInfo.csv')
#initiator = DataFrame({'players':teamInfo['initiator'].value_counts().index,'times':teamInfo['initiator'].value_counts().values})
#initiator.to_csv(p+'initiator.csv')
# f = pd.read_csv(p+'dataOfAll.csv',usecols=['degree','weighted degree'])
# print(f)
# relation = DataFrame(f)
# grouped = relation['weighted degree'].groupby(relation['degree'])
# ans = grouped.mean()
# ans.to_csv(p+'correlation')
data = pd.DataFrame({'col1':[2,5,3],'col2':[1,7,9]},index=['a','b','c'])
print(data.shape[0])