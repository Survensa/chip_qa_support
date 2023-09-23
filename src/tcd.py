from bs4 import BeautifulSoup
import openpyxl
from openpyxl.styles import Font, Alignment
import re
import difflib

print("Process Starts")

# Define filenames and sheet names
filename = 'Docs/TC_Summary.xlsx'
app_html = 'Docs/Test_Plan_HTML/allclusters.html'
main_html = 'Docs/Test_Plan_HTML/index.html'
sheet_names = ["All_TC_Details", "The Line Changes"]

# Create an Excel workbook
workbook = openpyxl.Workbook()

# Create separate sheets for "All_TC_Details" and "The Line Changes"
sheets = {name: workbook.create_sheet(name) for name in sheet_names}

# Define column headers
headers = ['S.No', 'Cluster Name', 'Test Case Name', 'Test Case ID', 'Test Plan']

# Set the font for headers
header_font = Font(name='Times New Roman', bold=True)

# Populate headers for all sheets
for sheet in sheets.values():
    for col_num, header in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_num, value=header)
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')

# Function to extract test case details and check for line changes
def extract_tc_details(h1_tags, a, row_number, all_tc_sheet, line_changes_sheet, app_html_content, main_html_content):
    for i, h1_tag in enumerate(h1_tags):
        h1 = h1_tag.text
        cluster_name = h1.replace('Cluster Test Plan', '')

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
                if h5_tag.find_previous('h1') == first_h1:
                    if h5_tag.find_next('h1') == second_h1:
                        result.append(h5_tag)
        else:
            h5_tags = first_h1.find_all_next('h6', {'id': lambda x: x and x.startswith('_test_procedure')})
            for h5_tag in h5_tags:
                if h5_tag.find_previous('h1') == first_h1:
                    if h5_tag.find_next('h1') == second_h1:
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
                row_values = [row_number, cluster_name, head_text, testcase_name, test_plan]

                # Compare app and main HTML content
                line_changes = list(difflib.unified_diff(app_html_content, main_html_content, lineterm=''))

                # Check for line changes
                line_changed = any(line.startswith('-') or line.startswith('+') for line in line_changes)

                if line_changed:
                    line_changes_sheet.append(row_values)

                all_tc_sheet.append(row_values)

                print(f"Fetching details for Test Case: {testcase_name}")

                # Increment row_number for each new row
                row_number += 1

# Parse 'app' HTML
with open(app_html, encoding='utf-8') as f1:
    app_html_content = f1.readlines()
    soup1 = BeautifulSoup(''.join(app_html_content), 'html.parser')
    h1_tags1 = soup1.find_all('h1', {'id': True})
    main_html_content = ""  # Initialize main_html_content
    extract_tc_details(h1_tags1, 1, 1, sheets["All_TC_Details"], sheets["The Line Changes"], app_html_content, main_html_content)

# Calculate the next row_number after parsing the first HTML
row_number = sheets["All_TC_Details"].max_row + 1

# Parse 'main' HTML
with open(main_html, encoding='utf-8') as f2:
    main_html_content = f2.readlines()
    soup2 = BeautifulSoup(''.join(main_html_content), 'html.parser')
    h1_tags2 = soup2.find_all('h1', {'id': True})
    extract_tc_details(h1_tags2, 0, row_number, sheets["All_TC_Details"], sheets["The Line Changes"], app_html_content, main_html_content)

# Set the font and alignment for the entire sheets
for sheet in sheets.values():
    for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, min_col=1, max_col=sheet.max_column):
        for cell in row:
            cell.font = Font(name='Times New Roman')
            cell.alignment = Alignment(vertical='center')

# Set alignment to center for columns A and E for all sheets
columns_to_center = ['A', 'E']
for sheet in sheets.values():
    for column_letter in columns_to_center:
        for cell in sheet[column_letter]:
            cell.alignment = Alignment(horizontal='center', vertical='center')

# Set column widths for all sheets
column_widths = {'A': 5, 'B': 30, 'C': 100, 'D': 25, 'E': 15}
for sheet in sheets.values():
    for column, width in column_widths.items():
        sheet.column_dimensions[column].width = width

# Save the workbook
print("Saving Excel workbook...")
workbook.save(filename)

print("Process completed. Excel file saved as 'TC_Summary.xlsx'.")
