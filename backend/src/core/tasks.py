"""
Celery 기반 비동기 작업 큐 설정
Redis 브로커/백엔드를 사용하며 AI 파이프라인 작업을 큐잉할 수 있도록 헬퍼를 제공합니다.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Optional

from celery import Celery
from celery.app.task import Task
from celery.result import AsyncResult
from celery.utils.log import get_task_logger
from celery.schedules import crontab
from kombu import Queue

from ..config.settings import settings

logger = get_task_logger(__name__)

# Celery application 초기화
celery_app = Celery(
    "traveltailor",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_default_queue="default",  # 기본 큐를 'default'로 설정하여 워커가 소비할 수 있도록 함
    broker_transport_options={"visibility_timeout": 60 * 60},  # 1 hour
    task_time_limit=60 * 10,  # Hard limit: 10 minutes
    task_soft_time_limit=60 * 8,  # Soft limit: 8 minutes
    worker_max_tasks_per_child=100,
)

# 큐 라우팅 설정
celery_app.conf.task_queues = (
    Queue("default", routing_key="default.#"),
    Queue("ai-tasks", routing_key="ai.#"),
    Queue("low-priority", routing_key="low.#"),
)


class AsyncTask(Task):
    """
    Celery에서 비동기 함수를 실행하기 위한 Task 베이스 클래스.
    자식 클래스는 `async def run_async(...)`를 구현하면 됩니다.
    """

    abstract = True

    async def run_async(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover - interface
        raise NotImplementedError

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Celery가 호출하는 동기 엔트리 포인트"""
        logger.debug("Executing async task %s", self.name)
        return asyncio.run(self.run_async(*args, **kwargs))


def register_task(
    func: Callable[..., Any],
    *,
    name: Optional[str] = None,
    queue: str = "default",
    max_retries: int = 3,
    retry_backoff: int = 5,
) -> Task:
    """
    주어진 함수(동기 또는 비동기)를 Celery task로 등록하고 반환합니다.

    Args:
        func: 호출할 함수. 코루틴 함수도 허용합니다.
        name: task 고유 이름. 미지정 시 함수의 풀 네임을 사용합니다.
        queue: 라우팅할 큐 이름.
        max_retries: 자동 재시도 횟수.
        retry_backoff: 지수 백오프 초기 지연 (초).
    """
    task_name = name or f"{func.__module__}.{func.__qualname__}"

    if asyncio.iscoroutinefunction(func):

        @celery_app.task(
            name=task_name,
            bind=True,
            queue=queue,
            max_retries=max_retries,
            autoretry_for=(Exception,),
            retry_backoff=retry_backoff,
            retry_backoff_max=60,
        )
        def _async_wrapper(self: Task, *args: Any, **kwargs: Any) -> Any:
            logger.info("Dispatching async task %s", task_name)
            return asyncio.run(func(*args, **kwargs))

        return _async_wrapper

    @celery_app.task(
        name=task_name,
        bind=True,
        queue=queue,
        max_retries=max_retries,
        autoretry_for=(Exception,),
        retry_backoff=retry_backoff,
        retry_backoff_max=60,
    )
    def _sync_wrapper(self: Task, *args: Any, **kwargs: Any) -> Any:
        logger.info("Dispatching sync task %s", task_name)
        return func(*args, **kwargs)

    return _sync_wrapper


def enqueue_task(task_name: str, *args: Any, **kwargs: Any) -> AsyncResult:
    """
    등록된 Celery task를 큐에 추가합니다.

    Example:
        enqueue_task("backend.services.ai.planner.generate_plan", plan_id)
    """
    logger.debug("Queueing task %s with args=%s kwargs=%s", task_name, args, kwargs)
    return celery_app.send_task(task_name, args=args, kwargs=kwargs)


def start_worker(argv: Optional[list[str]] = None) -> None:
    """
    개발 환경에서 Celery 워커를 실행하기 위한 헬퍼.
    예: `uv run python -m backend.src.core.tasks worker`
    """
    arguments = argv or ["worker", "--loglevel=INFO", "--queues=default,ai-tasks"]
    celery_app.worker_main(arguments)


def schedule_periodic_task(name: str, task: str, cron: str) -> None:
    """
    Celery Beat 스케줄에 주기적 작업을 등록합니다.

    Args:
        name: 스케줄 이름
        task: 호출할 task dotted-path
        cron: crontab 표현식 (예: "0 * * * *")
    """
    celery_app.conf.beat_schedule = celery_app.conf.beat_schedule or {}
    parts = cron.split()
    if len(parts) != 5:
        raise ValueError("Cron expression must have 5 space-separated fields")

    minute, hour, day_of_month, month_of_year, day_of_week = parts
    celery_app.conf.beat_schedule[name] = {
        "task": task,
        "schedule": crontab(
            minute=minute,
            hour=hour,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
            day_of_week=day_of_week,
        ),
    }
