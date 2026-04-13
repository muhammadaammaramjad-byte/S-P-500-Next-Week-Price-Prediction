import os
import logging
from typing import List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

logger = logging.getLogger(__name__)

def get_optimal_workers(task_type: str = 'cpu') -> int:
    cpu_count = os.cpu_count() or 4
    if task_type == 'cpu':
        return max(1, cpu_count - 1)
    return min(32, cpu_count * 4)

def parallel_map(func: Callable, items: List, max_workers: Optional[int] = None) -> List:
    if max_workers is None:
        max_workers = get_optimal_workers('io')
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(func, item): item for item in items}
        for future in as_completed(futures):
            results.append(future.result())
    return results
