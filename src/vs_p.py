from bs4 import BeautifulSoup
import openpyxl
from openpyxl import load_workbook
from joblib import Parallel, delayed
import re
import datetime
import pandas as pd
import json

today = datetime.date.today().strftime('%Y-%m-%d')
filename = f"test_plan_change.xlsx"



try:
    workbook = load_workbook(filename)
except FileNotFoundError:
    workbook = openpyxl.Workbook()

sheet_names = workbook.sheetnames

app = '/home/grl/Downloads/allclusters (4).html'
main = '/home/grl/Downloads/index (5).html'
#app = '/home/grl/Downloads/Matter.Allclusters.Test.Plan.V1.2.html'
#main = '/home/grl/Downloads/Matter.Core.Test.Plan.V1.2.html'

json_filename = 'TC_Summary.json'


def tc_id (head):
    testcase1 = re.search(r'\[(.*?)\]',head)
    if testcase1:
        matched_str = testcase1.group()  # Extract the matched substring
        testcase = re.sub(r'\[|\]', '', matched_str)

    return testcase

def tc(h4_tag, tp):
    d = {}
    headt= h4_tag.text

    d["Test Case Name"] = headt
    d["Test Case ID"] = tc_id(headt)
    d["Test Plan"] = tp

    pur_tag = h4_tag.find_next('h5', {'id': lambda x: x and x.startswith('_purpose')})
    pur = pur_tag.find_next('p')
    purt =pur.text

    d["Purpose"] = purt

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

        d["PICS"].append(pt)

    pre_tag = h4_tag.find_next('h5', {'id': lambda x: x and x.startswith('_preconditions')})
    if pre_tag:
        d["Pre-condition"] = {}
        table = pre_tag.find_next('table')
        if table:
            data_dict = create_df(table)
        if data_dict:
            d["Pre-condition"] = data_dict
                        
    else:
            
            d["Pre-condition"] = "Nil"

    h5_tags = h4_tag.find_next('h5', {'id': lambda x: x and x.startswith('_test_procedure')}) 
    if h5_tags:
        None
    else:
        h5_tags = h4_tag.find_next('h6', {'id': lambda x: x and x.startswith('_test_procedure')}) 
    table = h5_tags.find_next('table')
    data_dict =   create_df(table)
    d["Test Procedure"] = data_dict
    
    workbook.save(filename)

    return headt , d


def tc_details (h_tag,a,s_h1):
        
        
        if a == 0:
            tp = "App Test Case"
            html = app
        else:
            tp = "Core Test Case" 
            html = main

        with open (html) as f:
            soup = BeautifulSoup(f, 'lxml')
        
        h1_tags = soup.find_all('h1', {'id': True})
        
        for tag in h1_tags:
            tag_text = tag.text
            if tag_text == h_tag:
                h1_tag = tag
            
        
        if s_h1:
            for tag in h1_tags:
                tag_text = tag.text
                if tag_text == s_h1:
                    second_h1 = tag
                

        else:
            second_h1 = False

        h1 = h1_tag.text
        cluster_name =  h1.replace(' Cluster Test Plan', '') \
            .replace(' Cluster TestPlan', '') \
            .replace(' Cluster', '') \
            .replace(' cluster', '') \
            .replace(' Test Plan', '')

        if h1 == "MCORE PICS Definition":
            return None


        clus = []

        first_h1 = h1_tag  # Select the first h1 tag in the pair

            
        # Find all h5 tags after the first h1 tag with id starting with the value
        h5_tags = first_h1.find_all_next(['h5','h6'], {'id': lambda x: x and x.startswith('_test_procedure')})  

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
                    headt, d = tc(h4_tag, tp)
                    clus.append(d)
                    heads.append(headt)

        else:
                h5_tags = first_h1.find_all_next(['h5','h6'], {'id': lambda x: x and x.startswith('_test_procedure')})  

                for h5_tag in h5_tags:
                    if h5_tag.find_previous('h1') == first_h1:
                        if h5_tag.find_next('h1') == second_h1:
                            result.append(h5_tag)
                
                heads =[]
                for h5_tag in result:
                    h4_tag = h5_tag.find_previous('h5')
                    headt , d = tc(h4_tag, tp)
                    clus.append(d)
                    heads.append(headt)


        return {cluster_name:clus}


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
    return(data_dict)

def diff(existing_data, updated_data):
    nc = list(updated_data.keys())
    oc = list(existing_data.keys())

    ac = list(set(nc).difference(set(oc)))
    rc = list(set(oc).difference(set(nc)))
    ctc = {}
    ntc =[]
    rtc =[]

    for cluster in nc:
        if cluster in ac+rc:
            continue
        a = updated_data[cluster]
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

def tpchan(dif, sheet, version):
    c = []
  
    if dif["chagedtc"]:
        keys = list(dif["chagedtc"].keys())
        for k in keys:
            for change in dif["chagedtc"][k]:
                c.append([today,version, k,"this Testcase is modified", change])
    if dif["addedcluster"]:
        for i in dif["addedcluster"]:
            c.append([today, version, i, "newly added cluster"])
    if dif["removedcluster"]:
        for i in dif["removedcluster"]:
            c.append([today,version, i,"this cluster is removed"])
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
        

    else:
        sheet.insert_rows(2)
        value = [today,version,"Nil", f"No changes on {today} ", "Nil"]
        for i in range(0, 1):
            for j, value in enumerate(value):                                                                                 
                sheet.cell(row=i + 2, column=j + 1, value=value)
    
    return None


def tcchan(dif, sheet, version):
    c = []
  
    if dif["chagedtc"]:
        keys = list(dif["chagedtc"].keys())
        for k in keys:
            for change in dif["chagedtc"][k]:
                if change in ["Test Case Name","Test Case ID"]:
                    c.append([today,version, k,"this Testcase is modified", change])
    if dif["addedcluster"]:
        for i in dif["addedcluster"]:
            c.append([today, version, i, "newly added cluster"])
    if dif["removedcluster"]:
        for i in dif["removedcluster"]:
            c.append([today,version, i,"this cluster is removed"])
    if dif["addedtc"]:
        for i in dif["addedtc"]:
            c.append([today,version, i,"new testcase is added to this cluster"])
    if dif["removedtc"]:
        for i in dif["removedtc"]:
            c.append([today,version, i,"Testcase is removed from this cluster"])

    if c:
        print(len(c))
        for h in range(len(c)):
            sheet.insert_rows(2)
        for i in range(len(c)):
            for j, value in enumerate(c[i]):                                                                                 
                sheet.cell(row=i + 2, column=j + 1, value=value)
        

    else:
        sheet.insert_rows(2)
        value = [today,version,"Nil", f"No changes on {today} ", "Nil"]
        for i in range(0, 1):
            for j, value in enumerate(value):                                                                                 
                sheet.cell(row=i + 2, column=j + 1, value=value)

    return None

def cluster_enclose(h1_tags1):
    ce = []
    for i in range(len(h1_tags1) ):
        if i == (len(h1_tags1) -1):
            
            sh= False
        else:
            second_h1 = h1_tags1[i+1] 
            sh = second_h1.text
        ce.append(sh)
    return ce

def tcsummary(sheet1, updated_data):
    clusters = list(updated_data.keys())
    for cluster in clusters:
        tcids = updated_data[cluster][0]["Test Case ID"]
        sh = re.search(r'-(.*?)-', tcids)
        code = sh.group(1)
        if code == 'LOWPOWER':
            code = 'MC'
        sheet = workbook[code]
        sheet.append([cluster])
        sheet.append([""])

        testcases = updated_data[cluster]
        for testcase in testcases:
            tcfn = testcase["Test Case Name"]
            sheet.append([tcfn])
            sheet.append([""])
            sheet.append(["Purpose"])
            sheet.append([testcase["Purpose"]])
            sheet.append([""])
            sheet.append(["PICS"])
            for pics in testcase["PICS"]:
                sheet.append([pics])
            sheet.append([""])
            sheet.append(["Pre-condition"])
            if testcase["Pre-condition"] == "Nil":
                sheet.append(["Nil"])
            else:
                head = list(testcase["Pre-condition"].keys())
                sheet.append(head)
                for i in range(len(list(testcase["Pre-condition"].values())[0])):
                    val =[]
                    for key, value in testcase["Pre-condition"].items():
                        if i < len(value):
                            val.append(value[i]) 
                    sheet.append(val)
            sheet.append([""])
            sheet.append(["Test Procedure"])
            keys = list(testcase["Test Procedure"].keys())
            sheet.append(keys)
            for i in range(len(list(testcase["Test Procedure"].values())[0])):
                val =[]
                for key, value in testcase["Test Procedure"].items():
                    if i < len(value):
                        val.append(value[i]) 
                sheet.append(val)
            sheet.append([""])
            sheet.append([""])
            sheet.append([""])
            head_text_match = re.search(r'\[(.*?)\]\s*(.*)', tcfn)
            if head_text_match:
                    tcname = '[' + head_text_match.group(1) + '] ' + head_text_match.group(2)
            else:
                    tcname = ''
            tcid = testcase["Test Case ID"]
            tp = testcase["Test Plan"]
            n = sheet1.max_row

            value = [n , cluster ,tcname , tcid , tp ]
            sheet1.append(value)
            workbook.save(filename)

    return None


if __name__ == '__main__':  

        updated_data ={}

        try:
            with open(json_filename, 'r') as json_file:
                existing_data = json.load(json_file)
                e = True
        except FileNotFoundError:
            existing_data = {}
            e = False

        with open (app) as f:
            soup1 = BeautifulSoup(f, 'lxml')
            
        with open (main) as f:
            soup2 = BeautifulSoup(f, 'lxml')

        versiontag = soup1.find ('div', class_='details')
        versiont = versiontag.find('span', id = "revnumber")
        version = versiont.text


        h1_tags1 = soup1.find_all('h1', {'id': True}) 
        h1_tags2 = soup2.find_all('h1', {'id': True})

        h1_tags1t = []
        h1_tags2t =[]

        for tag in h1_tags1:
            tag_text = tag.text
            h1_tags1t.append(tag_text)

        for tag in h1_tags2:
            tag_text = tag.text
            h1_tags2t.append(tag_text)

        print(len(h1_tags1))
        if "All_TC_Details" in sheet_names:
            workbook.remove(workbook["All_TC_Details"])
            workbook.create_sheet("All_TC_Details", 0)
            sheet1 = workbook["All_TC_Details"]

        else:
            sheet1 = workbook.active
            sheet1.title = "All_TC_Details"
        
        head = ["S.no" ,"Cluster Name","Test Case Name","Test Case ID"," Test Plan "]
        sheet1.append(head)
        
        ce1 = cluster_enclose(h1_tags1)
        print(ce1)
       
        if len(ce1) == len(h1_tags1):
            input_data = []
            for i in range(len(ce1)):
                a = (h1_tags1t[i],0,ce1[i])
                input_data.append(a)
            print(input_data)

            results =Parallel(n_jobs=-1)(delayed(tc_details)(a, b, c) for a, b, c in input_data)

            for result in results:
                if result is not None:
                    updated_data.update(result)


        else:
            print("fail")
     
        ce2 = cluster_enclose(h1_tags2)

        if len(ce2) == len(h1_tags2):
            input_data = []
            for i in range(len(ce2)):
                a = (h1_tags2t[i],1,ce2[i])
                input_data.append(a)

            results = Parallel(n_jobs=-1)(delayed(tc_details)(a, b, c) for a, b, c in input_data)

            for result in results:
                if result is not None:
                    updated_data.update(result)
                        
        else:
            print("fail")

        codes = []
        clusters = list(existing_data.keys())

        for test in updated_data:
            tcid = updated_data[test][0]["Test Case ID"]
            sh = re.search(r'-(.*?)-', tcid)
            code = sh.group(1)
            if code == 'LOWPOWER':
                code = 'MC'

            codes.append(code)

        for code in codes:
            if code in sheet_names:
                workbook.remove(workbook[code])
                workbook.create_sheet(code, sheet_names.index(code))
                

            else:
                workbook.create_sheet(code)
    
        tcsummary(sheet1, updated_data)

        if e:
            dif = diff(existing_data, updated_data)
            print(dif)
            if "Test_plan_Changes" not in sheet_names:

                sheet = workbook.create_sheet("Test_plan_Changes",2)
                sheet.append(["Date of Run"," Commit","Cluster/Testcase","Changes","Column"])
            else:
                sheet = workbook["Test_plan_Changes"]

            tpchan(dif, sheet, version)

            print(dif)
            if "Test_Summary_Changes" not in sheet_names:

                sheet = workbook.create_sheet("Test_Summary_Changes",1)
                sheet.append(["Date of Run"	, "Cluster Name",	"Test Case Name",	"Test Case ID",	"Test Plan",	"Change Type"])

            else:
                sheet = workbook["Test_Summary_Changes"]

            tcchan(dif, sheet, version)

        column_widths = {'A': 10, 'B': 20, 'C': 50 ,'D':30,'E':30}  # Specify the column widths as desired

        for column, width in column_widths.items():
                sheet1.column_dimensions[column].width = width

        workbook.save(filename)

        with open(json_filename, 'w') as json_file:
                json.dump(updated_data, json_file, indent=4)

        workbook.save(filename)    
