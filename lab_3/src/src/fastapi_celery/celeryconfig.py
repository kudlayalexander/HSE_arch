from kombu import Queue

task_track_started = True
result_persistent = True
task_acks_late = True


task_queues = (
    Queue('default', routing_key='task.#'),
    Queue('ssh_queue', routing_key='ssh.#'),
    Queue('rs232_queue', routing_key='rs232.#'),
    Queue('install_queue', routing_key='install.#'),
)

task_default_queue = 'default'
task_default_exchange = 'tasks'
task_default_exchange_type = 'topic'
task_default_routing_key = 'task.default'


task_routes = {
    'src.fastapi_celery.device_ssh.tasks': {'queue': 'ssh_queue'},
    'src.fastapi_celery.device_rs232.tasks': {'queue': 'rs232_queue'},
    'src.fastapi_celery.device_install.tasks': {'queue': 'install_queue'},
}
