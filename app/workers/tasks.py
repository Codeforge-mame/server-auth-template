from app.workers.celery_client import celery_app
import asyncio


# Helper to run async code inside a synchronous Celery task
def run_sync(coro):
    return asyncio.get_event_loop().run_until_complete(coro)