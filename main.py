import requests
from bs4 import BeautifulSoup
import csv

# Define constants
RFC_INDEX_URL = "https://www.rfc-editor.org/search/rfc_search_detail.php?stream_name=IETF&page=All"
OUTPUT_FILE = "tls_related_rfc.csv"

def fetch_rfc_index():
    """Fetch the RFC index page."""
    response = requests.get(RFC_INDEX_URL)
    response.raise_for_status()
    return response.text

def parse_rfc_results(html_content):
    """Parse RFC results from the correct table."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Locate the correct table (we dont need the searchbar table)
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

        # Filter for relevant RFCs
        if "TLS" in title.upper() and "PROPOSED STANDARD" in status.upper() and "CHANGED FROM PROPOSED STANDARD" not in status.upper():
            rfc_list.append({
                "RFC Number": rfc_number,
                "Title": title,
                "URL": f"https://www.rfc-editor.org/info/{rfc_number.lower()}",
                "Publication Date": pub_date,
                "Status": status
            })

    print(f"Extracted {len(rfc_list)} relevant RFCs.")
    return rfc_list



def save_to_csv(rfc_list):
    """Save RFC list to a CSV file."""
    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["RFC Number", "Title", "URL", "Publication Date", "Status", "Obsoleted By"])
        writer.writeheader()
        writer.writerows(rfc_list)

def main():
    """Main function to execute the script."""
    print("Fetching RFC index...")
    html_content = fetch_rfc_index()

    print("Parsing RFC data...")
    rfc_list = parse_rfc_results(html_content)

    print(f"Found {len(rfc_list)} relevant RFCs. Saving to CSV...")
    save_to_csv(rfc_list)
    print(f"Data saved to {OUTPUT_FILE}.")

if __name__ == "__main__":
    main()
