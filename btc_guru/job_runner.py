from etl.coinapi import CoinApiETL
from etl.ml import MLETL
from helpers.ml.train_model import MLTools
from schedule import Scheduler, Job
import threading
from traceback import format_exc
from config import logger
from typing import Callable
import logging
from datetime import datetime, timedelta
import time


class SafeScheduler(Scheduler):
    """
    An implementation of Scheduler that catches jobs that fail, logs their
    exception tracebacks as errors, optionally reschedules the jobs for their
    next run time, and keeps going.
    Use this to run jobs that may or may not crash without worrying about
    whether other jobs will run or if they'll crash the entire script.
    """

    def __init__(self, reschedule_on_failure: bool = True, logger: logging.Logger = None) -> None:
        """
        If reschedule_on_failure is True, jobs will be rescheduled for their
        next run as if they had completed successfully. If False, they'll run
        on the next run_pending() tick.
        """
        self.logger = logger
        self.reschedule_on_failure = reschedule_on_failure
        super().__init__()

    def _run_job(self, job: Job) -> None:
        try:
            super()._run_job(job)
        except Exception:
            if self.logger:
                self.logger.error(format_exc())
            job.last_run = datetime.now()
            job._schedule_next_run()


def run_threaded(job_func: Callable) -> None:
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def coinapi_job_factory() -> None:
    capi = CoinApiETL(time_start=(datetime.now() - timedelta(hours=24)).isoformat()[:14] + '00:00',
                      time_end=datetime.now().isoformat()[:14] + '00:00')
    capi.job()


def mletl_job_factory() -> None:
    mletl = MLETL()
    mletl.job()


def ml_training_job_fatory() -> None:
    mlt = MLTools()
    mlt.train_model()


if __name__ == '__main__':
    scheduler = SafeScheduler(logger=logger)
    scheduler.every().hour.at(":00").do(run_threaded, coinapi_job_factory)
    scheduler.every().hour.at(":10").do(run_threaded, mletl_job_factory)
    scheduler.every().sunday.at("00:00").do(run_threaded, ml_training_job_fatory)
    while True:
        logger.debug('Heartbeat 5 seconds')
        scheduler.run_pending()
        time.sleep(5)
