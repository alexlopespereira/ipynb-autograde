import re
import gspread
from analysis.autograde_automata import WDFA
from automata.base.exceptions import RejectionException

SERVICE_ACCOUNT_FILE = './key/key.json'
SAMPLE_SPREADSHEET_ID = '1h0WZrH3rQOwP6XOvnfqpH_qSF6nrYTXWFNjVln-e-l8'
SAMPLE_RANGE_NAME = 'Form Responses 1!H2:I10'
gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
autograde_spreadsheet = gc.open_by_key(SAMPLE_SPREADSHEET_ID)
forms_sheet = autograde_spreadsheet.get_worksheet(0)


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
    'inc': {'f': 1, 't': 0, 'v': 1, 'i': 0},
    'te': {'f': 0, 't': 0, 'v': 0, 'i': 0}
}, initial_state='q0', final_states={'q0', 'inc', 'te'})

no_function_wdfa = WDFA(states={'q0', 'inc', 'fu'}, input_symbols={'f', 't', 'v', 'i'}, transitions={
    'q0': {'t': 'q0', 'v': 'inc', 'i': 'q0'},
    'inc': {'f': 'fu', 'v': 'inc', 'i': 'inc', 't': 'inc'},
    'fu': {'f': 'fu', 't': 'fu', 'v': 'fu', 'i': 'fu'}
}, weights={
    'q0': {'t': 0, 'v': 1, 'i': 0},
    'inc': {'f': 0, 't': 0, 'v': 1, 'i': 0},
    'fu': {'f': 0, 't': 0, 'v': 0, 'i': 0}
}, initial_state='q0', final_states={'q0', 'inc', 'fu'})

start, end = findLastRow(forms_sheet, 10, 1)
cells_range = f"A{start + 1}:I{end}"
values = forms_sheet.get(cells_range)
total_cell_list = forms_sheet.range(f"J{start + 1}:J{end}")
notest_cell_list = forms_sheet.range(f"K{start + 1}:K{end}")
nofunction_cell_list = forms_sheet.range(f"L{start + 1}:L{end}")

for i, row in enumerate(values):
    if len(row) < 8:
        continue
    input_data = re.findall("(#+\s+[Ff]a[cc]a )(.*)(testes|função|validação|import)(.*)(\d{1,2}\.\d{1,2})?(\n)", row[7])
    if bool(input_data) and len(input_data[0]) == 6:
        actions = "".join(map(lambda x, y: x[2][0] if x[4] == y else "", input_data, [input_data[0][4]] * len(input_data)))
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


forms_sheet.update_cells(total_cell_list)
forms_sheet.update_cells(notest_cell_list)
forms_sheet.update_cells(nofunction_cell_list)
