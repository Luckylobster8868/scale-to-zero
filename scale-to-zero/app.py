# API: receives a request, puts it in the Redis queue, lets you check the result.
import os
import uuid
import redis
from fastapi import FastAPI, HTTPException

app = FastAPI()
r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)


@app.post("/jobs")
def create_job(text: str):
    job_id = str(uuid.uuid4())
    r.hset(f"job:{job_id}", mapping={"status": "queued", "text": text})
    r.rpush("jobs", job_id)  # add to the queue KEDA is watching
    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    data = r.hgetall(f"job:{job_id}")
    if not data:
        raise HTTPException(status_code=404, detail="job not found")
    return data
