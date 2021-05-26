import re
import gspread
from analysis.autograde_automata import WDFA

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

#TODO: criar variaveis para os pesos das transicoes
total_wdfa = WDFA(states={'q0', 'fu', 'te', 'va', 'im'}, input_symbols={'f', 't', 'v', 'i'}, transitions={
    'q0': {'f': 'fu', 't': 'te', 'v': 'va', 'i': 'im'},
    'im': {'f': 'fu', 't': 'te', 'v': 'va', 'i': 'im'},
    'fu': {'f': 'fu', 't': 'te', 'v': 'va', 'i': 'im'},
    'te': {'f': 'fu', 't': 'te', 'v': 'va', 'i': 'im'},
    'va': {'f': 'fu', 't': 'te', 'v': 'va', 'i': 'im'},
}, weights={
    'q0': {'f': 5, 't': 1, 'v': 5, 'i': 0},
    'im': {'f': 3, 't': 0, 'v': 5, 'i': 0},
    'fu': {'f': 2, 't': 1, 'v': 1, 'i': 1},
    'te': {'f': 1, 't': 0, 'v': 6, 'i': 1},
    'va': {'f': 2, 't': 1, 'v': 2, 'i': 1}
},
                  initial_state='q0', final_states={'q0', 'fu', 'te', 'va', 'im'})

no_import_wdfa = WDFA(states={'q0', 'fu', 'te', 'va'}, input_symbols={'f', 't', 'v'}, transitions={
    'q0': {'f': 'fu', 't': 'te', 'v': 'va'},
    'fu': {'f': 'fu', 't': 'te', 'v': 'va'},
    'te': {'f': 'fu', 't': 'te', 'v': 'va'},
    'va': {'f': 'fu', 't': 'te', 'v': 'va'},
}, weights={
    'q0': {'f': 5, 't': 1, 'v': 5},
    'fu': {'f': 2, 't': 1, 'v': 1},
    'te': {'f': 1, 't': 0, 'v': 6},
    'va': {'f': 2, 't': 1, 'v': 2}
},
                      initial_state='q0', final_states={'q0', 'fu', 'te', 'va'})

no_test_wdfa = WDFA(states={'q0', 'fu', 'va', 'im'}, input_symbols={'f', 'v', 'i'}, transitions={
    'q0': {'f': 'fu', 'v': 'va', 'i': 'im'},
    'im': {'f': 'fu', 'v': 'va', 'i': 'im'},
    'fu': {'f': 'fu', 'v': 'va', 'i': 'im'},
    'va': {'f': 'fu', 'v': 'va', 'i': 'im'},
}, weights={
    'q0': {'f': 5, 't': 1, 'v': 5, 'i': 0},
    'im': {'f': 3, 't': 0, 'v': 5, 'i': 0},
    'fu': {'f': 2, 't': 1, 'v': 1, 'i': 1},
    'va': {'f': 2, 't': 1, 'v': 2, 'i': 1}
},
                  initial_state='q0', final_states={'q0', 'fu', 'va', 'im'})

start, end = findLastRow(forms_sheet, 10, 1)
cells_range = f"A{start + 1}:I{end}"
values = forms_sheet.get(cells_range)
cell_list = forms_sheet.range(f"J{start + 1}:J{end}")

for i, row in enumerate(values):
    if len(row) < 8:
        continue
    input_data = re.findall("(# Faca )(.*)(testes|função|validação|import)(.*)(\d{1,2}\.\d{1,2})(\n)", row[7])
    if bool(input_data) and len(input_data[0]) == 6:
        actions = "".join(map(lambda x, y: x[2][0] if x[4] == y else "", input_data, [input_data[0][4]] * len(input_data)))
        total_wdfa.reset()
        cost = total_wdfa.read_input(actions)[1]
        cell_list[i].value = cost

forms_sheet.update_cells(cell_list)
