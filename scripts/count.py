import re
import sys
from collections import Counter

content = sys.stdin.read()
failures = []
for line in content.split('\n'):
    if line.startswith('FAILED ') or line.startswith('ERROR '):
        parts = line.split(' ')
        if len(parts) >= 2:
            test_file = parts[1].split('::')[0]
            failures.append(test_file)

counter = Counter(failures)
for item, count in sorted(counter.items()):
    val = int(count)
    if 'tests/' in item:
        print(f'{val} {item}')
