from bs4 import BeautifulSoup
import openpyxl
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment
import re
import datetime
import os
import pandas as pd
import json

today = datetime.date.today().strftime('%Y-%m-%d')
filename = "Docs/test_plan_change.xlsx"

print("Starting the script...")

# Load or create a workbook
try:
    workbook = load_workbook(filename)
    print("Workbook loaded successfully.")
except FileNotFoundError:
    workbook = openpyxl.Workbook()
    print("Workbook not found, creating a new one.")

sheet_names = workbook.sheetnames

app_html_path = 'Docs/Test_Plan_HTML/allclusters.html'
main_html_path = 'Docs/Test_Plan_HTML/index.html'

json_filename = 'src/TC_Summary_VS.json'

current_data = {}

def extract_test_case_id(test_case_header):
    match = re.search(r'\[(.*?)\]', test_case_header)
    if match:
        return match.group(1)
    return None

def extract_test_case(h4_tag, target_worksheet, test_plan):
    test_case_data = {}
    test_case_header_text = h4_tag.text
    target_worksheet.append([test_case_header_text])
    test_case_data["Test Case Name"] = test_case_header_text
    test_case_id = extract_test_case_id(test_case_header_text)
    test_case_data["Test Case ID"] = test_case_id
    test_case_data["Test Plan"] = test_plan
    target_worksheet.append([""])
    target_worksheet.append(["Purpose"])    
    purpose_heading_tag = h4_tag.find_next('h5', {'id': lambda x: x and x.startswith('_purpose')})
    purpose_paragraph = purpose_heading_tag.find_next('p')
    purpose_text = purpose_paragraph.text
    target_worksheet.append([purpose_text])
    test_case_data["Purpose"] = purpose_text
    print("Test Case Name:", test_case_header_text)
    print("Test Case ID:", test_case_id)
    print("Purpose:", purpose_text)
    target_worksheet.append([""])
    target_worksheet.append(["PICS"])
    test_case_data["PICS"] = []
    pics_heading_tag = h4_tag.find_next('h5', {'id': lambda x: x and x.startswith('_pics')})
    ul_div = pics_heading_tag.find_next('div', class_='ulist')
    
    if ul_div:
        pics_paragraphs = ul_div.find_all('p')
    else:
        pics_heading_tag = pics_heading_tag.find_next('h5', {'id': lambda x: x and x.startswith('_pics')})
        ul_div = pics_heading_tag.find_next('div', class_='ulist')
        pics_paragraphs = ul_div.find_all('p')
    
    for paragraph in pics_paragraphs:
        pics_text = paragraph.text
        target_worksheet.append([pics_text])
        test_case_data["PICS"].append(pics_text)
        print("PICS:", pics_text)
    
    target_worksheet.append([""])
    target_worksheet.append(["Pre-condition"])
    precondition_heading_tag = h4_tag.find_next('h5', {'id': lambda x: x and x.startswith('_preconditions')})
    
    if precondition_heading_tag:
        test_case_data["Pre-condition"] = {}
        table = precondition_heading_tag.find_next('table')
        
        if table:
            data_dict = create_df(table)
        
        if data_dict:
            test_case_data["Pre-condition"] = data_dict
            keys = list(data_dict.keys())
            target_worksheet.append(keys)
            print("Pre-condition Keys:", keys)
                   
            for i in range(len(list(data_dict.values())[0])):
                row_values = []
                for key, value in data_dict.items():
                    if i < len(value):
                        row_values.append(value[i])
                target_worksheet.append(row_values)
                print("Pre-condition Row Values:", row_values)
    else:
        target_worksheet.append(["nil"])
        test_case_data["Pre-condition"] = "Nil"
        print("Pre-condition: Nil")
    
    target_worksheet.append([""])
    target_worksheet.append(["Test Procedure"])
    h5_tags = h4_tag.find_next('h5', {'id': lambda x: x and x.startswith('_test_procedure')})
    
    if not h5_tags:
        h5_tags = h4_tag.find_next('h6', {'id': lambda x: x and x.startswith('_test_procedure')})
    
    table = h5_tags.find_next('table')
    data_dict = create_df(table)
    test_case_data["Test Procedure"] = data_dict
    keys = list(data_dict.keys())
    target_worksheet.append(keys)
    print("Test Procedure Keys:", keys)
    
    for i in range(len(list(data_dict.values())[0])):
        row_values = []
        for key, value in data_dict.items():
            if i < len(value):
                row_values.append(value[i])
        target_worksheet.append(row_values)
        print("Test Procedure Row Values:", row_values)
    
    target_worksheet.append([""])
    target_worksheet.append([""])
    target_worksheet.append([""])
    workbook.save(filename)

    return test_case_header_text, test_case_data

def extract_test_case_details(h1_tags, workbook, sheet1, current_data, test_plan_type):
    if test_plan_type == 0:
        test_plan_type_label = "App Test Case"
    else:
        test_plan_type_label = "Core Test Case"

    for i, h1_tag in enumerate(h1_tags):
        cluster_title = h1_tag.text
        cluster_name = cluster_title.replace(' Cluster Test Plan', '') \
            .replace(' Cluster TestPlan', '') \
            .replace(' Cluster', '') \
            .replace(' cluster', '') \
            .replace(' Test Plan', '')

        if cluster_title == "MCORE PICS Definition":
            continue
        if cluster_title == "Bulk Data Exchange Protocol Test Plan":
            sheet_name = "BR"
        else:
            h4_tag = h1_tag.find_next('h4', {'id': lambda x: x and x.startswith('_tc')})
            if h4_tag:
                h4 = h4_tag.text
                sheet_name = tc_id(h4)
            else:
                continue
            if sheet_name == "LOWPOWER":
                sheet_name = "MC"
            else:
                h4_tag = h1_tag.find_next('h5', {'id': lambda x: x and x.startswith('_tc')})
                h4 = h4_tag.text
                sheet_name = tc_id(h4)
                sh = re.search(r'-(.*?)-', test_case_id)
                sheet_name = sh.group(1)

        print(sheet_name)
        if sheet_name in workbook.sheetnames:
            workbook.remove(workbook[sheet_name])
            new_sheet = workbook.create_sheet(sheet_name, workbook.sheetnames.index(sheet_name))
        else:
            new_sheet = workbook.create_sheet(sheet_name)

        new_sheet.append([cluster_name])
        new_sheet.append([""])
        cluster_data = current_data[cluster_name] = []

        result = []
        if i == (len(h1_tags) - 1):
            second_h1 = False
        else:
            second_h1 = h1_tags[i + 1]

        h5_tags = h1_tag.find_all_next('h5', {'id': lambda x: x and x.startswith('_test_procedure')})

        if second_h1:
            for h5_tag in h5_tags:
                if h5_tag.find_previous('h1') == h1_tag:
                    if h5_tag.find_next('h1') == second_h1:
                        result.append(h5_tag)
        else:
            for h5_tag in h5_tags:
                if h5_tag.find_previous('h1') == h1_tag:
                    if h5_tag.find_next('h1') == second_h1:
                        result.append(h5_tag)

        if result:
            heads = []
            for h5_tag in result:
                h4_tag = h5_tag.find_previous('h4')
                test_case_name, test_case_data = extract_test_case(h4_tag, new_sheet, test_plan_type_label)
                cluster_data.append(test_case_data)
                heads.append(test_case_name)
        else:
            h6_tags = h1_tag.find_all_next('h6', {'id': lambda x: x and x.startswith('_test_procedure')})

            for h6_tag in h6_tags:
                if h6_tag.find_previous('h1') == h1_tag:
                    if h6_tag.find_next('h1') == second_h1:
                        result.append(h6_tag)

            heads = []
            for h6_tag in result:
                h5_tag = h6_tag.find_previous('h5')
                test_case_name, test_case_data = extract_test_case(h5_tag, new_sheet, test_plan_type_label)
                cluster_data.append(test_case_data)
                heads.append(test_case_name)

        column_widths = {'A': 10, 'B': 20, 'C': 20, 'D': 40, 'E': 50}
        if isinstance(new_sheet, list):
            print(f"{sheet_name} already exists")
        else:
            for column, width in column_widths.items():
                new_sheet.column_dimensions[column].width = width
        
        for j in range(len(result)):
            testcase = tc_id(heads[j])
            head_text_match = re.search(r'\[(.*?)\]\s*(.*)', heads[j])
            if head_text_match:
                tcname = '[' + head_text_match.group(1) + '] ' + head_text_match.group(2)
            else:
                tcname = ''

            n = sheet1.max_row
            value = [n, cluster_name, tcname, testcase, test_plan_type_label]
            sheet1.append(value)

def create_dataframe_from_table(html_table):
    rows = html_table.find_all('tr')
    data = []
    col_spans = []
    row_spans = []

    # Find colspan and rowspan attributes
    for row_index, row in enumerate(rows):
        cells = row.find_all(['th', 'td'])
        row_data = []
        for cell_index, cell in enumerate(cells):
            if cell.has_attr('colspan'):
                col_spans.append((row_index, cell_index, int(cell['colspan'])))
            if cell.has_attr('rowspan'):
                row_spans.append((row_index, cell_index, int(cell['rowspan'])))
            row_data.append(cell.get_text(strip=True))
        data.append(row_data)
    
    # Apply colspans to data
    for col_span in col_spans:
        row_index, cell_index, span_size = col_span
        for r in range(1, span_size):
            data[row_index].insert(cell_index + 1, '')

    # Apply rowspans to data
    for row_span in row_spans:
        row_index, cell_index, span_size = row_span
        for r in range(1, span_size):
            data[row_index + r].insert(cell_index, '')

    # Create a DataFrame from the data
    columns = data[0]
    df_data = data[1:]
    df = pd.DataFrame(df_data, columns=columns)

    # Replace None values with empty strings
    df = df.fillna('')

    # Convert the DataFrame to a dictionary
    data_dict = df.to_dict('list')

    return data_dict

def find_differences(existing_data, current_data):
    # Initialize lists to store added, removed, and changed clusters and test cases
    added_clusters = []
    removed_clusters = []
    changed_test_cases = {}
    added_test_cases = []
    removed_test_cases = []

    # Get the list of cluster names in existing and current data
    existing_clusters = list(existing_data.keys())
    current_clusters = list(current_data.keys())

    # Find added and removed clusters
    added_clusters = list(set(current_clusters).difference(set(existing_clusters)))
    removed_clusters = list(set(existing_clusters).difference(set(current_clusters)))

    # Compare cluster details and test cases for common clusters
    for cluster in current_clusters:
        if cluster in added_clusters or cluster in removed_clusters:
            continue

        # Get the list of test cases for the current cluster in existing and current data
        existing_test_cases = existing_data[cluster]
        current_test_cases = current_data[cluster]

        # Find added and removed test cases
        added_test_cases = [test_case for test_case in current_test_cases if test_case not in existing_test_cases]
        removed_test_cases = [test_case for test_case in existing_test_cases if test_case not in current_test_cases]

        # Find changes in test cases
        changed_test_cases[cluster] = []

        for test_case in current_test_cases:
            if test_case in existing_test_cases:
                existing_test_case = existing_test_cases[test_case]
                current_test_case = current_test_cases[test_case]

                # Compare individual test case details
                changes = []
                for key in current_test_case:
                    if key not in existing_test_case:
                        changes.append(f"New {key}")
                    elif current_test_case[key] != existing_test_case[key]:
                        changes.append(f"{key} changed")

                if changes:
                    changed_test_cases[cluster].append((test_case, changes))

    # Create a dictionary to store the differences
    differences = {
        "added_clusters": added_clusters,
        "removed_clusters": removed_clusters,
        "changed_test_cases": changed_test_cases,
        "added_test_cases": added_test_cases,
        "removed_test_cases": removed_test_cases
    }

    return differences

def update_test_plan_changes(log_sheet, changes, software_version):
    change_entries = []

    if changes["chagedtc"]:
        for test_case_id, modified_columns in changes["chagedtc"].items():
            for column in modified_columns:
                change_entries.append([today, software_version, test_case_id, "Test case modified", column])

    if change_entries:
        for _ in change_entries:
            log_sheet.insert_rows(2)

        for i in range(len(change_entries)):
            for j, value in enumerate(change_entries[i]):
                log_sheet.cell(row=i + 2, column=j + 1, value=value)

def update_change_log(log_sheet, changes, software_version):
    log_entries = []

    if changes["chagedtc"]:
        for test_case_id, modified_columns in changes["chagedtc"].items():
            for column in modified_columns:
                log_entries.append([today, software_version, test_case_id, "Test case modified", column])

    if changes["addedcluster"]:
        for added_cluster in changes["addedcluster"]:
            log_entries.append([today, software_version, added_cluster, "New cluster added"])

    if changes["removedcluster"]:
        for removed_cluster in changes["removedcluster"]:
            log_entries.append([today, software_version, removed_cluster, "Cluster removed"])

    if changes["addedtc"]:
        for added_test_case in changes["addedtc"]:
            log_entries.append([today, software_version, added_test_case, "New test case added to this cluster"])

    if changes["removedtc"]:
        for removed_test_case in changes["removedtc"]:
            log_entries.append([today, software_version, removed_test_case, "Test case removed from this cluster"])

    if log_entries:
        for _ in log_entries:
            log_sheet.insert_rows(2)

        for i in range(len(log_entries)):
            for j, value in enumerate(log_entries[i]):
                log_sheet.cell(row=i + 2, column=j + 1, value=value)

if __name__ == '__main__':
    # Load existing data from a JSON file or create an empty data structure
    try:
        with open(json_filename, 'r') as json_file:
            existing_data = json.load(json_file)
            existing_data_loaded = True
    except FileNotFoundError:
        existing_data = {}
        existing_data_loaded = False

    with open(app_html_path) as f:
        app_soup = BeautifulSoup(f, 'html.parser')

    with open(main_html_path) as f:
        main_soup = BeautifulSoup(f, 'html.parser')

    version_tag = app_soup.find('div', class_='details')
    version_text = version_tag.find('span', id="revnumber").text
    version = version_text

    h1_tags_app = app_soup.find_all('h1', {'id': True})
    h1_tags_main = main_soup.find_all('h1', {'id': True})

    print(len(h1_tags_app))

    # Create or update the "All_TC_Details" sheet
    if "All_TC_Details" in sheet_names:
        workbook.remove(workbook["All_TC_Details"])
        workbook.create_sheet("All_TC_Details", 0)
        all_tc_sheet = workbook["All_TC_Details"]
    else:
        all_tc_sheet = workbook.active
        all_tc_sheet.title = "All_TC_Details"

    header = ["S.no", "Cluster Name", "Test Case Name", "Test Case ID", "Test Plan"]
    all_tc_sheet.append(header)

    extract_test_case_details(h1_tags_app, workbook, all_tc_sheet, current_data, 0)
    extract_test_case_details(h1_tags_main, workbook, all_tc_sheet, current_data, 1)

    column_widths = {'A': 10, 'B': 20, 'C': 50, 'D': 30, 'E': 30}
    for column, width in column_widths.items():
        all_tc_sheet.column_dimensions[column].width = width

    workbook.save(filename)

    # Save current data to a JSON file
    with open(json_filename, 'w') as json_file:
        json.dump(current_data, json_file, indent=4)

    # Compare existing and current data to find differences
    if existing_data_loaded:
        differences = find_differences(existing_data, current_data)

        # Update change log sheets
        if "Test_plan_Changes" not in sheet_names:
            test_plan_changes_sheet = workbook.create_sheet("Test_plan_Changes", 2)
            test_plan_changes_sheet.append(["Date", "Commit", "Cluster/Testcase", "Changes", "Column"])
        else:
            test_plan_changes_sheet = workbook["Test_plan_Changes"]

        update_change_log(test_plan_changes_sheet, differences, version)

        if "Test_Summary_Changes" not in sheet_names:
            test_summary_changes_sheet = workbook.create_sheet("Test_Summary_Changes", 1)
            test_summary_changes_sheet.append(["Date", "Commit", "Cluster/Testcase", "Changes", "Column"])
        else:
            test_summary_changes_sheet = workbook["Test_Summary_Changes"]

        update_change_log(test_summary_changes_sheet, differences, version)

    # Save the workbook
    print("Saving the workbook to file:", filename)
    workbook.save(filename)
    print("Workbook saved successfully.")
