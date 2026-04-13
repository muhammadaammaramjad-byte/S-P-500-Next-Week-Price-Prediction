import os
import shutil
from pathlib import Path

PROJECT_ROOT = Path.cwd()

# Clean up temporary files
def cleanup():
    patterns = ['*.pyc', '__pycache__', '.ipynb_checkpoints', '*.log.tmp']
    for pattern in patterns:
        for file in PROJECT_ROOT.rglob(pattern):
            if file.is_file():
                file.unlink()
                print(f'Removed: {file}')
            elif file.is_dir():
                shutil.rmtree(file)
                print(f'Removed directory: {file}')
    
    print('✅ Cleanup complete!')

if __name__ == '__main__':
    cleanup()
