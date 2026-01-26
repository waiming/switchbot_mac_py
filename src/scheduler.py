import schedule
import time
import subprocess
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

def run_pressing_script():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running pressing3times.py...")
    print("-" * 60)
    try:
        result = subprocess.run(
            ["python", "pressing3times.py"],
            cwd=script_dir,
            capture_output=True,
            text=True
        )
        # Print the output from the script
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        print("-" * 60)
        if result.returncode == 0:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Success!")
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Failed with exit code {result.returncode}")
    except Exception as e:
        print("-" * 60)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Exception: {e}")

# Schedule the task to run every 1 hour 
schedule.every(1).hours.do(run_pressing_script)

print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Scheduler started. Will run pressing3times.py every 1 hour.")
print("Press Ctrl+C to stop.")

# Run once immediately on startup (optional - remove if you don't want this)
run_pressing_script()

# Keep the scheduler running
while True:
    schedule.run_pending()
    time.sleep(1)
