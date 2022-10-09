#
# from fastapi import FastAPI
# from pydantic import BaseModel
# import uvicorn
#
#
# global mission_progress
#
# class Para(BaseModel):
#     taskID: int
#     missionType: str
#     server_pid: int
#     progress: float
#
# app = FastAPI()
#
#
# @app.post("/progress")
# async def get_progress(item:Para):
#     global mission_progress
#     s = item.progress
#     mission_progress = s
#     print(item.progress)
#     print(mission_progress)
#
#     return (mission_progress)
#
#
# @app.get('/get')
# async def root():
#     global mission_progress
#     print(mission_progress)
#     return{mission_progress}
#
# print(get_progress(Para))
#
# print(1)
#
#
# # if __name__ == "__main__":
# #     uvicorn.run(app='progressAPI:app', host="0.0.0.0", port=8006, reload=True, debug=False)
# #
# #     print(2)
# #
# #     print("moon:"+str(mission_progress))