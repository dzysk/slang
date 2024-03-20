import os, sys, re, time, json, argparse
import gspread
from oauth2client.service_account import ServiceAccountCredentials

try:
    # Open file containing stdout of results
    with open(sys.argv[1], "rt", encoding="utf-16") as fp:
        data = fp.read()
    # Unique ID for the current test results. Format: YYYYmmddHHMMSS (YearMonthDayHourMinuteSecond)
    results_id = time.strftime(r"%Y%m%d%H%M%S", time.localtime()) 
    rtn_json = {}
    rtn_json[results_id] = {}
    pvc = re.findall(r"(?<=Time for program version creation )(\((glslang|slang)\): ([0-9]*\.[0-9][0-9][0-9]))", data)  # Program version creation
    pkc = re.findall(r"(?<=Time for program kernel creation )(\((glslang|slang)\): ([0-9]*\.[0-9][0-9][0-9]))", data)   # Program kernel creation
    fe = re.findall(r"(?<=Time for frontend execution:)([0-9]*\.[0-9][0-9][0-9])", data)                                # Frontend execution
    sg = re.findall(r"(?<=Time for spirv generation by )((glslang|slang): ([0-9]*\.[0-9][0-9][0-9]))", data)            # Spirv generation
    sc = re.findall(r"(?<=Time for compiling spirv generated by )((glslang|slang): ([0-9]*\.[0-9][0-9][0-9]))", data)   # Spirv compilation

    rtn_json[results_id]["program-version-creation"] = {pvc[0][1]: float(pvc[0][2]), pvc[1][1]: float(pvc[1][2])}
    rtn_json[results_id]["program-kernel-creation"] = {pkc[0][1]: float(pkc[0][2]), pkc[1][1]: float(pkc[1][2])}
    rtn_json[results_id]["frontend-execution"] = {"glslang": float(fe[0]), "slang": float(fe[1])}
    rtn_json[results_id]["spirv-generation"] = {sg[0][1]: float(sg[0][2]), sg[1][1]: float(sg[1][2])}
    rtn_json[results_id]["spirv-compilation"] = {sc[0][1]: float(sc[0][2]), sc[1][1]: float(sc[1][2])}
except:
    exit(1)

scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file'
        ]

github_sha = os.environ[ 'github_sha' ]
creds_str = os.environ[ 'slang_verif_svc' ]

creds_dict = eval(creds_str)

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open("Falcor Nightly Perf Results").sheet1
python_sheet = sheet.get_all_records()

num_rows = len(python_sheet)

sheet_row = []
sheet_index = num_rows + 2
    
for date_key in rtn_json.keys():
    sheet_row.append(str(date_key))
    sheet_row.append(github_sha)
    for result_key in rtn_json[date_key].keys():
        for flow_key in rtn_json[date_key][result_key].keys():
            sheet_row.append(rtn_json[date_key][result_key][flow_key])

sheet.insert_row(sheet_row, sheet_index)
