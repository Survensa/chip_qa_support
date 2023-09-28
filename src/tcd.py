from bs4 import BeautifulSoup
import openpyxl
from openpyxl.styles import Font, Alignment
import re

print("Process Starts")

# Create an Excel workbook and define the filename
filename = 'Docs/TC_Summary.xlsx'

app_html = 'Docs/Test_Plan_HTML/allclusters.html'
main_html = 'Docs/Test_Plan_HTML/index.html'

# Load the existing workbook
workbook = openpyxl.load_workbook(filename)
sheet1 = workbook['All_TC_Details']

# Create a new sheet for changes
changes_sheet = workbook.create_sheet(title="Changes")

# Define column headers for the changes sheet
changes_headers = ['S.No', 'Cluster Name', 'Test Case Name', 'Test Case ID', 'Test Plan', 'Change Type']
for col_num, header in enumerate(changes_headers, 1):
    cell = changes_sheet.cell(row=1, column=col_num, value=header)
    cell.font = Font(name='Times New Roman', bold=True)
    cell.alignment = Alignment(horizontal='center', vertical='center')

# Set header row alignment to center for the changes sheet
for cell in changes_sheet[1]:
    cell.alignment = Alignment(horizontal='center', vertical='center')

# Function to find changes and append them to the changes sheet
def find_and_append_changes(html_tags, a):
    row_number = sheet1.max_row + 1
    for i, h1_tag in enumerate(html_tags):
        h1 = h1_tag.text
        cluster_name = h1.replace('Cluster Test Plan', '')

        first_h1 = h1_tag
        if i == (len(html_tags) - 1):
            second_h1 = False
        else:
            second_h1 = html_tags[i + 1]

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

                test_plan = "Core Test Case" if a == 0 else "App Test Case"

                # Check if the row already exists in the All_TC_Details sheet
                existing_row = None
                for row in sheet1.iter_rows(min_row=2, max_row=sheet1.max_row, min_col=4, max_col=4):
                    if row[0].value == testcase_name:
                        existing_row = row[0].row
                        break

                if existing_row:
                    # Row exists, compare values
                    existing_values = [cell.value for cell in sheet1[existing_row]]
                    new_values = [row_number, cluster_name, head_text, testcase_name, test_plan]

                    if existing_values != new_values:
                        # Values are different, append to the changes sheet as modified
                        changes_sheet.append(new_values + ["Modified"])
                else:
                    # Row doesn't exist, append to the changes sheet as added
                    changes_sheet.append([row_number, cluster_name, head_text, testcase_name, test_plan, "Added"])

                # Increment row_number for each new row
                row_number += 1

# Parse 'app' HTML
print("^" * 40)
print("Parsing 'app' HTML...")
with open(app_html, encoding='utf-8') as f1:
    soup1 = BeautifulSoup(f1, 'html.parser')
    h1_tags1 = soup1.find_all('h1', {'id': True})
    find_and_append_changes(h1_tags1, 1)

# Parse 'main' HTML
print("^" * 40)
print("Parsing 'main' HTML...")
with open(main_html, encoding='utf-8') as f2:
    soup2 = BeautifulSoup(f2, 'html.parser')
    h1_tags2 = soup2.find_all('h1', {'id': True})
    find_and_append_changes(h1_tags2, 0)

# Identify removed items
for row in sheet1.iter_rows(min_row=2, max_row=sheet1.max_row, min_col=4, max_col=4):
    testcase_name = row[0].value
    if not any(testcase_name in h1_tag.text for h1_tag in h1_tags1 + h1_tags2):
        # Test case not found in HTML data, append to the changes sheet as removed
        changes_sheet.append([row[0].row, row[1].value, row[2].value, row[3].value, row[4].value, "Removed"])

# Set the font for the entire sheet to Times New Roman
for row in changes_sheet.iter_rows(min_row=2, max_row=changes_sheet.max_row, min_col=1, max_col=changes_sheet.max_column):
    for cell in row:
        cell.font = Font(name='Times New Roman')
        cell.alignment = Alignment(vertical='center')  # Center-align vertically

# Set alignment to center for columns A to F in the changes sheet
for column_letter in ['A', 'B', 'C', 'D', 'E', 'F']:
    for cell in changes_sheet[column_letter]:
        cell.alignment = Alignment(horizontal='center', vertical='center')

# Set column widths for the changes sheet
changes_column_widths = {'A': 5, 'B': 30, 'C': 100, 'D': 25, 'E': 15, 'F': 15}
for column, width in changes_column_widths.items():
    changes_sheet.column_dimensions[column].width = width

# Save the updated workbook
print("Saving Excel workbook with changes...")
workbook.save(filename)

print("Process completed. Excel file updated with changes.")
