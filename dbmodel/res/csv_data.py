import pandas as pd
import pathlib
from dbmodel.dbconfig import s

def load_data(file_name):
    file_name = pathlib.Path(__file__).absolute().parent/'test_data'/file_name
    data = pd.read_csv(file_name, quotechar='"', skipinitialspace=True, encoding = "latin1")
    data = data.where(pd.notnull(data), None)
    data = data.to_dict(orient='records')
    return data

def save_test_data(file_name, model, ):
    data = load_data(file_name)
    for row in data:
        model1 = model(**row)
        s.add(model1)
        s.commit()
        s.close()