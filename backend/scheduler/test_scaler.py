import pytest

from backend.scheduler.main import get_new_cluster_size

def test_scaler_increase():
    queue_size = 10000
    active_workers = 10
    tasks_per_worker = 5
    updated_size = get_new_cluster_size(queue_size, active_workers, tasks_per_worker)
    assert updated_size == 2000

def test_scaler_decrease():
    queue_size = 10
    active_workers = 100
    tasks_per_worker = 5
    updated_size = get_new_cluster_size(queue_size, active_workers, tasks_per_worker)
    assert updated_size == 2

def test_scaler_close_enough():
    queue_size = 0
    active_workers = 100
    tasks_per_worker = 5
    updated_size = get_new_cluster_size(queue_size, active_workers, tasks_per_worker)
    assert updated_size == 1

def test_scaler_no_update():
    queue_size = 51
    active_workers = 10
    tasks_per_worker = 5
    updated_size = get_new_cluster_size(queue_size, active_workers, tasks_per_worker)
    assert updated_size == None