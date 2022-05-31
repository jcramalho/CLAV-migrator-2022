from numpy import NaN
from openpyxl import load_workbook
import classe as c
import tindice as ti
import entidade as e
import tipologia as tip
import leg 

data_file = '../dados/excel/Frecolha-20220204.xlsx'
sheets = ['100_csv','150_csv','200_csv','250_csv','300_csv','350_csv','400_csv','450_csv','500_csv','550_csv','600_csv',
            '650_csv','700_csv','710_csv','750_csv','800_csv','850_csv','900_csv','950_csv']

backsheets = ['ti_csv','leg_csv','ent_sioe_csv','tip_ent_csv']

# Load the entire workbook.
wb = load_workbook(data_file)

ws = wb['leg_csv']
data = ws.values
print(type(data), " :: ", data)
cols = next(data)
print(type(cols), " :: ", cols)
data = list(data)
print(type(data), " :: ", data[0])
idx = [r[0] for r in data]
data = (islice(r, 1, None) for r in data)
#df = pd.DataFrame(data, index=idx, columns=cols)