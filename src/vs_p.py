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
filename = 'Docs/test_plan_change.xlsx'

try:
    workbook = load_workbook(filename)
except FileNotFoundError:
    workbook = openpyxl.Workbook()

sheet_names = workbook.sheetnames

app = 'Docs/Test_Plan_HTML/allclusters.html'
main = 'Docs/Test_Plan_HTML/index.html'

json_filename = 'src/TC_Summary_VS.json'

current_data ={}

def tc_id (head):
    testcase1 = re.search(r'\[(.*?)\]',head)
    if testcase1:
        matched_str = testcase1.group()  # Extract the matched substring
        testcase = re.sub(r'\[|\]', '', matched_str)

    return testcase

def tc(h4_tag, new_sheet, tp):
    d = {}
    headt= h4_tag.text
    new_sheet.append([headt])
    d["Test Case Name"] = headt
    d["Test Case ID"] = tc_id(headt)
    d["Test Plan"] = tp
    new_sheet.append([""])
    new_sheet.append(["Purpose"])
    pur_tag = h4_tag.find_next('h5', {'id': lambda x: x and x.startswith('_purpose')})
    pur = pur_tag.find_next('p')
    purt =pur.text
    new_sheet.append([purt])
    d["Purpose"] = purt
    new_sheet.append([""])
    new_sheet.append(["PICS"])
    d["PICS"] = []
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
        d["PICS"].append(pt)
    new_sheet.append([""])
    new_sheet.append(["Pre-condition"])
    pre_tag = h4_tag.find_next('h5', {'id': lambda x: x and x.startswith('_preconditions')})
    if pre_tag:
        d["Pre-condition"] = {}
        table = pre_tag.find_next('table')
        if table:
            data_dict = create_df(table)
        if data_dict:
            d["Pre-condition"] = data_dict
            keys = list(data_dict.keys())
            new_sheet.append(keys)
                   
            for i in range(len(list(data_dict.values())[0])):
                val =[]
                for key, value in data_dict.items():
                    if i < len(value):
                        val.append(value[i]) 
                new_sheet.append(val)
            
    else:
            new_sheet.append(["nil"])
            d["Pre-condition"] = "Nil"
    new_sheet.append([""])
    new_sheet.append(["Test Procedure"])
    h5_tags = h4_tag.find_next('h5', {'id': lambda x: x and x.startswith('_test_procedure')}) 
    if h5_tags:
        None
    else:
        h5_tags = h4_tag.find_next('h6', {'id': lambda x: x and x.startswith('_test_procedure')}) 
    table = h5_tags.find_next('table')
    data_dict =   create_df(table)
    d["Test Procedure"] = data_dict
    keys = list(data_dict.keys())
    new_sheet.append(keys)
    for i in range(len(list(data_dict.values())[0])):
        val =[]
        for key, value in data_dict.items():
            if i < len(value):
                val.append(value[i]) 
        new_sheet.append(val)
    new_sheet.append([""])
    new_sheet.append([""])
    new_sheet.append([""])
    workbook.save(filename)

    return headt , d


def tc_details (h1_tags,sheet1,a):
    if a == 0:
        tp = "App Test Case"
    else:
        tp = "Core Test Case" 
    
    for i in range(len(h1_tags)):
        
        h1 = h1_tags[i].text
        cluster_name = h1.replace('Cluster', '').replace('Test', '').replace('Plan', '')
        if h1 == "MCORE PICS Definition":
            continue
        if h1 == "Bulk Data Exchange Protocol Test Plan":
            sheet = "BR"
        else:
            h4t = h1_tags[i].find_next('h4', {'id': lambda x: x and x.startswith('_tc')})
            h4 = h4t.text
            
            sn = tc_id(h4)
            sh = re.search(r'-(.*?)-', sn)
            sheet = sh.group(1)
            if sheet:
                if sheet == "LOWPOWER":
                    sheet = "MC"
            else:
                h4 = h1.find_next('h5', {'id': lambda x: x and x.startswith('_tc')})
                h4 = h4_tag[i].text
                sheet = tc_id(h4)
                sh = re.search(r'-(.*?)-', sn)
                sheet = sh.group(1)
        
        print (sheet)
        if sheet in sheet_names:
            new_sheet = []
        else:
            new_sheet = workbook.create_sheet(sheet)
        new_sheet.append([cluster_name])
        new_sheet.append([""])
        clus = current_data[cluster_name] = []

        first_h1 = h1_tags[i]  # Select the first h1 tag in the pair
        if i == (len(h1_tags)-1):
            second_h1 = False
        else:
            second_h1 = h1_tags[i+1]  # Select the second h1 tag in the pair
            
        # Find all h5 tags after the first h1 tag with id starting with the value
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
                heads = []
                for h5_tag in result:
                    h4_tag = h5_tag.find_previous('h4')
                    headt, d = tc(h4_tag,new_sheet, tp)
                    clus.append(d)
                    heads.append(headt)

        else:
                h5_tags = first_h1.find_all_next('h6', {'id': lambda x: x and x.startswith('_test_procedure')})  

                for h5_tag in h5_tags:
                    if h5_tag.find_previous('h1') == first_h1:
                        if h5_tag.find_next('h1') == second_h1:
                            result.append(h5_tag)
                
                print (result)
                heads =[]
                for h5_tag in result:
                    h4_tag = h5_tag.find_previous('h5')
                    headt , d = tc(h4_tag,new_sheet, tp)
                    clus.append(d)
                    heads.append(headt)

                
        
        column_widths = {'A': 10, 'B': 20, 'C': 20 ,'D': 40,'E': 50}  # Specify the column widths as desired
        if isinstance(new_sheet, list):
            print(f"{sheet} is already exsit")
        else:
            for column, width in column_widths.items():
                new_sheet.column_dimensions[column].width = width
        
        for j in range(len(result)):
            testcase = tc_id(heads[j])

            tc_name = heads[j].split("]", 1)[-1].strip()

            
            n = sheet1.max_row

            value = [n , tp , cluster_name , testcase , tc_name , heads[j]]
            sheet1.append(value)


def create_df(table):
    rows = table.find_all('tr')
    data = []
    col_spans = []
    row_spans = []
    # to find the rowspan and colspan
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
    # Apply colspans to data
    for span in col_spans:
        i, j, span_size = span
        for r in range(1, span_size):
            data[i].insert(j+1, '')
    # Apply rowspans to data
    for span in row_spans:
        i, j, span_size = span
        for r in range(1, span_size):
            data[i+r].insert(j, '')

    # Convert the data into a pandas dataframe
    df = pd.DataFrame(data[1:], columns=data[0])

    # Replace any None values with an empty string
    df = df.fillna('')
    # convert the dataframe to dict
    data_dict = {}
    # convert the dataframe to dict
    data_dict = df.to_dict('list')
    #print(data_dict)
    return(data_dict)

def diff(existing_data, current_data):
    nc = list(current_data.keys())
    oc = list(existing_data.keys())

    ac = list(set(nc).difference(set(oc)))
    rc = list(set(oc).difference(set(nc)))
    ctc = {}
    ntc =[]
    rtc =[]

    for cluster in nc:
        if cluster in ac+rc:
            continue
        a = current_data[cluster]
        b = existing_data[cluster]
        if a == b:
            print(f"No changes in {cluster} cluster")
            continue
        if len(a) == len(b):
            for i in range(len(a)):
                if a[i] == b[i]:
                    print(f"{a[i]['Test Case ID']} has no change ")
                else:
                    c =[]
                    #ctc.append(a[i]['Test Case ID'])
                    keys = list(a[i].keys())
                    for k in keys:
                        if a[i][k] == b[i][k]:
                            print(f"{a[i]['Test Case ID']} {k} has no change ")
                        elif k == "Test Procedure":
                            tp = list(a[i][k].keys())
                            print(tp)

                            for t in tp :
                                if a[i][k][t] == b[i][k][t]:
                                    print(f"{a[i]['Test Case ID']} {t} has no change ")
                                else:
                                        c.append(f"Testprocedure({t})")
                        else:
                            c.append(k)
                    ctc[a[i]['Test Case ID']]   = c                  


        elif len(a) >  len(b):
            ntc.append(cluster) 

        else:
            rtc.append(cluster) 
    dif = {}
    dif = {"addedcluster": ac, "removedcluster": rc, "chagedtc" : ctc, "addedtc" : ntc,"removedtc": rtc}

    return (dif)

def chan(dif, sheet, version):
    c = []
    if dif["addedcluster"]:
        for i in dif["addedcluster"]:
            c.append([today, version, i, "newly added cluster"])
    if dif["removedcluster"]:
        for i in dif["removedcluster"]:
            c.append([today,version, i,"this cluster is removed"])
    if dif["chagedtc"]:
        keys = list(dif["chagedtc"].keys())
        for k in keys:
            for change in dif["chagedtc"][k]:
                c.append([today,version, k,"this Testcase is modified", change])
    if dif["addedtc"]:
        for i in dif["addedtc"]:
            c.append([today,version, i,"new testcase is added to this cluster"])
    if dif["removedtc"]:
        for i in dif["removedtc"]:
            c.append([today,version, i,"Testcase is removed from this cluster"])

    print (c)

    if c:
        print(len(c))
        for h in range(len(c)):
            sheet.insert_rows(2)
        for i in range(len(c)):
            for j, value in enumerate(c[i]):                                                                                 
                sheet.cell(row=i + 2, column=j + 1, value=value)
    
    return None


if __name__ == '__main__':

        try:
            with open(json_filename, 'r') as json_file:
                existing_data = json.load(json_file)
                e = True
        except FileNotFoundError:
            existing_data = {}
            e = False

        with open (app) as f:
            soup1 = BeautifulSoup(f, 'html.parser')
            
        with open (main) as f:
            soup2 = BeautifulSoup(f, 'html.parser')

        versiontag = soup1.find ('div', class_='details')
        versiont = versiontag.find('span', id = "revnumber")
        version = versiont.text


        h1_tags1 = soup1.find_all('h1', {'id': True}) 
        h1_tags2 = soup2.find_all('h1', {'id': True})

        print(len(h1_tags1))
        if "All_TC_Details" in sheet_names:
            workbook.remove(workbook["All_TC_Details"])
            workbook.create_sheet("All_TC_Details", 0)
            sheet1 = workbook["All_TC_Details"]

        else:
            sheet1 = workbook.active
            sheet1.title = "All_TC_Details"
        
        head = ["S.no" ,"Test Plan","Cluster Name",	"TC ID","TC Name","TC Full Name"]
        sheet1.append(head)
        
        tc_details(h1_tags1,sheet1,0)
        tc_details(h1_tags2,sheet1,1)

        column_widths = {'A': 10, 'B': 20, 'C': 20 ,'D':30,'E':40,"F":50}  # Specify the column widths as desired

        for column, width in column_widths.items():
                sheet1.column_dimensions[column].width = width

        workbook.save(filename)

        with open(json_filename, 'w') as json_file:
            json.dump(current_data, json_file, indent=4)

        if e:
            dif = diff(existing_data, current_data)
            print(dif)
            if "changes" not in sheet_names:

                sheet = workbook.create_sheet("changes",1)
                sheet.append(["Date"," commit","Cluster/Testcase","Changes","Column"])
            else:
                sheet = workbook["changes"]

            chan(dif, sheet, version)

            workbook.save(filename)    
