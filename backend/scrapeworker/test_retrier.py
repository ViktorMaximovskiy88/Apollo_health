import pytest
from backend.scrapeworker.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_retrier():
    wait_between_requests = 0.1
    rl = RateLimiter(wait_between_requests=wait_between_requests)
    async for attempt in rl.attempt_with_backoff():
        with attempt:
            if attempt.retry_state.attempt_number == 1:
                raise Exception("First Failure")
            if attempt.retry_state.attempt_number == 2:
                raise Exception("Second Failure")

    assert rl.wait_between_requests == wait_between_requests * 2**2
