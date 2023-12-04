from bs4 import BeautifulSoup
import openpyxl
from openpyxl import load_workbook
from joblib import Parallel, delayed
import re
import datetime
import pandas as pd
import json

today_date = datetime.date.today().strftime("%Y-%m-%d")
excel_filename = "Docs/Test_plan_changes.xlsx"

try:
    workbook = load_workbook(excel_filename)
except FileNotFoundError:
    workbook = openpyxl.Workbook()

sheet_names = workbook.sheetnames

app_html_path = "Docs/Test_Plan_HTML/allclusters.html"
main_html_path = "Docs/Test_Plan_HTML/index.html"

json_filename = "src/TC_Summary.json"


def extract_testcase_id(header_text):
    match = re.search(r"\[(.*?)\]", header_text)
    if match:
        return match.group(1)
    return None


def extract_testcase_details(h4_tag, test_plan):
    print(f"Extracting details for test case: {h4_tag.text}")
    data = {}
    header_text = h4_tag.text

    data["Test Case Name"] = header_text
    data["Test Case ID"] = extract_testcase_id(header_text)
    data["Test Plan"] = test_plan

    purpose_tag = h4_tag.find_next(
        "h5", {"id": lambda x: x and x.startswith("_purpose")}
    )
    purpose = purpose_tag.find_next("p").text
    data["Purpose"] = purpose

    data["PICS"] = []
    pics_tag = h4_tag.find_next("h5", {"id": lambda x: x and x.startswith("_pics")})
    ul_div = pics_tag.find_next("div", class_="ulist")

    if ul_div:
        p_tags = ul_div.find_all("p")
    else:
        pics_tag = pics_tag.find_next(
            "h5", {"id": lambda x: x and x.startswith("_pics")}
        )
        ul_div = pics_tag.find_next("div", class_="ulist")
        p_tags = ul_div.find_all("p")

    for p_tag in p_tags:
        data["PICS"].append(p_tag.text)

    preconditions_tag = h4_tag.find_next(
        "h5", {"id": lambda x: x and x.startswith("_preconditions")}
    )

    if preconditions_tag:
        data["Pre-condition"] = {}
        table = preconditions_tag.find_next("table")

        if table:
            data["Pre-condition"] = create_dataframe_from_table(table)

    else:
        data["Pre-condition"] = "Nil"

    test_procedure_tags = h4_tag.find_next(
        "h5", {"id": lambda x: x and x.startswith("_test_procedure")}
    )

    if not test_procedure_tags:
        test_procedure_tags = h4_tag.find_next(
            "h6", {"id": lambda x: x and x.startswith("_test_procedure")}
        )

    table = test_procedure_tags.find_next("table")
    data["Test Procedure"] = create_dataframe_from_table(table)

    print(f"Test case details extracted for {data['Test Case ID']}")
    workbook.save(excel_filename)

    return header_text, data


def extract_testcase_details_from_html(html_path, header_tag, second_header_text):
    with open(html_path) as file:
        soup = BeautifulSoup(file, "lxml")

    header_tags = soup.find_all("h1", {"id": True})
    first_header_tag = [tag for tag in header_tags if tag.text == header_tag][0]

    if second_header_text:
        second_header_tag = [
            tag for tag in header_tags if tag.text == second_header_text
        ][0]
    else:
        second_header_tag = False

    cluster_name = (
        header_tag.replace(" Cluster Test Plan", "")
        .replace(" Cluster TestPlan", "")
        .replace(" Cluster", "")
        .replace(" cluster", "")
        .replace(" Test Plan", "")
    )

    if header_tag == "MCORE PICS Definition":
        return None

    result = []

    if second_header_tag:
        for h5_tag in first_header_tag.find_all_next(
            ["h5", "h6"], {"id": lambda x: x and x.startswith("_test_procedure")}
        ):
            if (
                h5_tag.find_previous("h1") == first_header_tag
                and h5_tag.find_next("h1") == second_header_tag
            ):
                result.append(h5_tag)
    else:
        for h5_tag in first_header_tag.find_all_next(
            ["h5", "h6"], {"id": lambda x: x and x.startswith("_test_procedure")}
        ):
            if h5_tag.find_previous("h1") == first_header_tag:
                result.append(h5_tag)

    if not result:
        h5_tags = first_header_tag.find_all_next(
            ["h5", "h6"], {"id": lambda x: x and x.startswith("_test_procedure")}
        )

        for h5_tag in h5_tags:
            if (
                h5_tag.find_previous("h1") == first_header_tag
                and h5_tag.find_next("h1") == second_header_tag
            ):
                result.append(h5_tag)

    headers = []
    for h5_tag in result:
        h4_tag = h5_tag.find_previous("h4")
        header_text, data = extract_testcase_details(
            h4_tag, get_test_plan_type(html_path)
        )
        headers.append(header_text)

    return {cluster_name: headers}


def create_dataframe_from_table(table):
    rows = table.find_all("tr")
    data = []
    col_spans = []
    row_spans = []

    for i, row in enumerate(rows):
        cells = row.find_all(["th", "td"])
        row_data = []
        for j, cell in enumerate(cells):
            if cell.has_attr("colspan"):
                col_spans.append((i, j, int(cell["colspan"])))
            if cell.has_attr("rowspan"):
                row_spans.append((i, j, int(cell["rowspan"])))
            row_data.append(cell.get_text(strip=True))
        data.append(row_data)

    for span in col_spans:
        i, j, span_size = span
        for r in range(1, span_size):
            data[i].insert(j + 1, "")

    for span in row_spans:
        i, j, span_size = span
        for r in range(1, span_size):
            data[i + r].insert(j, "")

    df = pd.DataFrame(data[1:], columns=data[0])
    df = df.fillna("")

    data_dict = df.to_dict("list")

    return data_dict


def detect_changes(existing_data, updated_data):
    new_clusters = list(updated_data.keys())
    old_clusters = list(existing_data.keys())

    added_clusters = list(set(new_clusters).difference(set(old_clusters)))
    removed_clusters = list(set(old_clusters).difference(set(new_clusters)))

    changed_testcases = {}
    new_testcases = []
    removed_testcases = []

    for cluster in new_clusters:
        if cluster in added_clusters + removed_clusters:
            continue

        new_testcases_data = updated_data[cluster]
        old_testcases_data = existing_data[cluster]

        if new_testcases_data == old_testcases_data:
            print(f"No changes in {cluster} cluster")
            continue

        if len(new_testcases_data) == len(old_testcases_data):
            for i in range(len(new_testcases_data)):
                if new_testcases_data[i] == old_testcases_data[i]:
                    print(f"{new_testcases_data[i]['Test Case ID']} has no change ")
                else:
                    changes = []
                    keys = list(new_testcases_data[i].keys())

                    for k in keys:
                        if new_testcases_data[i][k] == old_testcases_data[i][k]:
                            print(
                                f"{new_testcases_data[i]['Test Case ID']} {k} has no change "
                            )
                        elif k == "Test Procedure":
                            test_procedure_keys = list(new_testcases_data[i][k].keys())
                            print(test_procedure_keys)

                            for tp_key in test_procedure_keys:
                                if (
                                    new_testcases_data[i][k][tp_key]
                                    == old_testcases_data[i][k][tp_key]
                                ):
                                    print(
                                        f"{new_testcases_data[i]['Test Case ID']} {tp_key} has no change "
                                    )
                                else:
                                    changes.append(f"Testprocedure({tp_key})")
                        else:
                            changes.append(k)

                    changed_testcases[new_testcases_data[i]["Test Case ID"]] = changes

        elif len(new_testcases_data) > len(old_testcases_data):
            new_testcases.append(cluster)

        else:
            removed_testcases.append(cluster)

    changes_data = {
        "added_clusters": added_clusters,
        "removed_clusters": removed_clusters,
        "changed_testcases": changed_testcases,
        "added_testcases": new_testcases,
        "removed_testcases": removed_testcases,
    }

    return changes_data


def update_changes_in_excel(changes_data, excel_sheet, version):
    changes = []

    if changes_data["changed_testcases"]:
        keys = list(changes_data["changed_testcases"].keys())
        for k in keys:
            for change in changes_data["changed_testcases"][k]:
                changes.append([today_date, version, k, "Testcase Modified", change])

    if changes_data["added_clusters"]:
        for cluster in changes_data["added_clusters"]:
            changes.append([today_date, version, cluster, "Cluster Added"])

    if changes_data["removed_clusters"]:
        for cluster in changes_data["removed_clusters"]:
            changes.append([today_date, version, cluster, "Cluster Removed"])

    if changes_data["added_testcases"]:
        for testcase in changes_data["added_testcases"]:
            changes.append([today_date, version, testcase, "Testcase Added"])

    if changes_data["removed_testcases"]:
        for testcase in changes_data["removed_testcases"]:
            changes.append([today_date, version, testcase, "Testcase Removed"])

    print(changes)

    if changes:
        print(len(changes))
        for i in range(len(changes)):
            excel_sheet.insert_rows(2)

        for i in range(len(changes)):
            for j, value in enumerate(changes[i]):
                excel_sheet.cell(row=i + 2, column=j + 1, value=value)
    else:
        excel_sheet.insert_rows(2)
        values = [today_date, version, "Nil", f"NO CHANGE : {today_date}", "Nil"]

        for i in range(0, 1):
            for j, value in enumerate(values):
                excel_sheet.cell(row=i + 2, column=j + 1, value=value)

    return None


def update_test_case_changes(changes_data, excel_sheet, version):
    changes = []

    if changes_data["changed_testcases"]:
        keys = list(changes_data["changed_testcases"].keys())
        for k in keys:
            for change in changes_data["changed_testcases"][k]:
                if change in ["Test Case Name", "Test Case ID"]:
                    changes.append(
                        [today_date, version, k, "Testcase Modified", change]
                    )

    if changes_data["added_clusters"]:
        for cluster in changes_data["added_clusters"]:
            changes.append([today_date, version, cluster, "Cluster Added"])

    if changes_data["removed_clusters"]:
        for cluster in changes_data["removed_clusters"]:
            changes.append([today_date, version, cluster, "Cluster Removed"])

    if changes_data["added_testcases"]:
        for testcase in changes_data["added_testcases"]:
            changes.append([today_date, version, testcase, "Testcase Added"])

    if changes_data["removed_testcases"]:
        for testcase in changes_data["removed_testcases"]:
            changes.append([today_date, version, testcase, "Testcase Removed"])

    if changes:
        print(len(changes))
        for i in range(len(changes)):
            excel_sheet.insert_rows(2)

        for i in range(len(changes)):
            for j, value in enumerate(changes[i]):
                excel_sheet.cell(row=i + 2, column=j + 1, value=value)
    else:
        excel_sheet.insert_rows(2)
        values = [today_date, version, "Nil", f"NO CHANGE : {today_date}", "Nil"]

        for i in range(0, 1):
            for j, value in enumerate(values):
                excel_sheet.cell(row=i + 2, column=j + 1, value=value)

    return None


def enclose_clusters(header_tags):
    enclosing_headers = []

    for i in range(len(header_tags)):
        if i == (len(header_tags) - 1):
            second_header = False
        else:
            second_header = header_tags[i + 1].text
        enclosing_headers.append(second_header)

    return enclosing_headers


def update_test_case_summary(excel_sheet, updated_data):
    print("Updating test case summary in Excel sheet 'All_TC_Details'...")
    clusters = list(updated_data.keys())

    for cluster in clusters:
        test_case_ids = updated_data[cluster][0]["Test Case ID"]
        sh = re.search(r"-(.*?)-", test_case_ids)
        code = sh.group(1)

        if code == "LOWPOWER":
            code = "MC"

        sheet = workbook[code]
        sheet.append([cluster])
        sheet.append([""])

        test_cases = updated_data[cluster]

        for test_case in test_cases:
            test_case_name = test_case["Test Case Name"]
            sheet.append([test_case_name])
            sheet.append([""])
            sheet.append(["Purpose"])
            sheet.append([test_case["Purpose"]])
            sheet.append([""])
            sheet.append(["PICS"])

            for pics in test_case["PICS"]:
                sheet.append([pics])

            sheet.append([""])
            sheet.append(["Pre-condition"])

            if test_case["Pre-condition"] == "Nil":
                sheet.append(["Nil"])
            else:
                headers = list(test_case["Pre-condition"].keys())
                sheet.append(headers)

                for i in range(len(list(test_case["Pre-condition"].values())[0])):
                    values = []

                    for key, value in test_case["Pre-condition"].items():
                        if i < len(value):
                            values.append(value[i])

                    sheet.append(values)

            sheet.append([""])
            sheet.append(["Test Procedure"])
            keys = list(test_case["Test Procedure"].keys())
            sheet.append(keys)

            for i in range(len(list(test_case["Test Procedure"].values())[0])):
                values = []

                for key, value in test_case["Test Procedure"].items():
                    if i < len(value):
                        values.append(value[i])

                sheet.append(values)

            sheet.append([""])
            sheet.append([""])
            sheet.append([""])
            head_text_match = re.search(r"\[(.*?)\]\s*(.*)", test_case_name)

            if head_text_match:
                test_case_full_name = (
                    "[" + head_text_match.group(1) + "] " + head_text_match.group(2)
                )
            else:
                test_case_full_name = ""

            test_case_id = test_case["Test Case ID"]
            test_plan = test_case["Test Plan"]
            row_number = excel_sheet.max_row

            row_values = [
                row_number,
                cluster,
                test_case_full_name,
                test_case_id,
                test_plan,
            ]
            excel_sheet.append(row_values)

            print(
                f"Updated details for test case: {test_case['Test Case ID']} in cluster: {cluster}"
            )
            workbook.save(excel_filename)

    print("Test case summary updated successfully.")


def main():
    print("Starting the script...")

    updated_data = {}

    try:
        with open(json_filename, "r") as json_file:
            existing_data = json.load(json_file)
            is_existing_data = True
    except FileNotFoundError:
        existing_data = {}
        is_existing_data = False

    with open(app_html_path) as f:
        soup_app = BeautifulSoup(f, "lxml")

    with open(main_html_path) as f:
        soup_main = BeautifulSoup(f, "lxml")

    version_tag_app = soup_app.find("div", class_="details")
    version_text = version_tag_app.find("span", id="revnumber")
    version = version_text.text

    h1_tags_app = soup_app.find_all("h1", {"id": True})
    h1_tags_main = soup_main.find_all("h1", {"id": True})

    h1_tags_app_text = [tag.text for tag in h1_tags_app]
    h1_tags_main_text = [tag.text for tag in h1_tags_main]

    print(f"Number of clusters in app HTML: {len(h1_tags_app)}")

    if "All_TC_Details" in sheet_names:
        print("Removing the existing 'All_TC_Details' sheet and creating a new one...")
        workbook.remove(workbook["All_TC_Details"])
        workbook.create_sheet("All_TC_Details", 0)
        excel_sheet = workbook["All_TC_Details"]
    else:
        print("Using the existing 'All_TC_Details' sheet...")
        excel_sheet = workbook.active
        excel_sheet.title = "All_TC_Details"

    header = ["S.no", "Cluster Name", "Test Case Name", "Test Case ID", " Test Plan "]
    excel_sheet.append(header)

    cluster_enclosures_app = cluster_enclose(h1_tags_app)
    print(f"Cluster enclosures in app HTML: {cluster_enclosures_app}")

    if len(cluster_enclosures_app) == len(h1_tags_app):
        input_data = [
            (h1_tags_app_text[i], 0, cluster_enclosures_app[i])
            for i in range(len(cluster_enclosures_app))
        ]
        print("Extracting test case details from app HTML...")
        results = Parallel(n_jobs=-1)(
            delayed(tc_details)(a, b, c) for a, b, c in input_data
        )

        for result in results:
            if result is not None:
                updated_data.update(result)

    else:
        print("Failed to extract test case details from app HTML")

    cluster_enclosures_main = cluster_enclose(h1_tags_main)

    if len(cluster_enclosures_main) == len(h1_tags_main):
        input_data = [
            (h1_tags_main_text[i], 1, cluster_enclosures_main[i])
            for i in range(len(cluster_enclosures_main))
        ]
        print("Extracting test case details from main HTML...")
        results = Parallel(n_jobs=-1)(
            delayed(tc_details)(a, b, c) for a, b, c in input_data
        )

        for result in results:
            if result is not None:
                updated_data.update(result)

    else:
        print("Failed to extract test case details from main HTML")

    codes = []
    clusters = list(existing_data.keys())

    for test in updated_data:
        test_case_id = updated_data[test][0]["Test Case ID"]
        sh = re.search(r"-(.*?)-", test_case_id)
        code = sh.group(1)

        if code == "LOWPOWER":
            code = "MC"

        codes.append(code)

    for code in codes:
        if code in sheet_names:
            workbook.remove(workbook[code])
            workbook.create_sheet(code, sheet_names.index(code))

        else:
            workbook.create_sheet(code)

    print("Updating test case summary in Excel...")
    update_test_case_summary(excel_sheet, updated_data)

    if is_existing_data:
        print("Detecting changes in test cases...")
        diff_result = detect_changes(existing_data, updated_data)
        print("\nChanges detected:")
        print(diff_result)

        if "Test_plan_Changes" not in sheet_names:
            changes_sheet = workbook.create_sheet("Test_plan_Changes", 2)
            changes_sheet.append(
                ["Date of Run", " Commit", "Cluster/Testcase", "Changes", "Column"]
            )
        else:
            changes_sheet = workbook["Test_plan_Changes"]

        print("\nUpdating Test Plan Changes sheet...")
        update_changes_in_excel(diff_result, changes_sheet, version)

        print("\nChanges detected:")
        print(diff_result)
        if "Test_Summary_Changes" not in sheet_names:
            changes_sheet = workbook.create_sheet("Test_Summary_Changes", 1)
            changes_sheet.append(
                [
                    "Date of Run",
                    "Cluster Name",
                    "Test Case Name",
                    "Test Case ID",
                    "Test Plan",
                    "Change Type",
                ]
            )
        else:
            changes_sheet = workbook["Test_Summary_Changes"]

        print("\nUpdating Test Summary Changes sheet...")
        update_test_case_changes(diff_result, changes_sheet, version)

    column_widths = {
        "A": 10,
        "B": 20,
        "C": 50,
        "D": 30,
        "E": 30,
    }

    for column, width in column_widths.items():
        excel_sheet.column_dimensions[column].width = width

    workbook.save(excel_filename)

    print("Saving updated data to JSON file...")
    with open(json_filename, "w") as json_file:
        json.dump(updated_data, json_file, indent=4)

    workbook.save(excel_filename)
    print("\nScript execution completed.")


if __name__ == "__main__":
    main()
