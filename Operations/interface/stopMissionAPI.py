from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from Judge.Operations.toServer.stopMission import kill_pid

global killing_pid


class mission_params(BaseModel):
    server_pid: int
    serverContext: str


app = FastAPI()


@app.post("/stopmission")
async def get_progress(item: mission_params):
    global killing_pid
    killing_pid = item.server_pid
    return {"Start killing mission"}


@app.get('/stopmission')
async def root():
    global killing_pid
    print(killing_pid)
    return (killing_pid)


print(get_progress(mission_params))

print(1)

# if __name__ == "__main__":
#     uvicorn.run(app='progressAPI:app', host="0.0.0.0", port=8007, reload=True, debug=False)
