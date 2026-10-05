try:
    from .celery import app as celery_app
except ModuleNotFoundError:  # Allows management commands before optional workers are installed.
    celery_app = None
__all__=("celery_app",)
