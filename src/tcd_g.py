from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting import set_row_height, set_column_width
from gspread_formatting import set_horizontal_alignment, set_vertical_alignment
from gspread_formatting import format_cell_ranges
import re
import json
import os
from datetime import datetime

print("Process Starts")

# Load existing JSON data or create an empty dictionary if it doesn't exist
json_filename = 'src/TC_Summary.json'
try:
    with open(json_filename, 'r') as json_file:
        existing_data = json.load(json_file)
except FileNotFoundError:
    existing_data = {}

# Google Sheets credentials
service_account_json = os.environ.get("SERVICE_ACCOUNT_JSON")
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(service_account_json, scope)
client = gspread.authorize(credentials)

# Define the Google Sheets workbook
workbook_title = 'Matter_Chip_Verification_Step_Document'
try:
    workbook = client.open(workbook_title)
    print(f"Existing workbook '{workbook_title}' opened.")
except gspread.SpreadsheetNotFound:
    workbook = client.create(workbook_title)
    print(f"New workbook '{workbook_title}' created.")

# Check if 'All_TC_Details' sheet exists, and if not, create it
sheet1_name = 'TC_Summary_List'
try:
    sheet1 = workbook.add_worksheet(title=sheet1_name, rows=100, cols=10)
    print(f"Sheet '{sheet1_name}' created.")
except gspread.exceptions.WorksheetNotFound:
    sheet1 = workbook.worksheet(sheet1_name)
    sheet1.clear()
    print(f"Sheet '{sheet1_name}' already exists. Existing data cleared.")

# Define column headers
headers = ['S.No', 'Cluster Name', 'Test Case Name', 'Test Case ID', 'Test Plan']

# Add headers to the first row and set formatting
header_format = {
    "textFormat": {"bold": True},
    "horizontalAlignment": "CENTER",
    "verticalAlignment": "MIDDLE"
}
sheet1.insert_row(headers, 1)
format_cell_ranges(sheet1, ['A1:E1'], header_format)

print(f"Sheet '{sheet1_name}' headers set.")

# Define a function to extract test case details
def extract_tc_details(h1_tags, a, row_number, sheet):
    for i, h1_tag in enumerate(h1_tags):
        h1 = h1_tag.text
        cluster_name = h1.replace(' Cluster Test Plan', '') \
            .replace(' Cluster TestPlan', '') \
            .replace(' Cluster', '') \
            .replace(' cluster', '') \
            .replace(' Test Plan', '')

        print("-" * 40)
        print(f"Fetching details for cluster: {cluster_name}")

        first_h1 = h1_tag
        if i == (len(h1_tags) - 1):
            second_h1 = False
        else:
            second_h1 = h1_tags[i + 1]

        h5_tags = first_h1.find_all_next('h5', {'id': lambda x: x and x.startswith('_test_procedure')})
        result = []

        if second_h1:
            for h5_tag in h5_tags:
                if h5_tag.find_previous('h1') == first_h1 and h5_tag.find_next('h1') == second_h1:
                    result.append(h5_tag)
        else:
            for h5_tag in h5_tags:
                if h5_tag.find_previous('h1') == first_h1:
                    result.append(h5_tag)

        if result:
            for j in range(len(result)):
                h4_tag = result[j].find_previous('h4')
                head_text_match = re.search(r'\[(.*?)\]\s*(.*)', h4_tag.text)
                if head_text_match:
                    head_text = '[' + head_text_match.group(1) + '] ' + head_text_match.group(2)
                else:
                    head_text = ''

                # Extract the "Test case name" using regular expressions
                testcase_match = re.search(r'\[(.*?)\]', head_text)
                if testcase_match:
                    testcase_name = testcase_match.group(1)  # Extract the first group (inside parentheses)
                else:
                    testcase_name = ''

                if a == 0:
                    test_plan = "Core Test Case"
                else:
                    test_plan = "App Test Case"

                # Modify row_values list to include "Test case name"
                row_values = [row_number, cluster_name, head_text, testcase_name, test_plan]
                sheet.insert_row(row_values, row_number + 1)

                print(f"Fetching details for Test Case: {testcase_name}")

                # Increment row_number for each new row
                row_number += 1

# Parse 'app' HTML
print("^" * 40)
print("Parsing 'app' HTML...")
app_html = 'Docs/Test_Plan_HTML/allclusters.html'
with open(app_html, encoding='utf-8') as f1:
    soup1 = BeautifulSoup(f1, 'html.parser')
    h1_tags1 = soup1.find_all('h1', {'id': True})
    extract_tc_details(h1_tags1, 1, 1, sheet1)  # Pass initial row_number and sheet1

# Calculate the next row_number after parsing the first HTML
row_number = sheet1.row_count - 1

# Parse 'main' HTML
print("^" * 40)
print("Parsing 'main' HTML...")
main_html = 'Docs/Test_Plan_HTML/index.html'
with open(main_html, encoding='utf-8') as f2:
    soup2 = BeautifulSoup(f2, 'html.parser')
    h1_tags2 = soup2.find_all('h1', {'id': True})
    extract_tc_details(h1_tags2, 0, row_number, sheet1)  # Pass the updated row_number and sheet1

# Set formatting for the entire sheet
format_cell_ranges(sheet1, ['A1:E' + str(sheet1.row_count)], {"textFormat": {"fontFamily": "Times New Roman"}})
set_vertical_alignment(sheet1, 'MIDDLE')
set_horizontal_alignment(sheet1, 'CENTER')

# Set alignment to center for columns A and E
for column_letter in ['A', 'E']:
    format_cell_ranges(sheet1, [column_letter + '2:' + column_letter + str(sheet1.row_count)],
                       {"horizontalAlignment": "CENTER"})

# Set column widths
column_widths = {'A': 5, 'B': 30, 'C': 100, 'D': 25, 'E': 15}
for column, width in column_widths.items():
    set_column_width(sheet1, column, width)

# Compare the current data with existing data to identify added and removed test cases
current_data = {}

for row in sheet1.get_all_records()[1:]:
    cluster_name = row['Cluster Name'] if 'Cluster Name' in row else None
    test_case_name = row['Test Case Name'] if 'Test Case Name' in row else None
    test_case_id = row['Test Case ID'] if 'Test Case ID' in row else None
    test_plan = row['Test Plan'] if 'Test Plan' in row else None

    # Check if the cluster_name is already in the dictionary
    if cluster_name not in current_data:
        current_data[cluster_name] = []

    # Append the test case details to the list under the cluster_name
    current_data[cluster_name].append({'Test Case Name': test_case_name, 'Test Case ID': test_case_id, 'Test Plan': test_plan})

# Print a message indicating that the JSON check is done
print("JSON check completed. Added and removed test cases identified.")

# Define added_test_cases and removed_test_cases before the check
added_test_cases = {}
removed_test_cases = {}

# Iterate through existing_data and current_data to identify added and removed test cases
for cluster_name, current_tests in current_data.items():
    existing_tests = existing_data.get(cluster_name, [])

    added_tests = [test for test in current_tests if test not in existing_tests]
    removed_tests = [test for test in existing_tests if test not in current_tests]

    if added_tests:
        added_test_cases[cluster_name] = added_tests
    if removed_tests:
        removed_test_cases[cluster_name] = removed_tests

# Check if 'TC_Changes' sheet exists, and if not, create it
changes_sheet_name = 'TC_Changes_List'
try:
    changes_sheet = workbook.add_worksheet(title=changes_sheet_name, rows=100, cols=10)
    print(f"Sheet '{changes_sheet_name}' created.")
except gspread.exceptions.WorksheetNotFound:
    changes_sheet = workbook.worksheet(changes_sheet_name)
    changes_sheet.clear()
    print(f"Sheet '{changes_sheet_name}' already exists.")

# Define changes headers
changes_headers = ['Date of Run', 'Cluster Name', 'Test Case Name', 'Test Case ID', 'Test Plan', 'Change Type']

# Add headers to the first row and set formatting
changes_sheet.insert_row(changes_headers, 1)
format_cell_ranges(changes_sheet, ['A1:F1'], header_format)

print(f"Sheet '{changes_sheet_name}' headers set.")

# Get the current date (without time)
current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Add the added and removed test cases to the "TC_Changes" sheet
rows_to_insert = []

for cluster_name, cluster_data_list in added_test_cases.items():
    for cluster_data in cluster_data_list:
        rows_to_insert.append([current_date, cluster_name, cluster_data['Test Case Name'], cluster_data['Test Case ID'], cluster_data['Test Plan'], 'ADDED'])

for cluster_name, cluster_data_list in removed_test_cases.items():
    for cluster_data in cluster_data_list:
        rows_to_insert.append([current_date, cluster_name, cluster_data['Test Case Name'], cluster_data['Test Case ID'], cluster_data['Test Plan'], 'REMOVED'])

# Check if there are no changes and append a row indicating "No change"
if not rows_to_insert:
    no_change_row = [current_date, '-', '-', '-', '-', 'NO CHANGE']
    changes_sheet.append_row(no_change_row)
    format_cell_ranges(changes_sheet, ['A' + str(changes_sheet.row_count) + ':F' + str(changes_sheet.row_count)],
                       {"horizontalAlignment": "CENTER", "verticalAlignment": "MIDDLE"})

# Insert all rows at once
changes_sheet.insert_rows(rows_to_insert, 2)

# Set alignment to center for columns A, E, and F
for column_letter in ['A', 'E', 'F']:
    format_cell_ranges(changes_sheet, [column_letter + '2:' + column_letter + str(changes_sheet.row_count)],
                       {"horizontalAlignment": "CENTER", "verticalAlignment": "MIDDLE"})

# Set column widths for 'TC_Changes' sheet
column_widths_changes = {'A': 17, 'B': 30, 'C': 80, 'D': 25, 'E': 15, 'F': 15}
for column, width in column_widths_changes.items():
    set_column_width(changes_sheet, column, width)

# Save the workbook
print("Saving Google Sheets workbook...")
workbook.batch_update({})
print(f"Process completed. Google Sheets workbook saved.")
