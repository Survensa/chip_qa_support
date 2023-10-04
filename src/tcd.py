from bs4 import BeautifulSoup
import openpyxl
from openpyxl.styles import Font, Alignment
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

# Define the filename
filename = 'Docs/TC_Summary.xlsx'

# Check if the file exists
if os.path.exists(filename):
    # Load the existing workbook
    workbook = openpyxl.load_workbook(filename)
    print(f"Existing workbook '{filename}' loaded.")
else:
    # Create a new workbook if the file doesn't exist
    workbook = openpyxl.Workbook()
    print(f"New workbook '{filename}' created.")

# Check if 'All_TC_Details' sheet exists, and if not, create it
sheet1_name = 'All_TC_Details'
if sheet1_name not in workbook.sheetnames:
    sheet1 = workbook.create_sheet(title=sheet1_name)

    # Define column headers
    headers = ['S.No', 'Cluster Name', 'Test Case Name', 'Test Case ID', 'Test Plan']

    # Add headers to the first row and set the font to bold for the headings
    header_font = Font(name='Times New Roman', bold=True)
    for col_num, header in enumerate(headers, 1):
        cell = sheet1.cell(row=1, column=col_num, value=header)
        cell.font = header_font

    # Set header row alignment to center
    for cell in sheet1[1]:
        cell.alignment = Alignment(horizontal='center', vertical='center')

    print(f"Sheet '{sheet1_name}' created.")
else:
    sheet1 = workbook[sheet1_name]
    print(f"Sheet '{sheet1_name}' already exists.")

# Check if 'TC_Changes' sheet exists, and if not, create it
changes_sheet_name = 'TC_Changes'
if changes_sheet_name not in workbook.sheetnames:
    changes_sheet = workbook.create_sheet(title=changes_sheet_name)

    changes_headers = ['Date of Run', 'Cluster Name', 'Test Case Name', 'Test Case ID', 'Test Plan', 'Change Type']
    # Add headers to the first row and set the font to bold for the headings
    for col_num, header in enumerate(changes_headers, 1):
        cell = changes_sheet.cell(row=1, column=col_num, value=header)
        cell.font = Font(name='Times New Roman', bold=True)
        cell.alignment = Alignment(horizontal='center', vertical='center')

    print(f"Sheet '{changes_sheet_name}' created.")
else:
    changes_sheet = workbook[changes_sheet_name]
    print(f"Sheet '{changes_sheet_name}' already exists.")

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
                sheet.append(row_values)

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
row_number = sheet1.max_row + 0

# Parse 'main' HTML
print("^" * 40)
print("Parsing 'main' HTML...")
main_html = 'Docs/Test_Plan_HTML/index.html'
with open(main_html, encoding='utf-8') as f2:
    soup2 = BeautifulSoup(f2, 'html.parser')
    h1_tags2 = soup2.find_all('h1', {'id': True})
    extract_tc_details(h1_tags2, 0, row_number, sheet1)  # Pass the updated row_number and sheet1

# Set the font for the entire sheet to Times New Roman
for row in sheet1.iter_rows(min_row=2, max_row=sheet1.max_row, min_col=1, max_col=sheet1.max_column):
    for cell in row:
        cell.font = Font(name='Times New Roman')
        cell.alignment = Alignment(vertical='center')  # Center-align vertically

# Set alignment to center for columns A and E
for column_letter in ['A', 'E']:
    for cell in sheet1[column_letter]:
        cell.alignment = Alignment(horizontal='center', vertical='center')

# Set column widths
column_widths = {'A': 5, 'B': 30, 'C': 100, 'D': 25, 'E': 15}
for column, width in column_widths.items():
    sheet1.column_dimensions[column].width = width

# Compare the current data with existing data to identify added and removed test cases
current_data = {}

for row in sheet1.iter_rows(min_row=2, max_row=sheet1.max_row, min_col=2, max_col=5, values_only=True):
    cluster_name = row[0] if len(row) >= 0 else None
    test_case_name = row[1] if len(row) >= 1 else None
    test_case_id = row[2] if len(row) >= 2 else None
    test_plan = row[3] if len(row) >= 3 else None

    # Check if the cluster_name is already in the dictionary
    if cluster_name not in current_data:
        current_data[cluster_name] = []

    # Append the test case details to the list under the cluster_name
    current_data[cluster_name].append({'Test Case Name': test_case_name, 'Test Case ID': test_case_id, 'Test Plan': test_plan})

# Print a message indicating that the JSON check is done
print("JSON check completed. Added and removed test cases identified.")

# Save the current data as the new reference data in the JSON file
with open(json_filename, 'w') as json_file:
    json.dump(current_data, json_file, indent=4)

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

# Add the added and removed test cases to a new sheet named "TC_Changes"
if 'TC_Changes' not in workbook.sheetnames:
    changes_sheet = workbook.create_sheet(title="TC_Changes")

    changes_headers = ['Date of Run', 'Cluster Name', 'Test Case Name', 'Test Case ID', 'Test Plan', 'Change Type']
    # Add headers to the first row and set the font to bold for the headings
    for col_num, header in enumerate(changes_headers, 1):
        cell = changes_sheet.cell(row=1, column=col_num, value=header)
        cell.font = Font(name='Times New Roman', bold=True)
        cell.alignment = Alignment(horizontal='center', vertical='center')
else:
    changes_sheet = workbook['TC_Changes']

# Get the current date (without time)
current_date = datetime.now().strftime("%Y-%m-%d")

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
    changes_sheet.append([current_date, '', '', '', '', 'NO CHANGE'])

# Insert all rows at once
for row_values in rows_to_insert:
    changes_sheet.append(row_values)

# Save the workbook
print("Saving Excel workbook...")
workbook.save(filename)

# Update the JSON file with the latest data
with open(json_filename, 'w') as json_file:
    json.dump(current_data, json_file, indent=4)

print("Process completed. Excel file saved as 'TC_Summary.xlsx'.")
