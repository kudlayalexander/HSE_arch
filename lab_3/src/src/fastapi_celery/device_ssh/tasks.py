import datetime

import paramiko
from celery import states
from celery.exceptions import MaxRetriesExceededError
from celery.utils.log import get_task_logger
from paramiko.ssh_exception import ChannelException, NoValidConnectionsError

from ..enums import ImageType, SshUser, DeviceType
from ..exceptions import ReceivingPasswordError
from .worker import ssh_worker
from .schemas import SshResult
from .ssh_password import get_password

logger = get_task_logger("SshTask")


@ssh_worker.task(name="ssh", bind=True, max_retries=3, default_retry_delay=5, queue='ssh_queue')
def task_ssh(
        self,
        command: str,
        hostname: str,
        username: SshUser,
        device_type: DeviceType,
        image_type: ImageType,
        port: int = 22,
        cmd_timeout: int = 5
) -> SshResult:
    try:
        self.update_state(state=states.STARTED,
                          meta={})

        password = get_password(username, image_type, device_type)

        start_time = datetime.datetime.now()

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=hostname, port=port,
                           username=username, password=password)

        self.update_state(state=states.STARTED,
                          meta={'cmd': f'{command}'})

        stdin, stdout, stderr = ssh_client.exec_command(
            command, timeout=cmd_timeout)

        output = stdout.read().decode(errors="skip")
        error = stderr.read().decode(errors="skip")

        # Blocking call if command was not finished
        retcode = stdout.channel.recv_exit_status()
        ssh_client.close()

        logger.info("Finished SSH!")

        end_time = datetime.datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        response = SshResult(
            stdout=output, stderr=error, retcode=retcode, execution_time_s=execution_time)

        return response.model_dump()
    except MaxRetriesExceededError as e:
        self.update_state(state=states.FAILURE,
                          meta={'exc_type': type(e).__name__,
                                'exc_message': e.__str__()})
    except paramiko.AuthenticationException as e:
        self.update_state(state=states.RETRY,
                          meta={'exc_type': type(e).__name__,
                                'exc_message': e.__str__()})
    except paramiko.SSHException as e:
        self.update_state(state=states.RETRY,
                          meta={'exc_type': type(e).__name__,
                                'exc_message': e.__str__()})
    except NoValidConnectionsError as e:
        self.update_state(state=states.RETRY,
                          meta={'exc_type': type(e).__name__,
                                'exc_message': e.__str__()})
    except ReceivingPasswordError as e:
        self.update_state(state=states.RETRY,
                          meta={'exc_type': type(e).__name__,
                                'exc_message': e.__str__()})
    except Exception as e:
        self.update_state(state=states.RETRY,
                          meta={'exc_type': type(e).__name__,
                                'exc_message': e.__str__()})
