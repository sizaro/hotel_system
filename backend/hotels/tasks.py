from celery import shared_task
@shared_task
def daily_operations_summary():
    return {"status":"scheduled","message":"Daily hotel summary foundation is active."}
