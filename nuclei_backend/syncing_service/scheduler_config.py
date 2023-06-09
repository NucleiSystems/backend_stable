from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor


class SchConfig:
    executors = {
        "default": ThreadPoolExecutor(20),
        "processpool": ProcessPoolExecutor(5),
    }
    job_defaults = {
        "coalesce": False,
        "max_instances": 10,
    }
    timezone = "UTC"
