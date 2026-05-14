# main.py
import os
import sys

# 1. Path Setup: Get the folder where main.py sits
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(BASE_DIR, 'src')

# 2. Tell Python to look inside the 'src' folder for our scripts
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# 3. Import the functions from your files
try:
    from data_loader import get_processed_data
    from train_base import train_specialists
    from ensemble_blend import run_blending_ensemble
    print("✅ Successfully linked to all scripts in src/")
except ImportError as e:
    print(f"❌ Still can't find a file: {e}")
    print(f"I am looking in: {SRC_PATH}")
    sys.exit(1)

def main():
    print("\n🚀 Starting Pipeline...")
    
    # Run Step 1: Training
    train_specialists()
    
    # Run Step 2: Blending
    run_blending_ensemble()

if __name__ == "__main__":
    main()