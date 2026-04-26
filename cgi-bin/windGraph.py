#!/usr/bin/env python3
import subprocess
import cgi

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
pathToResources = BASE_DIR.parent / 'cgi-bin'       # where the data cache and the "static" resources are stored.


def run_step(script_name):
    # Runs the sub-program and captures its output
    result = subprocess.run(['python3', script_name], capture_output=True, text=True)
    return result.stdout.strip()

def main():
    # Print CGI header
    print("Content-Type: text/html\n")

    # Step 1: Run first program
    response = run_step(pathToResources / 'windGraphOCR.py')

    # Step 2: Act on result and run next if successful
    if "PROCEED" in response1:
        response = run_step(pathToResources / 'windGraphNWS.py')

        # # Step 3: Run final program
        # if "PROCEED" in response2:
        #     final_response = run_step('program3.py')
        #     print(f"Workflow Complete: {final_response}")
        # else:
        print(f"{response}")
    else:
        print(f"{response}")

if __name__ == "__main__":
    main()
