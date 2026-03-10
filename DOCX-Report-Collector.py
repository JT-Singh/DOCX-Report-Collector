"""
FINAL Document Collector
------------------------

Purpose
-------
This tool recursively scans a directory structure looking for DOCX files
whose filenames end with "_FINAL.docx". All matching files are copied
into a folder named "FINAL_TRs" created in the directory where the
script is executed.

Key Features
------------
1. Recursive directory traversal
2. Multithreaded processing using 75% of available CPU cores
3. SHA256 hash-based duplicate detection
4. Progress bar for visibility during large scans
5. Safe copying with metadata preservation
6. Automatic filename collision handling

Typical Use Case
----------------
Collecting final versions of reports or documents scattered across
large project directories.

Example
-------
Input structure:

Projects/
 ├─ ClientA/
 │   ├─ TR1_FINAL.docx
 │   └─ TR1_DRAFT.docx
 ├─ ClientB/
 │   └─ SecurityReview_FINAL.docx

Output:

FINAL_TRs/
 ├─ TR1_FINAL.docx
 └─ SecurityReview_FINAL.docx
"""

import os
import shutil
import hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import multiprocessing


# Name of the folder where matching files will be copied
DEST_FOLDER_NAME = "FINAL_TRs"


def calculate_hash(file_path, chunk_size=65536):
    """
    Compute the SHA256 hash of a file.

    Why hashing?
    ------------
    Different directories may contain identical copies of the same
    document. Instead of copying duplicates, we calculate a hash
    fingerprint for each file and only keep unique ones.

    Parameters
    ----------
    file_path : Path
        Path to the file being hashed.

    chunk_size : int
        Number of bytes read at a time. Chunked reading prevents
        loading large files entirely into memory.

    Returns
    -------
    str or None
        SHA256 hash string if successful, otherwise None if an error occurs.
    """

    sha256 = hashlib.sha256()

    try:
        # Open the file in binary mode
        with open(file_path, "rb") as f:

            # Read the file in chunks to keep memory usage low
            while chunk := f.read(chunk_size):
                sha256.update(chunk)

        return sha256.hexdigest()

    except Exception:
        # If hashing fails (permissions, corruption etc.)
        return None


def find_matching_files(source):
    """
    Recursively locate all files that match *_FINAL.docx.

    We use os.walk() because it is efficient and reliable for
    traversing deep directory structures.

    Parameters
    ----------
    source : Path
        Root directory where scanning should begin.

    Returns
    -------
    list
        List of full file paths matching the required pattern.
    """

    matches = []

    # Walk through every folder and subfolder
    for root, _, files in os.walk(source):

        # Check every file in the current directory
        for file in files:

            # Case-insensitive check for filenames ending in "_FINAL.docx"
            if file.lower().endswith("_final.docx"):
                matches.append(Path(root) / file)

    return matches


def process_file(file_path, destination, existing_hashes):
    """
    Handle hashing and copying of a single file.

    This function is executed by worker threads so that
    multiple files can be processed simultaneously.

    Workflow
    --------
    1. Generate SHA256 hash
    2. Check if the file already exists (duplicate detection)
    3. Copy the file if unique
    4. Handle filename collisions

    Parameters
    ----------
    file_path : Path
        File to process.

    destination : Path
        Output directory where files should be copied.

    existing_hashes : set
        Shared set storing hashes of already copied files.

    Returns
    -------
    tuple
        (status, file_path)

        status values:
        - "copied"
        - "duplicate"
        - "error"
    """

    # Calculate hash fingerprint
    file_hash = calculate_hash(file_path)

    # If hashing failed, mark as error
    if file_hash is None:
        return "error", file_path

    # Check if the file is already known
    if file_hash in existing_hashes:
        return "duplicate", file_path

    # Determine destination file path
    dest_file = destination / file_path.name

    # If a file with the same name already exists in the destination,
    # append a numeric suffix to avoid overwriting.
    counter = 1
    while dest_file.exists():
        dest_file = destination / f"{file_path.stem}_{counter}{file_path.suffix}"
        counter += 1

    # Copy the file while preserving timestamps and metadata
    shutil.copy2(file_path, dest_file)

    # Record the hash to prevent future duplicates
    existing_hashes.add(file_hash)

    return "copied", file_path


def main(source_folder):
    """
    Main execution function.

    Responsibilities
    ----------------
    1. Validate source directory
    2. Discover matching files
    3. Initialise multithreading
    4. Track progress and statistics
    5. Print final results
    """

    # Convert source folder into a canonical absolute path
    source_folder = Path(source_folder).resolve()

    # Create the destination directory where results will be stored
    destination = Path.cwd() / DEST_FOLDER_NAME
    destination.mkdir(exist_ok=True)

    print(f"\nScanning source directory:\n{source_folder}\n")

    # Find candidate files
    files = find_matching_files(source_folder)

    if not files:
        print("No matching *_FINAL.docx files found.")
        return

    print(f"Found {len(files)} candidate files.\n")

    # Determine number of CPU cores available
    cpu_count = multiprocessing.cpu_count()

    # Use 75% of cores to avoid saturating the machine
    workers = max(1, int(cpu_count * 0.75))

    print(f"Using {workers} threads (75% of {cpu_count} CPU cores)\n")

    # Set used to track hashes of files already copied
    existing_hashes = set()

    # Statistics counters
    copied = 0
    duplicates = 0
    errors = 0

    # Thread pool allows multiple files to be processed concurrently
    with ThreadPoolExecutor(max_workers=workers) as executor:

        # Submit each file to the thread pool
        futures = [
            executor.submit(process_file, file, destination, existing_hashes)
            for file in files
        ]

        # tqdm provides a live progress bar
        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Processing files"
        ):

            status, _ = future.result()

            # Update counters based on result
            if status == "copied":
                copied += 1
            elif status == "duplicate":
                duplicates += 1
            else:
                errors += 1

    # Print final summary
    print("\n-------- Summary --------")
    print(f"Files copied       : {copied}")
    print(f"Duplicates skipped : {duplicates}")
    print(f"Errors             : {errors}")
    print(f"\nOutput folder: {destination}")
    print("-------------------------\n")


if __name__ == "__main__":

    # Ask the user which directory should be scanned
    source = input("Enter folder to scan: ").strip()

    # Basic validation to ensure a real directory was provided
    if not os.path.isdir(source):
        print("Invalid directory.")
    else:
        main(source)