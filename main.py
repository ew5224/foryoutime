from fastapi import FastAPI, Request, Form
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.templating import Jinja2Templates
import logging
from service import get_correction_from_db, parse_url, get_server_time_from_url, get_server_time_from_url_by_string
logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

@app.get("/correction/")
async def get_correction(url: str, es=None):
    parsed_url = parse_url(url)
    correction = get_correction_from_db(parsed_url, es)
    logging.info(f"Elasped time : {correction}")
    return {'correction': correction}

@app.get("/server_time/")
async def get_server_time(url: str):
    parsed_url = parse_url(url)
    server_time = get_server_time_from_url([parsed_url])
    return {"server_time": int(server_time)}


@app.get("/modified_server_time/")
async def get_modified_server_time(url: str, es=None):
    server_time = get_server_time_from_url(url)

    parsed_url = parse_url(url)
    correction = get_correction_from_db(parsed_url, es)

    modified_server_time = server_time - correction
    logging.info(f"Elasped time : {correction}")
    return {"server_time": int(modified_server_time)}

@app.get("/test_foryoutime", response_class=HTMLResponse)
async def read_root(request : Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/test_foryoutime/get_server_time/", response_class=JSONResponse)  # JSON 형식의 응답을 반환하도록 수정
async def get_server_time(request: Request, url: str = Form(...)):
    try:
        result = get_server_time_from_url_by_string(url)
        return {"server_date": result}

    except Exception as e:
        error_message = f"Error: {str(e)}"
        return {"error_message": error_message}