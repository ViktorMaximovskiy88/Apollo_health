import asyncio
from datetime import datetime
from tenacity._asyncio import AsyncRetrying
from tenacity.stop import stop_after_attempt


class RateLimiter:
    def __init__(self, wait_between_requests=1) -> None:
        self.last_request_time = datetime.now()
        self.wait_between_requests = wait_between_requests
        pass

    async def wait(self):
        time_since_last_request = datetime.now() - self.last_request_time
        remaining_wait = (
            self.wait_between_requests - time_since_last_request.total_seconds()
        )
        if remaining_wait > 0:
            await asyncio.sleep(remaining_wait)
            await self.wait()

    def increase_wait(self):
        print("increased_wait", self.wait_between_requests)
        if self.wait_between_requests < 64:
            self.wait_between_requests *= 1.5

    def decrease_wait(self):
        if self.wait_between_requests > 1:
            self.wait_between_requests /= 1.5

    async def attempt_with_backoff(self, stop_attempts=16):
        """
        Attempts to run the function, if it fails, increase the wait time and try again, max 1 minute.
        If it succeeds, reduce the wait time, min 1 second.
        """
        async for attempt in AsyncRetrying(stop=stop_after_attempt(stop_attempts)):
            await self.wait()

            self.last_request_time = datetime.now()
            yield attempt

            res = attempt.retry_state.outcome
            if res and not res.cancelled() and res.exception():
                print(res.exception())
                self.increase_wait()
            else:
                self.decrease_wait()
