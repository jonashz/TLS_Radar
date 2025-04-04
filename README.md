# RFC Extraction Script

This script is designed to extract and monitor RFCs related to TLS from the IETF RFC Editor website. It focuses on RFCs that are categorized as either Proposed Standard (excluding those labeled as "Changed from Proposed Standard") or Internet Standard. The goal is to provide users with an up-to-date list of relevant RFCs and to track any changes over time.

## Features

### Web Scraping:
- Retrieves the complete RFC index from the RFC Editor website.

### Filtering:
- Extracts only those RFCs whose titles contain "TLS" and whose status is either "Proposed Standard" or "Internet Standard".

### CSV Output:
- Saves the filtered RFC data into a CSV file (tls_related_rfc.csv).

### Change Detection:
- Compares the newly fetched data with a previously saved CSV (if available) and generates a differences file (tls_related_rfc_changes.csv) to highlight any additions, modifications, or removals.

## Requirements

- Python 3.x
- requests
- beautifulsoup4
- csv (included in Python’s standard library)

## Installation

You can install the required libraries using pip:

```bash
pip install requests beautifulsoup4
```

## Usage

1. Ensure Dependencies are Installed:
   - Verify that you have Python 3.x installed along with the necessary libraries.
2. Run the Script:
   - Execute the script from the command line:

```bash
python main.py
```

### Output Files

- tls_related_rfc.csv: Contains the current list of extracted RFCs.
- tls_related_rfc_changes.csv: Contains the differences between the current extraction and the previous run (if a previous file exists).

## Customization

- Target URL:
  - If you need to adjust the source of the RFC index, modify the RFC_INDEX_URL variable in the script.
- Filtering Criteria:
  - The filtering logic is implemented in the parse_rfc_results function. Adjust it as needed.



