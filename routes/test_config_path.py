import sys
import os

# Add parent directory to path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

def check_base_dir():
    print(f"BASE_DIR: {Config.BASE_DIR}")
    expected = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print(f"Expected: {expected}")
    
    if Config.BASE_DIR == expected:
        print("SUCCESS: BASE_DIR matches expected path")
    else:
        print("FAILURE: BASE_DIR does not match")

if __name__ == "__main__":
    check_base_dir()
