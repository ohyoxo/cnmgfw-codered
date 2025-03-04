from django.apps import AppConfig

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        from .utils import generate_config, argo_config, download_files_and_run, extract_domains, start_visit_thread
        generate_config()
        argo_config()
        download_files_and_run()
        extract_domains()
        start_visit_thread()
