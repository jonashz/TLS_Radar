import os
import requests
from bs4 import BeautifulSoup
import csv

# Define constants
RFC_INDEX_URL = "https://www.rfc-editor.org/search/rfc_search_detail.php?stream_name=IETF&page=All"
OUTPUT_FILE = "tls_related_rfc.csv"
DIFF_FILE = "tls_related_rfc_changes.csv"

def fetch_rfc_index():
    """Fetch the RFC index page."""
    response = requests.get(RFC_INDEX_URL)
    response.raise_for_status()
    return response.text

def parse_rfc_results(html_content):
    """Parse RFC results from the correct table."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Locate the correct table (we don't need the searchbar table)
    table = soup.find("table", {"class": "gridtable"})
    if not table:
        print("RFC results table not found.")
        return []

    rfc_list = []
    rows = table.find_all("tr")[1:]  # Skip header

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 7:
            continue

        # Extract data from cells
        rfc_number = cells[0].text.strip()  # "Number" column
        title = cells[2].text.strip()       # "Title" column
        pub_date = cells[4].text.strip()    # "Date" column
        status = cells[6].text.strip()      # "Status" column

        # Filter for relevant RFCs with TLS in title and either Proposed Standard or Internet Standard status
        if ("TLS" in title.upper() and
           (
             ("PROPOSED STANDARD" in status.upper() and "CHANGED FROM PROPOSED STANDARD" not in status.upper()) or
             ("INTERNET STANDARD" in status.upper())
           )):
            rfc_list.append({
                "RFC Number": rfc_number,
                "Title": title,
                "URL": f"https://www.rfc-editor.org/info/{rfc_number.lower()}",
                "Publication Date": pub_date,
                "Status": status,
                "Obsoleted By": ""  # Included for consistency with CSV header
            })

    print(f"Extracted {len(rfc_list)} relevant RFCs.")
    return rfc_list

def save_to_csv(rfc_list, filename=OUTPUT_FILE):
    """Save RFC list to a CSV file."""
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        fieldnames = ["RFC Number", "Title", "URL", "Publication Date", "Status", "Obsoleted By"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rfc_list)
    print(f"Data saved to {filename}.")

def read_csv(filename):
    """Read CSV file and return a list of dictionaries."""
    if not os.path.exists(filename):
        return None
    with open(filename, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)

def compare_data(old_list, new_list):
    """
    Compare two lists of dictionaries keyed by 'RFC Number'
    and return a list of differences with a "Change Type" field.
    """
    diff = []
    # Create dictionaries keyed by RFC Number
    old_dict = { row["RFC Number"]: row for row in old_list } if old_list else {}
    new_dict = { row["RFC Number"]: row for row in new_list }

    # Check for added or modified rows.
    for rfc, new_row in new_dict.items():
        if rfc not in old_dict:
            # New row added
            new_row_copy = new_row.copy()
            new_row_copy["Change Type"] = "Added"
            diff.append(new_row_copy)
        else:
            old_row = old_dict[rfc]
            # Compare all fields (ignoring potential differences in formatting)
            fields = ["RFC Number", "Title", "URL", "Publication Date", "Status", "Obsoleted By"]
            if any(new_row.get(field, "") != old_row.get(field, "") for field in fields):
                new_row_copy = new_row.copy()
                new_row_copy["Change Type"] = "Modified"
                diff.append(new_row_copy)

    # Check for removed rows.
    for rfc, old_row in old_dict.items():
        if rfc not in new_dict:
            old_row_copy = old_row.copy()
            old_row_copy["Change Type"] = "Removed"
            diff.append(old_row_copy)

    return diff

def save_diff(diff_list, filename=DIFF_FILE):
    """Save the differences to a CSV file with an extra 'Change Type' column."""
    if not diff_list:
        print("No differences found; no diff file created.")
        return
    fieldnames = ["Change Type", "RFC Number", "Title", "URL", "Publication Date", "Status", "Obsoleted By"]
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(diff_list)
    print(f"Diff file saved to {filename} with {len(diff_list)} changes.")

def main():
    # Read old data (if exists) before generating new data
    old_data = read_csv(OUTPUT_FILE)
    
    print("Fetching RFC index...")
    html_content = fetch_rfc_index()

    print("Parsing RFC data...")
    new_rfc_list = parse_rfc_results(html_content)

    print(f"Found {len(new_rfc_list)} relevant RFCs. Saving to CSV...")
    save_to_csv(new_rfc_list)

    # Compare new data with old data and output the differences
    if old_data is not None:
        diff = compare_data(old_data, new_rfc_list)
        save_diff(diff)
    else:
        print("No previous CSV file found; skipping diff generation.")

if __name__ == "__main__":
    main()
