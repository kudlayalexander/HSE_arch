import datetime

from celery import states
from celery.exceptions import MaxRetriesExceededError
from celery.utils.log import get_task_logger
from serial import SerialException, SerialTimeoutException

from ..exceptions import Rs232Exception
from .schemas import Rs232ReadResult, Rs232WriteAndReadResult, Rs232WriteResult
from .serial_module import (connect_via_serial, read_from_serial,
                            write_to_serial)
from .worker import rs232_worker

logger = get_task_logger("Rs232Task")


@rs232_worker.task(name="rs232_read", max_retries=2, default_retry_delay=3, bind=True, queue='rs232_queue')
def rs232_read_task(
    self,
    port: str,
    timeout: float,
    baudrate: int
) -> Rs232ReadResult:
    self.update_state(state=states.STARTED,
                      meta={})
    serial = connect_via_serial(
        port=port, baudrate=baudrate, timeout=timeout)

    try:
        start_time = datetime.datetime.now()

        serial_output = read_from_serial(serial)

        end_time = datetime.datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        response = Rs232ReadResult(
            output=serial_output, execution_time_s=execution_time)

        return response.model_dump()
    except MaxRetriesExceededError as e:
        self.update_state(state=states.FAILURE, meta={})
    except Rs232Exception as e:
        self.update_state(state=states.RETRY, meta={
                          'exception': f'Exception with serial. Exception: {str(e)}'})
    except SerialException as e:
        self.update_state(state=states.RETRY,
                          meta={'exc_type': type(e).__name__,
                                'exc_message': e.__str__()})
    except SerialTimeoutException as e:
        self.update_state(state=states.RETRY,
                          meta={'exc_type': type(e).__name__,
                                'exc_message': e.__str__()})
    except Exception as e:
        self.update_state(state=states.RETRY, meta={
                          'exception': f'Unexpected exception. Exception: {str(e)}. Type: {type(e)}'})
    finally:
        serial.close()


@rs232_worker.task(name="rs232_write", bind=True, max_retries=2, default_retry_delay=3, queue='rs232_queue')
def rs232_write_task(
    self,
    port: str,
    baudrate: int,
    timeout: float,
    text: str
) -> Rs232WriteResult:
    self.update_state(state=states.STARTED,
                      meta={})
    serial = connect_via_serial(
        port=port, baudrate=baudrate, timeout=timeout)

    try:
        start_time = datetime.datetime.now()

        write_to_serial(serial, text)

        end_time = datetime.datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        response = Rs232WriteResult(
            execution_time_s=execution_time)

        return response.model_dump()
    except MaxRetriesExceededError as e:
        self.update_state(state=states.FAILURE, meta={})
    except Rs232Exception as e:
        self.update_state(state=states.RETRY, meta={
                          'exception': f'Exception with serial. Exception: {str(e)}'})
    except SerialException as e:
        self.update_state(state=states.RETRY,
                          meta={'exc_type': type(e).__name__,
                                'exc_message': e.__str__()})
    except SerialTimeoutException as e:
        self.update_state(state=states.RETRY,
                          meta={'exc_type': type(e).__name__,
                                'exc_message': e.__str__()})
    except Exception as e:
        self.update_state(state=states.RETRY, meta={
                          'exception': f'Unexpected exception. Exception: {str(e)}. Type: {type(e)}'})
    finally:
        serial.close()


@rs232_worker.task(name="rs232_write_and_read", max_retries=2, default_retry_delay=3, bind=True, queue='rs232_queue')
def rs232_write_and_read_task(
    self,
    port: str,
    baudrate: int,
    text: str,
    timeout: float
) -> Rs232WriteAndReadResult:
    self.update_state(state=states.STARTED,
                      meta={})
    serial = connect_via_serial(
        port=port, baudrate=baudrate, timeout=timeout)

    try:
        start_time = datetime.datetime.now()

        write_to_serial(serial, text)

        serial_output = read_from_serial(serial)

        end_time = datetime.datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        response = Rs232WriteAndReadResult(
            execution_time_s=execution_time, output=serial_output)

        return response.model_dump()
    except MaxRetriesExceededError as e:
        self.update_state(state=states.FAILURE, meta={})
    except Rs232Exception as e:
        self.update_state(state=states.RETRY, meta={
                          'exception': f'Exception with serial. Exception: {str(e)}'})
    except SerialException as e:
        self.update_state(state=states.RETRY,
                          meta={'exc_type': type(e).__name__,
                                'exc_message': e.__str__()})
    except SerialTimeoutException as e:
        self.update_state(state=states.RETRY,
                          meta={'exc_type': type(e).__name__,
                                'exc_message': e.__str__()})
    except Exception as e:
        self.update_state(state=states.RETRY, meta={
                          'exception': f'Unexpected exception. Exception: {str(e)}. Type: {type(e)}'})
    finally:
        serial.close()
