import json

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates

from air_pressure.model.prediction_from_model import Prediction
from air_pressure.model.training_model import Train_Model
from air_pressure.validation_insertion.prediction_validation_insertion import \
    Pred_Validation
from air_pressure.validation_insertion.train_validation_insertion import \
    Train_Validation
from utils.read_params import read_params

app = FastAPI()

config = read_params()

templates = Jinja2Templates(directory=config["templates"]["dir"])

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        config["templates"]["index_html_file"], {"request": request}
    )


@app.get("/train")
async def trainRouteClient():
    try:
        train_val = Train_Validation()

        train_val.training_validation()

        train_model = Train_Model()

        model_score_lst = train_model.training_model()

        # load_prod_model = Load_Prod_Model()

        # load_prod_model.load_production_model(model_score_lst)

        return Response("Training successfull!!")

    except Exception as e:
        return Response(f"Error Occurred! {e}")


@app.get("/predict")
async def predictRouteClient():
    try:
        pred_val = Pred_Validation()

        pred_val.prediction_validation()

        pred = Prediction()

        bucket, filename, json_predictions = pred.predict_from_model()

        return Response(
            f"prediction file created in {bucket} bucket with filename as {filename}, and few of the predictions are {str(json.loads(json_predictions))}"
        )

    except Exception as e:
        return Response(f"Error Occurred! {e}")


if __name__ == "__main__":
    host = config["app"]["host"]

    port = config["app"]["port"]

    uvicorn.run(app, host=host, port=port)
