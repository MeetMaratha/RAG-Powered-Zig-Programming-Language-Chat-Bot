import os
import time
from pathlib import Path
from typing import Set

import requests

if __name__ == "__main__":
    processed_files: Set[str] = set()  # Fixed type: store filenames as strings
    folder_path: Path = Path("zig-documentations")

    while True:
        try:
            # Check if directory exists
            if not folder_path.exists() or not folder_path.is_dir():
                print(f"Directory not found: {folder_path}. Waiting...")
                time.sleep(5)
                continue

            current_files = set(os.listdir(folder_path))
            new_files = current_files - processed_files

            if new_files:
                file_name = next(iter(new_files))  # Get one new file
                processed_files.add(file_name)  # Mark as processed immediately
                file_path = folder_path / file_name

                # Verify it's a file and exists
                if file_path.is_file():
                    try:
                        # Read file
                        with open(file_path, "r", encoding="utf-8") as f:
                            text: str = f.read()

                        # Send request
                        response = requests.post(
                            url="http://chunker-function:8080/2015-03-31/functions/function/invocations",
                            json={"text": text},
                            timeout=10,  # Add timeout
                        )
                        print(f"Successfully processed: {file_name}")

                    except Exception as e:
                        print(f"Error processing {file_name}: {str(e)}")
                else:
                    print(f"Skipped non-file: {file_name}")
            else:
                # No new files - sleep to reduce CPU usage
                time.sleep(1)

        except FileNotFoundError:
            print(f"Directory temporarily inaccessible. Retrying...")
            time.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            time.sleep(5)
