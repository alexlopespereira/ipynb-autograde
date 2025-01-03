import re
import gspread
from analysis.autograde_automata import WDFA
from automata.base.exceptions import RejectionException
import pandas as pd
from operator import itemgetter
import sys
from autograde.defs import datasets

SERVICE_ACCOUNT_FILE = './analysis/key/key.json'
# ENAP_ESP_SPREADSHEET_ID = '1h0WZrH3rQOwP6XOvnfqpH_qSF6nrYTXWFNjVln-e-l8'
# SGD_TRIBO_SPREADSHEET_ID = '1OVxeKMyzPdPO80A-xBm8sGW3-bDz5k-vERvoet-IXQ0'
SAMPLE_RANGE_NAME = 'Form Responses 1!H2:I10'



def findLastRow(worksheet, col1, col2=None):
    n1 = len(worksheet.col_values(col1))
    if col2:
        n2 = len(worksheet.col_values(col2))
        return n1, n2
    else:
        return n1


Q0F = 5; Q0T = 1; Q0V = 5; Q0I = 0
IMF = 3; IMT = 1; IMV = 5; IMI = 0
FUF = 3; FUT = 1; FUV = 1; FUI = 0
TEF = 1; TET = 1; TEV = 6; TEI = 0
VAF = 2; VAT = 1; VAV = 2; VAI = 0

total_wdfa = WDFA(states={'q0', 'fu', 'te', 'va', 'im'}, input_symbols={'f', 't', 'v', 'i'}, transitions={
    'q0': {'f': 'fu', 't': 'te', 'v': 'va', 'i': 'im'},
    'im': {'f': 'fu', 't': 'te', 'v': 'va', 'i': 'im'},
    'fu': {'f': 'fu', 't': 'te', 'v': 'va', 'i': 'im'},
    'te': {'f': 'fu', 't': 'te', 'v': 'va', 'i': 'im'},
    'va': {'f': 'fu', 't': 'te', 'v': 'va', 'i': 'va'},
}, weights={
    'q0': {'f': Q0F, 't': Q0T, 'v': Q0V, 'i': Q0I},
    'im': {'f': IMF, 't': IMT, 'v': IMV, 'i': IMI},
    'fu': {'f': FUF, 't': FUT, 'v': FUV, 'i': FUI},
    'te': {'f': TEF, 't': TET, 'v': TEV, 'i': TEI},
    'va': {'f': VAF, 't': VAT, 'v': VAV, 'i': VAI}
}, initial_state='q0', final_states={'q0', 'fu', 'te', 'va', 'im'})

no_test_wdfa = WDFA(states={'q0', 'inc', 'te'}, input_symbols={'f', 't', 'v', 'i'}, transitions={
    'q0': {'f': 'inc', 'v': 'inc', 'i': 'q0'},
    'inc': {'f': 'inc', 'v': 'inc', 'i': 'inc', 't': 'te'},
    'te': {'f': 'te', 't': 'te', 'v': 'te', 'i': 'te'}
}, weights={
    'q0': {'f': 1, 'v': 1, 'i': 0},
    'inc': {'f': 0, 't': 0, 'v': 0, 'i': 0},
    'te': {'f': 0, 't': 0, 'v': 0, 'i': 0}
}, initial_state='q0', final_states={'q0', 'inc', 'te'})

no_function_wdfa = WDFA(states={'q0', 'inc', 'fu'}, input_symbols={'f', 't', 'v', 'i'}, transitions={
    'q0': {'t': 'q0', 'v': 'inc', 'i': 'q0'},
    'inc': {'f': 'fu', 'v': 'inc', 'i': 'inc', 't': 'inc'},
    'fu': {'f': 'fu', 't': 'fu', 'v': 'fu', 'i': 'fu'}
}, weights={
    'q0': {'t': 0, 'v': 1, 'i': 0},
    'inc': {'f': 0, 't': 0, 'v': 0, 'i': 0},
    'fu': {'f': 0, 't': 0, 'v': 0, 'i': 0}
}, initial_state='q0', final_states={'q0', 'inc', 'fu'})


def update_errors_spreadsheet(spreadsheet_id, service_account_file):
    gc = gspread.service_account(filename=service_account_file)
    autograde_spreadsheet = gc.open_by_key(spreadsheet_id)
    forms_sheet = autograde_spreadsheet.get_worksheet(0)
    errors_sheet = autograde_spreadsheet.get_worksheet(1)

    start, end = findLastRow(forms_sheet, 10, 1)
    start = max(start,1)
    cells_range = f"A{start + 1}:I{end}"
    values = forms_sheet.get(cells_range)
    total_cell_list = forms_sheet.range(f"J{start + 1}:J{end}")
    notest_cell_list = forms_sheet.range(f"K{start + 1}:K{end}")
    nofunction_cell_list = forms_sheet.range(f"L{start + 1}:L{end}")
    df_error_list = []
    for i, row in enumerate(values):
        if len(row) < 8:
            continue
        log_input_data = re.findall("(#+\s+[Ff]a[cc]a )(.*)(testes|função|validação|import)(.*)(\d{1,2}\.\d{1,2})?(\n)", row[7])
        if bool(log_input_data) and len(log_input_data[0]) == 6:
            actions = "".join(map(lambda x, y: x[2][0] if x[4] == y else "", log_input_data, [log_input_data[0][4]] * len(log_input_data)))
            total_wdfa.reset()
            no_test_wdfa.reset()
            no_function_wdfa.reset()
            try:
                total_cell_list[i].value = total_wdfa.read_input(actions)[1]
            except RejectionException as e:
                pass
            try:
                notest_cell_list[i].value = no_test_wdfa.read_input(actions)[1]
            except RejectionException as e:
                pass
            try:
                nofunction_cell_list[i].value = no_function_wdfa.read_input(actions)[1]
            except RejectionException as e:
                pass

        if len(row) > 8:
            exclude_patterns = [".*Traceback.*\n?", "\/usr\/local\/lib\/python", "ipython-input", "(\[0m.*){4}"]
            current_error_data = row[8]
            for e in exclude_patterns:
                current_error_data = re.sub(e, "", current_error_data)
            error_input_data = re.findall("(\[\d+;\d+m)(.*Error)(\[\d+m?.*m\:(\[.*m)?\s?)(.*)(\n)", current_error_data)
            df_errors = pd.DataFrame(data=[row[0:7]]*len(error_input_data))
            df_errors[['category','subcategory']] = [itemgetter(1, 4)(l) for l in error_input_data]
            df_errors[9] = df_errors['subcategory'].str.extract(".*'(.*)'").fillna("")
            df_error_list.append(df_errors)

    forms_sheet.update_cells(total_cell_list)
    forms_sheet.update_cells(notest_cell_list)
    forms_sheet.update_cells(nofunction_cell_list)
    df_errors = pd.concat(df_error_list)
    error_values = df_errors.values.tolist()
    errors_sheet.append_rows(error_values)


if __name__ == '__main__':
    course_name = sys.argv[1]
    spreadsheet_id = datasets[course_name]['errors_spreadsheet_id']
    update_errors_spreadsheet(spreadsheet_id, SERVICE_ACCOUNT_FILE)
