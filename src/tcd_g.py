from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import github
import re
from openpyxl.styles import Font, Alignment

# Function to extract test case details
def extract_tc_details(h1_tags, a, sheet):
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
                    testcase_name = testcase_match.group(1)
                else:
                    testcase_name = ''

                if a == 0:
                    test_plan = "Core Test Case"
                else:
                    test_plan = "App Test Case"

                # Modify row_values list to include "Test case name"
                row_values = [cluster_name, head_text, testcase_name, test_plan]
                sheet.append(row_values)

                print(f"Fetching details for Test Case: {testcase_name}")

# Load existing JSON data or create an empty dictionary if it doesn't exist
json_filename = 'TC_Summary.json'
try:
    with open(json_filename, 'r') as json_file:
        existing_data = json.load(json_file)
except FileNotFoundError:
    existing_data = {}

# GitHub and Google Sheets setup
github_token = os.environ.get("GITHUB_TOKEN")
service_account_json = os.environ.get("TC_SUMMARY_SERVICE_ACCOUNT_JSON")

g = github.Github(github_token)
service_account_json_dict = json.loads(service_account_json)
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_json_dict, scope)
gc = gspread.authorize(credentials)

# Define the Google Sheets workbook and sheet
workbook_name = 'Matter_CHIP_Verification_Step_Document'
sheet1_name = 'TC_Summary_List'
changes_sheet_name = 'TC_Change_List'

try:
    workbook = gc.open(workbook_name)
    sheet1 = workbook.worksheet(sheet1_name)
    changes_sheet = workbook.worksheet(changes_sheet_name)
    print(f"Existing workbook '{workbook_name}' and sheets '{sheet1_name}' and '{changes_sheet_name}' loaded.")
except gspread.SpreadsheetNotFound:
    workbook = gc.create(workbook_name)
    sheet1 = workbook.add_worksheet(title=sheet1_name, rows="100", cols="10")
    changes_sheet = workbook.add_worksheet(title=changes_sheet_name, rows="100", cols="10")
    print(f"New workbook '{workbook_name}' created with sheets '{sheet1_name}' and '{changes_sheet_name}'.")

# Parse 'app' HTML
print("^" * 40)
print("Parsing 'app' HTML...")
app_html = 'Docs/Test_Plan_HTML/allclusters.html'
with open(app_html, encoding='utf-8') as f1:
    soup1 = BeautifulSoup(f1, 'html.parser')
    h1_tags1 = soup1.find_all('h1', {'id': True})
    extract_tc_details(h1_tags1, 1, sheet1)  # Pass initial row_number and sheet1

# Parse 'main' HTML
print("^" * 40)
print("Parsing 'main' HTML...")
main_html = 'Docs/Test_Plan_HTML/index.html'
with open(main_html, encoding='utf-8') as f2:
    soup2 = BeautifulSoup(f2, 'html.parser')
    h1_tags2 = soup2.find_all('h1', {'id': True})
    extract_tc_details(h1_tags2, 0, sheet1)  # Pass the updated row_number and sheet1

# Compare the current data with existing data to identify added and removed test cases
current_data = {}

for row in sheet1.get_all_values()[1:]:
    cluster_name, head_text, testcase_name, test_plan = row

    if cluster_name not in current_data:
        current_data[cluster_name] = []

    current_data[cluster_name].append({'Head Text': head_text, 'Test Case Name': testcase_name, 'Test Plan': test_plan})

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
changes_sheet_name = 'TC_Changes'
if changes_sheet_name not in workbook.worksheets():
    changes_sheet = workbook.add_worksheet(title=changes_sheet_name, rows="100", cols="10")

    changes_headers = ['Date of Run', 'Cluster Name', 'Head Text', 'Test Case Name', 'Test Plan', 'Change Type']
    changes_sheet.insert_row(changes_headers, 1)

    print(f"Sheet '{changes_sheet_name}' created.")
else:
    print(f"Sheet '{changes_sheet_name}' already exists.")

# Get the current date (without time)
current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Add the added and removed test cases to the "TC_Changes" sheet
rows_to_insert = []

for cluster_name, cluster_data_list in added_test_cases.items():
    for cluster_data in cluster_data_list:
        rows_to_insert.append([current_date, cluster_name, cluster_data['Head Text'], cluster_data['Test Case Name'], cluster_data['Test Plan'], 'ADDED'])

for cluster_name, cluster_data_list in removed_test_cases.items():
    for cluster_data in cluster_data_list:
        rows_to_insert.append([current_date, cluster_name, cluster_data['Head Text'], cluster_data['Test Case Name'], cluster_data['Test Plan'], 'REMOVED'])

# Check if there are no changes and append a row indicating "No change"
if not rows_to_insert:
    no_change_row = [current_date, '-', '-', '-', '-', 'NO CHANGE']
    changes_sheet.append_row(no_change_row)

# Insert all rows at once
for row_values in rows_to_insert:
    changes_sheet.append_row(row_values)

# Save the workbook (Note: Google Sheets are saved automatically)
# Update the JSON file with the latest data, excluding the history
with open(json_filename, 'w') as json_file:
    json.dump(current_data, json_file, indent=4)

print(f"Process completed. Google Sheets workbook updated and '{json_filename}' updated.")
