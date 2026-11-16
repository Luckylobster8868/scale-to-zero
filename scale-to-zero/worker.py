# Worker: takes jobs from the Redis queue and processes them.
# Kubernetes runs 0 copies of this until jobs appear in the queue.
import os
import time
import signal
import redis

r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)

running = True


def stop(signum, frame):
    # Kubernetes sends SIGTERM when scaling down. Finish the current job, then exit.
    global running
    running = False


signal.signal(signal.SIGTERM, stop)

print("worker started", flush=True)

while running:
    item = r.blpop("jobs", timeout=5)  # wait up to 5s for a job
    if item is None:
        continue

    job_id = item[1]
    r.hset(f"job:{job_id}", "status", "processing")
    text = r.hget(f"job:{job_id}", "text")
    print(f"processing {job_id}", flush=True)

    time.sleep(5)  # pretend this is slow work

    r.hset(
        f"job:{job_id}",
        mapping={"status": "done", "result": text.upper(), "words": len(text.split())},
    )
    print(f"finished {job_id}", flush=True)

print("worker stopped", flush=True)
