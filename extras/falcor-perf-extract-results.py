import os
import sys
import re
import time
import json
import argparse
import subprocess
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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

raw_data_sheet = client.open("Falcor Nightly Perf Results").sheet1
raw_data_records = raw_data_sheet.get_all_records()
raw_data_index = len(raw_data_records) + 2
averages_sheet = client.open("Falcor Nightly Perf Results").worksheet("Averages")
averages_records = averages_sheet.get_all_records()
averages_index = len(averages_records) + 2
recent_sheet = client.open("Falcor Nightly Perf Results").worksheet("Recent")
recent_records = recent_sheet.get_all_records()
recent_index = len(recent_records) + 2

res_dict = {}
cmd = sys.argv[1]
proc_env = os.environ.copy()
proc_env["PATH"] = proc_env["PATH"] + ";" + sys.argv[2]
program_version_creation_glslang = []
program_version_creation_slang = []
program_kernel_creation_glslang = []
program_kernel_creation_slang = []
frontend_execution_glslang = []
frontend_execution_slang = []
spirv_generation_glslang = []
spirv_generation_slang = []
spirv_compilation_glslang = []
spirv_compilation_slang = []
sheet_row = []
row_date = time.strftime(r"%Y%m%d%H%M%S", time.localtime()) 
rtn_json = {}

for i in range(10):
    results_id = time.strftime(r"%Y%m%d%H%M%S", time.localtime()) 
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True,
                           env=proc_env)
    stdout, stderr = proc.communicate()
    with open("zysk"+results_id+".txt", "w") as fh:
        fh.write("cmd: " + cmd + "\n")
        fh.write("proc_env: " + proc_env + "\n")
        fh.write("stdout: " + stdout + "\n")
        fh.write("stderr: " + stderr + "\n")
    retcode = proc.returncode
    res_dict[results_id] = stdout

for key in res_dict.keys():
    data = res_dict[key]
    results_id = key
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
    rtn_json[results_id]["program-version-creation"] = {pvc[0][1]: float(pvc[0][2]), pvc[1][1]: float(pvc[1][2])}
    rtn_json[results_id]["program-kernel-creation"] = {pkc[0][1]: float(pkc[0][2]), pkc[1][1]: float(pkc[1][2])}
    rtn_json[results_id]["frontend-execution"] = {"glslang": float(fe[0]), "slang": float(fe[1])}
    rtn_json[results_id]["spirv-generation"] = {sg[0][1]: float(sg[0][2]), sg[1][1]: float(sg[1][2])}
    rtn_json[results_id]["spirv-compilation"] = {sc[0][1]: float(sc[0][2]), sc[1][1]: float(sc[1][2])}
    program_version_creation_glslang.append(float(rtn_json[results_id]["program-version-creation"]["glslang"]))
    program_version_creation_slang.append(float(rtn_json[results_id]["program-version-creation"]["slang"]))
    program_kernel_creation_glslang.append(float(rtn_json[results_id]["program-kernel-creation"]["glslang"]))
    program_kernel_creation_slang.append(float(rtn_json[results_id]["program-kernel-creation"]["slang"]))
    frontend_execution_glslang.append(float(rtn_json[results_id]["frontend-execution"]["glslang"]))
    frontend_execution_slang.append(float(rtn_json[results_id]["frontend-execution"]["slang"]))
    spirv_generation_glslang.append(float(rtn_json[results_id]["spirv-generation"]["glslang"]))
    spirv_generation_slang.append(float(rtn_json[results_id]["spirv-generation"]["slang"]))
    spirv_compilation_glslang.append(float(rtn_json[results_id]["spirv-compilation"]["glslang"]))
    spirv_compilation_slang.append(float(rtn_json[results_id]["spirv-compilation"]["slang"]))

if len(recent_records) > 29:
    cell_list = recent_sheet.range("A2:L31")
    j = 0

    for i in range(len(recent_records) - 29, len(recent_records)):
        for key in recent_records[i].keys():
            cell_list[j].value = recent_records[i][key]
            j += 1

    date_format = "%Y%m%d%H%M%S" 
    date_obj = datetime.strptime(row_date, date_format)

    cell_list[j].value = date_obj.strftime("%Y-%m-%d")
    j += 1
    cell_list[j].value = github_sha
    j += 1
    cell_list[j].value = sum(program_version_creation_glslang)/len(program_version_creation_glslang)
    j += 1
    cell_list[j].value = sum(program_version_creation_slang)/len(program_version_creation_slang)
    j += 1
    cell_list[j].value = sum(program_kernel_creation_glslang)/len(program_kernel_creation_glslang)
    j += 1
    cell_list[j].value = sum(program_kernel_creation_slang)/len(program_kernel_creation_slang)
    j += 1
    cell_list[j].value = sum(frontend_execution_glslang)/len(frontend_execution_glslang)
    j += 1
    cell_list[j].value = sum(frontend_execution_slang)/len(frontend_execution_slang)
    j += 1
    cell_list[j].value = sum(spirv_generation_glslang)/len(spirv_generation_glslang)
    j += 1
    cell_list[j].value = sum(spirv_generation_slang)/len(spirv_generation_slang)
    j += 1
    cell_list[j].value = sum(spirv_compilation_glslang)/len(spirv_compilation_glslang)
    j += 1
    cell_list[j].value = sum(spirv_compilation_slang)/len(spirv_compilation_slang)
    j += 1
    recent_sheet.update_cells(cell_list)

date_format = "%Y%m%d%H%M%S" 
date_obj = datetime.strptime(row_date, date_format)

sheet_row.append(date_obj.strftime("%Y-%m-%d"))
sheet_row.append(github_sha)
sheet_row.append(sum(program_version_creation_glslang)/len(program_version_creation_glslang))
sheet_row.append(sum(program_version_creation_slang)/len(program_version_creation_slang))
sheet_row.append(sum(program_kernel_creation_glslang)/len(program_kernel_creation_glslang))
sheet_row.append(sum(program_kernel_creation_slang)/len(program_kernel_creation_slang))
sheet_row.append(sum(frontend_execution_glslang)/len(frontend_execution_glslang))
sheet_row.append(sum(frontend_execution_slang)/len(frontend_execution_slang))
sheet_row.append(sum(spirv_generation_glslang)/len(spirv_generation_glslang))
sheet_row.append(sum(spirv_generation_slang)/len(spirv_generation_slang))
sheet_row.append(sum(spirv_compilation_glslang)/len(spirv_compilation_glslang))
sheet_row.append(sum(spirv_compilation_slang)/len(spirv_compilation_slang))
averages_sheet.insert_row(sheet_row, averages_index)
if len(recent_records) <= 29:
    recent_sheet.insert_row(sheet_row, recent_index)

for date_key in rtn_json.keys():
    sheet_row = []
    sheet_row.append(str(date_key))
    sheet_row.append(github_sha)
    for result_key in rtn_json[date_key].keys():
        for flow_key in rtn_json[date_key][result_key].keys():
            sheet_row.append(rtn_json[date_key][result_key][flow_key])
    raw_data_sheet.insert_row(sheet_row, raw_data_sheet_index)
    raw_data_sheet_index += 1
