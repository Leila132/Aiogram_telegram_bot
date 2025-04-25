from celery import Celery

app = Celery(
    "tasks",
    broker="amqp://guest:guest@localhost:5672/",
    backend="db+sqlite:///celery_results.sqlite",
)
app.autodiscover_tasks(["config.tasks"])
