from bs4 import BeautifulSoup
import openpyxl
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment
import re
import datetime
import os
import pandas as pd
import json

# Current date
today = datetime.date.today().strftime('%Y-%m-%d')

# Output filename
output_filename = "Docs/test_plan_change.xlsx"

try:
    workbook = load_workbook(output_filename)
except FileNotFoundError:
    workbook = openpyxl.Workbook()

sheet_names = workbook.sheetnames

app_html_path = 'Docs/Test_Plan_HTML/allclusters.html'
main_html_path = 'Docs/Test_Plan_HTML/index.html'

json_filename = 'src/TC_Summary_VS.json'

current_data = {}

def extract_test_case_id(header):
    match = re.search(r'\[(.*?)\]', header)
    if match:
        matched_data = match.group()
        testcase = re.sub(r'\[|\]', '', matched_data)
    return testcase

def process_test_case(h4_tag, new_sheet, test_plan):
    data = {}
    header_text = h4_tag.text
    new_sheet.append([header_text])
    data["Test Case Name"] = header_text
    data["Test Case ID"] = extract_test_case_id(header_text)
    data["Test Plan"] = test_plan
    new_sheet.append([""])
    new_sheet.append(["Purpose"])
    purpose_tag = h4_tag.find_next('h5', {'id': lambda x: x and x.startswith('_purpose')})
    purpose = purpose_tag.find_next('p').text
    new_sheet.append([purpose])
    data["Purpose"] = purpose
    new_sheet.append([""])
    new_sheet.append(["PICS"])
    data["PICS"] = []
    pics_tag = h4_tag.find_next('h5', {'id': lambda x: x and x.startswith('_pics')})
    ul_div = pics_tag.find_next('div', class_='ulist')
    if ul_div:
        p_tag = ul_div.find_all('p')
    else:
        pics_tag = pics_tag.find_next('h5', {'id': lambda x: x and x.startswith('_pics')})
        ul_div = pics_tag.find_next('div', class_='ulist')
        p_tag = ul_div.find_all('p')
    for p in p_tag:
        pt = p.text
        new_sheet.append([pt])
        data["PICS"].append(pt)
    new_sheet.append([""])
    new_sheet.append(["Pre-condition"])
    preconditions_tag = h4_tag.find_next('h5', {'id': lambda x: x and x.startswith('_preconditions')})
    if preconditions_tag:
        data["Pre-condition"] = {}
        table = preconditions_tag.find_next('table')
        if table:
            data_dict = create_data_dict_from_table(table)
        if data_dict:
            data["Pre-condition"] = data_dict
            keys = list(data_dict.keys())
            new_sheet.append(keys)

            for i in range(len(list(data_dict.values())[0])):
                val = []
                for key, value in data_dict.items():
                    if i < len(value):
                        val.append(value[i])
                new_sheet.append(val)
    else:
        new_sheet.append(["nil"])
        data["Pre-condition"] = "Nil"
    new_sheet.append([""])
    new_sheet.append(["Test Procedure"])
    test_procedure_tag = h4_tag.find_next('h5', {'id': lambda x: x and x.startswith('_test_procedure')})
    if test_procedure_tag:
        None
    else:
        test_procedure_tag = h4_tag.find_next('h6', {'id': lambda x: x and x.startswith('_test_procedure')})
    table = test_procedure_tag.find_next('table')
    data_dict = create_data_dict_from_table(table)
    data["Test Procedure"] = data_dict
    keys = list(data_dict.keys())
    new_sheet.append(keys)
    for i in range(len(list(data_dict.values())[0])):
        val = []
        for key, value in data_dict.items():
            if i < len(value):
                val.append(value[i])
        new_sheet.append(val)
    new_sheet.append([""])
    new_sheet.append([""])
    new_sheet.append([""])
    workbook.save(output_filename)
    return header_text, data

def process_test_case_details(h1_tags, sheet1, app_flag):
    if app_flag == 0:
        test_plan_type = "App Test Case"
    else:
        test_plan_type = "Core Test Case"

    for i in range(len(h1_tags)):
        print(f"Processing h1 tag {i + 1}/{len(h1_tags)}")
        h1 = h1_tags[i].text
        cluster_name = h1.replace(' Cluster Test Plan', '') \
            .replace(' Cluster TestPlan', '') \
            .replace(' Cluster', '') \
            .replace(' cluster', '') \
            .replace(' Test Plan', '')

        if h1 == "MCORE PICS Definition":
            continue
        if h1 == "Bulk Data Exchange Protocol Test Plan":
            sheet_name = "BR"
        else:
            h4_tag_data = h1_tags[i].find_next('h4', {'id': lambda x: x and x.startswith('_tc')})
            h4 = h4_tag_data.text
            test_case_id = extract_test_case_id(h4)
            match = re.search(r'-(.*?)-', test_case_id)
            sheet_name = match.group(1)
            if sheet_name:
                if sheet_name == "LOWPOWER":
                    sheet_name = "MC"
            else:
                h4 = h1.find_next('h5', {'id': lambda x: x and x.startswith('_tc')})
                h4 = h4_tag[i].text
                sheet_name = extract_test_case_id(h4)
                match = re.search(r'-(.*?)-', test_case_id)
                sheet_name = match.group(1)

        print("Sheet Name:", sheet_name)
        if sheet_name in sheet_names:
            workbook.remove(workbook[sheet_name])
            workbook.create_sheet(sheet_name, sheet_names.index(sheet_name))
            new_sheet = workbook[sheet_name]
        else:
            new_sheet = workbook.create_sheet(sheet_name)
        new_sheet.append([cluster_name])
        new_sheet.append([""])
        current_cluster_data = current_data[cluster_name] = []

        first_h1 = h1_tags[i]
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
            for h5_tag in h5_tags:
                result.append(h5_tag)
        if result:
            headers = []
            for h5_tag in result:
                h4_tag = h5_tag.find_previous('h4')
                header_text, data = process_test_case(h4_tag, new_sheet, test_plan_type)
                current_cluster_data.append(data)
                headers.append(header_text)
        else:
            h5_tags = first_h1.find_all_next('h6', {'id': lambda x: x and x.startswith('_test_procedure')})
            for h5_tag in h5_tags:
                if h5_tag.find_previous('h1') == first_h1:
                    if h5_tag.find_next('h1') == second_h1:
                        result.append(h5_tag)
            print("Result:", result)
            headers = []
            for h5_tag in result:
                h4_tag = h5_tag.find_previous('h5')
                header_text, data = process_test_case(h4_tag, new_sheet, test_plan_type)
                current_cluster_data.append(data)
                headers.append(header_text)
        column_widths = {'A': 10, 'B': 20, 'C': 20, 'D': 40, 'E': 50}
        if isinstance(new_sheet, list):
            print(f"{sheet_name} already exists")
        else:
            for column, width in column_widths.items():
                new_sheet.column_dimensions[column].width = width
        for j in range(len(result)):
            test_case_id = extract_test_case_id(headers[j])
            head_text_match = re.search(r'\[(.*?)\]\s*(.*)', headers[j])
            if head_text_match:
                test_case_name = '[' + head_text_match.group(1) + '] ' + head_text_match.group(2)
            else:
                test_case_name = ''
            row_number = sheet1.max_row
            values = [row_number, cluster_name, test_case_name, test_case_id, test_plan_type]
            sheet1.append(values)

def create_data_dict_from_table(table):
    rows = table.find_all('tr')
    data = []
    col_spans = []
    row_spans = []
    for i, row in enumerate(rows):
        cells = row.find_all(['th', 'td'])
        row_data = []
        for j, cell in enumerate(cells):
            if cell.has_attr('colspan'):
                col_spans.append((i, j, int(cell['colspan'])))
            if cell.has_attr('rowspan'):
                row_spans.append((i, j, int(cell['rowspan'])))
            row_data.append(cell.get_text(strip=True))
        data.append(row_data)
    for span in col_spans:
        i, j, span_size = span
        for r in range(1, span_size):
            data[i].insert(j + 1, '')
    for span in row_spans:
        i, j, span_size = span
        for r in range(1, span_size):
            data[i + r].insert(j, '')
    df = pd.DataFrame(data[1:], columns=data[0])
    df = df.fillna('')
    data_dict = {}
    data_dict = df.to_dict('list')
    return(data_dict)

def find_changes(existing_data, current_data):
    new_clusters = list(set(current_data.keys()) - set(existing_data.keys()))
    removed_clusters = list(set(existing_data.keys()) - set(current_data.keys()))
    changed_clusters = {}
    added_test_cases = []
    removed_test_cases = []
    print("New Clusters:", new_clusters)
    print("Removed Clusters:", removed_clusters)
    print("Changed Clusters:", changed_clusters)
    print("Added Test Cases:", added_test_cases)
    print("Removed Test Cases:", removed_test_cases)
    for cluster in current_data.keys():
        if cluster in new_clusters or cluster in removed_clusters:
            continue
        current_cluster = current_data[cluster]
        existing_cluster = existing_data[cluster]
        if current_cluster == existing_cluster:
            print(f"No changes in the {cluster} cluster")
        if len(current_cluster) == len(existing_cluster):
            for i in range(len(current_cluster)):
                if current_cluster[i] == existing_cluster[i]:
                    print(f"{current_cluster[i]['Test Case ID']} has no change ")
                else:
                    changes = []
                    keys = list(current_cluster[i].keys())
                    for key in keys:
                        if current_cluster[i][key] == existing_cluster[i][key]:
                            print(f"{current_cluster[i]['Test Case ID']} {key} has no change ")
                        elif key == "Test Procedure":
                            test_procedures = list(current_cluster[i][key].keys())
                            for tp in test_procedures:
                                if current_cluster[i][key][tp] != existing_cluster[i][key][tp]:
                                    changes.append(f"Test procedure ({tp})")
                        else:
                            changes.append(key)
                    changed_clusters[current_cluster[i]['Test Case ID']] = changes
        elif len(current_cluster) > len(existing_cluster):
            added_test_cases.append(cluster)
        else:
            removed_test_cases.append(cluster)
    changes_dict = {}
    changes_dict = {
        "added_clusters": new_clusters,
        "removed_clusters": removed_clusters,
        "changed_test_cases": changed_clusters,
        "added_test_cases": added_test_cases,
        "removed_test_cases": removed_test_cases
    }
    return changes_dict

def update_test_plan_changes(changes_dict, sheet, version):
    changes = []
    if changes_dict["changed_test_cases"]:
        keys = list(changes_dict["changed_test_cases"].keys())
        for test_case_id in keys:
            for change in changes_dict["changed_test_cases"][test_case_id]:
                print(f"Updating change for Test Case {test_case_id}: {change}")
                changes.append([today, version, test_case_id, "This test case is modified", change])
                
    if changes:
        print("Changes to be updated:")
        print(changes)
        for h in range(len(changes)):
            sheet.insert_rows(2)
        for i in range(len(changes)):
            for j, value in enumerate(changes[i]):
                sheet.cell(row=i + 2, column=j + 1, value=value)

    else:
        sheet.insert_rows(2)
        value = [today,version,"Nil", f"No changes on {today} ", "Nil"]
        for i in range(0, 1):
            for j, value in enumerate(value):                                                                                 
                sheet.cell(row=i + 2, column=j + 1, value=value)

def update_test_case_changes(changes_dict, sheet, version):
    changes = []
    if changes_dict["added_clusters"]:
        for cluster in changes_dict["added_clusters"]:
            changes.append([today, version, cluster, "New cluster added"])
    if changes_dict["removed_clusters"]:
        for cluster in changes_dict["removed_clusters"]:
            changes.append([today, version, cluster, "Cluster removed"])
    if changes_dict["added_test_cases"]:
        for test_case in changes_dict["added_test_cases"]:
            changes.append([today, version, test_case, "New test case added to this cluster"])
    if changes_dict["removed_test_cases"]:
        for test_case in changes_dict["removed_test_cases"]:
            changes.append([today, version, test_case, "Test case removed from this cluster"])

    if changes:
        print("Changes to be updated:")
        print(changes)
        for h in range(len(changes)):
            sheet.insert_rows(2)
        for i in range(len(changes)):
            for j, value in enumerate(changes[i]):
                sheet.cell(row=i + 2, column=j + 1, value=value)

    else:
        sheet.insert_rows(2)
        value = [today,version,"Nil", f"No changes on {today} ", "Nil"]
        for i in range(0, 1):
            for j, value in enumerate(value):                                                                                 
                sheet.cell(row=i + 2, column=j + 1, value=value)

if __name__ == '__main__':
    try:
        with open(json_filename, 'r') as json_file:
            existing_data = json.load(json_file)
            existing_data_flag = True
    except FileNotFoundError:
        existing_data = {}
        existing_data_flag = False

    with open(app_html_path) as f:
        soup1 = BeautifulSoup(f, 'html.parser')

    with open(main_html_path) as f:
        soup2 = BeautifulSoup(f, 'html.parser')

    version_tag = soup1.find('div', class_='details')
    version = version_tag.find('span', id="revnumber").text
    h1_tags1 = soup1.find_all('h1', {'id': True})
    h1_tags2 = soup2.find_all('h1', {'id': True})
	
    if "All_TC_Details" in sheet_names:
        workbook.remove(workbook["All_TC_Details"])
        workbook.create_sheet("All_TC_Details", 0)
        sheet1 = workbook["All_TC_Details"]
    else:
        sheet1 = workbook.active
        sheet1.title = "All_TC_Details"
    
    header = ["S.no", "Cluster Name", "Test Case Name", "Test Case ID", "Test Plan"]
    sheet1.append(header)

    print("Start processing test case details")
    process_test_case_details(h1_tags1, sheet1, 0)
    print("Finished processing test case details for App Test Case")
    print("Start processing test case details for Core Test Case")
    process_test_case_details(h1_tags2, sheet1, 1)
    print("Finished processing test case details for Core Test Case")

    column_widths = {'A': 10, 'B': 20, 'C': 50, 'D': 30, 'E': 30}
    for column, width in column_widths.items():
        sheet1.column_dimensions[column].width = width

    workbook.save(output_filename)

    with open(json_filename, 'w') as json_file:
        json.dump(current_data, json_file, indent=4)

    if existing_data_flag:
        changes_dict = find_changes(existing_data, current_data)
        if "Test_plan_Changes" not in sheet_names:
            changes_sheet = workbook.create_sheet("Test_plan_Changes", 2)
            changes_sheet.append(["Date", "Commit", "Cluster/Testcase", "Changes", "Column"])
        else:
            changes_sheet = workbook["Test_plan_Changes"]

        update_test_plan_changes(changes_dict, changes_sheet, version)

        if "Test_Summary_Changes" not in sheet_names:
            changes_sheet = workbook.create_sheet("Test_Summary_Changes", 1)
            changes_sheet.append(["Date", "Commit", "Cluster/Testcase", "Changes", "Column"])
        else:
            changes_sheet = workbook["Test_Summary_Changes"]

        update_test_case_changes(changes_dict, changes_sheet, version)

    workbook.save(output_filename)
