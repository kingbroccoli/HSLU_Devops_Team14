from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import pickle
import pandas as pd
import json

# load model on startup
model = None
with open('model/best_model.pickle', 'rb') as fin:
    model = pickle.load(fin)

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def root():
    return '''
    <h3>House_Price_Prediction</h3>
    <form action="predict/" method="post">
    <textarea name="data" style="width:300px; height:600px">[{
        "MSSubClass": 50,
        "LotArea": 8064,
        "OverallCond": 7,
        "YearBuilt": 1948,
        "YearRemodAdd": 1994,
        "BsmtFinSF2": 0.0,
        "TotalBsmtSF": 864.0,
        "MSZoning_C_all": 0.0,
        "MSZoning_FV": 0.0,
        "MSZoning_RH": 0.0,
        "MSZoning_RL": 1.0,
        "MSZoning_RM": 0.0,
        "LotConfig_Corner": 1.0,
        "LotConfig_CulDSac": 0.0,
        "LotConfig_FR2": 0.0,
        "LotConfig_FR3": 0.0,
        "LotConfig_Inside": 0.0,
        "BldgType_1Fam": 1.0,
        "BldgType_2fmCon": 0.0,
        "BldgType_Duplex": 0.0,
        "BldgType_Twnhs": 0.0,
        "BldgType_TwnhsE": 0.0,
        "Exterior1st_AsbShng": 0.0,
        "Exterior1st_AsphShn": 0.0,
        "Exterior1st_BrkComm": 0.0,
        "Exterior1st_BrkFace": 0.0,
        "Exterior1st_CBlock": 0.0,
        "Exterior1st_CemntBd": 0.0,
        "Exterior1st_HdBoard": 0.0,
        "Exterior1st_ImStucc": 0.0,
        "Exterior1st_MetalSd": 1.0,
        "Exterior1st_Plywood": 0.0,
        "Exterior1st_Stone": 0.0,
        "Exterior1st_Stucco": 0.0,
        "Exterior1st_VinylSd": 0.0,
        "Exterior1st_Wd_Sdng": 0.0,
        "Exterior1st_WdShing": 0.0
    }]
    </textarea><br>
    <br>
    <button type="submit">Submit</button>
    </form>

    '''


@app.post("/predict/")
async def predict(data=Form()):
    data_dict = json.loads(data)
    X = pd.DataFrame.from_dict(data_dict)
    y = model.predict(X)
    return {"predictions": list(y)}
