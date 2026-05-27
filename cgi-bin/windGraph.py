#!/usr/bin/env python3
import subprocess

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
pathToResources = BASE_DIR.parent / 'cgi-bin'       # where the data cache and the "static" resources are stored.


def run_step(script_name):
    # Runs the sub-program and captures its output
    result = subprocess.run(['python3', script_name], capture_output=True, text=True)
    return result.stdout.strip()

def main():
    # Print CGI header  We hold off and let the actual program generate the header so we can
    # return an error if something goes wrong. If the first program fails, we don't want to
    # return a 200 OK header.
    # print("Content-Type: text/html\n")  The return from the successful returns this response header.

    # Step 1: Run first program
    response = run_step(pathToResources / 'windGraphOCR.py')
    # response = run_step(pathToResources / 'windGraphNWS.py')

    # Step 2: Act on result and run next if successful
    if "SUCCESS" in response:
        # Looks good so far but how old is the data?
        # # Step 3: Run final program
        if ("hours ago" in response  and float(response.split("'")[1]) > 5):
            # OCR data is too old, so we should try the NWS data instead.
            response = run_step(pathToResources / 'windGraphNWS.py')

        print(f"{response}")
    else:
        print(f"{response}")

if __name__ == "__main__":
    main()
