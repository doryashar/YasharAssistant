import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

from os import getenv
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, BackgroundTasks, Request, Response, Query
from src.WhatsAppBot import handle_data 
# from pydantic import BaseModel

# class Base(BaseModel):
#     username: str
#     age: int

load_dotenv()
app = FastAPI()

# @app.route('/sayname')
# def sayname():
#     return '<h1>Hello Flask</h1>'

@app.get("/")
async def verify_token(
    token: str = Query(alias="hub.verify_token"),
    challenge: str = Query(alias="hub.challenge"),
    ):
    if token == getenv('FLASK_VERIFY_TOKEN'):
        logging.info("Verified webhook")
        return challenge
    logging.error("Webhook Verification failed")
    return "Invalid verification token"
 
@app.post("/")
async def hook(request: Request, bg_tasks: BackgroundTasks): 
    data = await request.json()
    logging.debug("Received webhook data: %s", data)
    bg_tasks.add_task(handle_data, data)
    return "Success"


# @app.on_event('startup')
# async def app_startup():
#     asyncio.create_task(runner())


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8070)
    
    
