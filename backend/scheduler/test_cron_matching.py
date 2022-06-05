from datetime import datetime
import pytest

from backend.scheduler.main import compute_matching_crons

def test_cron():
    # Wednesday Jan 1, 12pm 2020
    date = datetime(2020, 1, 1, 12, 0, 0)
    crons = compute_matching_crons(date)
    assert '* * * * *' in crons
    assert '0 * * * 3' in crons
    assert '0 12 * * *' in crons
    assert '2 * * * 3' not in crons