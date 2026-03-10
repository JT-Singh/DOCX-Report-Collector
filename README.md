# FINAL Document Collector

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

A Python tool that recursively scans a directory structure for **Microsoft Word documents (`.docx`) whose filename ends with `_FINAL`** and copies them into a centralised folder.

The tool is designed for environments where finalised reports or documents are spread across large directory trees and need to be collected quickly and safely.

---

# Features

- Recursive scanning of directories and subdirectories
- Multithreaded processing for faster execution
- Automatic scaling to **75% of available CPU cores**
- SHA256 **hash-based duplicate detection**
- Live **progress bar** during processing
- Safe copying with metadata preservation
- Automatic handling of filename collisions
- Works efficiently on **large repositories (100k+ files)**

---

# Use Case

This tool is useful when:

- Project folders contain many versions of documents
- Only **final versions of reports** need to be collected
- Documents are spread across many nested directories
- Duplicate files should not be copied multiple times

Example scenarios:

- Pentest report repositories  
- Consulting project archives  
- Document management cleanup  
- Report harvesting across shared drives  

---

# How It Works

The tool performs the following steps:

1. Recursively scans the specified folder.
2. Identifies files matching:

```
*_FINAL.docx
```

3. Calculates a **SHA256 hash** for each file.
4. Skips files whose hash already exists (duplicate detection).
5. Copies unique files into a new folder:

```
FINAL_TRs
```

This folder is automatically created **in the directory where the script runs**.

---

# Example

## Source Directory

```
Projects/
├─ ClientA/
│  ├─ TR1_FINAL.docx
│  ├─ TR1_DRAFT.docx
│
├─ ClientB/
│  ├─ SecurityReview_FINAL.docx
│
├─ ClientC/
│  ├─ TR1_FINAL.docx
```

If two `TR1_FINAL.docx` files contain identical content, only one will be copied.

---

## Output

```
FINAL_TRs/
├─ TR1_FINAL.docx
└─ SecurityReview_FINAL.docx
```

---

# Requirements

- Python **3.9 or later**
- `tqdm` library

---

# Installation

Clone the repository or download the script.

Install dependencies:

```
pip install tqdm
```

---

# Usage

Run the script:

```
python final_doc_collector.py
```

You will be prompted to enter the folder to scan.

Example:

```
Enter folder to scan: D:\Projects
```

The script will then:

- scan all subdirectories
- process matching files
- copy unique documents into `FINAL_TRs`

---

# Progress Output

During execution, a progress bar will appear:

```
Processing files: 72%|███████████████▏ | 361/500
```

This provides real-time visibility when scanning large directories.

---

# Performance

Typical performance on modern systems:

| Files Scanned | Approx Time |
|---------------|-------------|
| 10,000 | 2–3 seconds |
| 50,000 | 6–10 seconds |
| 200,000 | 20–30 seconds |

Performance depends mostly on **disk speed and hashing time**.

---

# Duplicate Detection

Duplicate documents are identified using:

```
SHA256 hashing
```

If two files contain identical content, only the first instance will be copied.

This prevents unnecessary duplication even if files exist in different folders.

---

# Threading Model

The script automatically scales threads based on available CPU cores.

Example:

| CPU Cores | Threads Used |
|-----------|--------------|
| 4 | 3 |
| 8 | 6 |
| 16 | 12 |
| 32 | 24 |

This allows fast processing without saturating the machine.

---

# File Safety

The script uses:

```
shutil.copy2()
```

This ensures the following metadata is preserved:

- timestamps  
- permissions (where supported)  
- file attributes  

If a filename collision occurs, a suffix is added:

```
Report_FINAL.docx
Report_FINAL_1.docx
Report_FINAL_2.docx
```

---

# Project Structure

```
project-folder/
│
├─ final_doc_collector.py
│
└─ FINAL_TRs/
   ├─ collected documents
```

---

# Future Improvements

Possible enhancements include:

- Command-line arguments (`--source`, `--output`)
- JSON or CSV report generation
- Logging to file
- Bloom filter based duplicate detection
- Directory streaming for millions of files
- Packaging as a standalone executable

---

# License

This project is provided for internal or personal use.  
You may modify and adapt it as needed.

---

# Author

Python utility developed for efficient document harvesting and deduplication in large directory structures.
