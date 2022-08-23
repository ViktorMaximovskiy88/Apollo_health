import asyncio
from datetime import datetime, timezone

from tenacity._asyncio import AsyncRetrying
from tenacity.stop import stop_after_attempt


class RateLimiter:
    def __init__(self, wait_between_requests: float = 1) -> None:
        self.last_request_time = datetime.now(tz=timezone.utc)
        self.wait_between_requests = wait_between_requests
        pass

    def remaining_wait(self):
        time_since_last_request = datetime.now(tz=timezone.utc) - self.last_request_time
        remaining_wait = self.wait_between_requests - time_since_last_request.total_seconds()
        return remaining_wait

    async def wait(self):
        wait = self.remaining_wait()
        while wait > 0:
            await asyncio.sleep(wait)
            wait = self.remaining_wait()

    def increase_wait(self):
        print("increased_wait", self.wait_between_requests)
        if self.wait_between_requests < 32:
            self.wait_between_requests *= 1.5

    def decrease_wait(self):
        if self.wait_between_requests > 1:
            self.wait_between_requests /= 1.5

    async def attempt_with_backoff(self, stop_attempts=16):
        """
        Attempts to run the function, if it fails, increase the wait time and try again, max 60 sec.
        If it succeeds, reduce the wait time, min 1 second.
        """
        async for attempt in AsyncRetrying(reraise=True, stop=stop_after_attempt(stop_attempts)):
            await self.wait()

            self.last_request_time = datetime.now(tz=timezone.utc)
            yield attempt

            res = attempt.retry_state.outcome
            if res and not res.cancelled() and res.exception():
                print(res.exception())
                self.increase_wait()
            else:
                self.decrease_wait()
