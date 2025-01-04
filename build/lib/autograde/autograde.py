import sys
from datetime import datetime
import requests
import time
from requests.utils import quote
import types
import numpy as np
import pandas as pd
import os
from IPython import get_ipython


def get_support_data():
    from autograde.defs import datasets

    course = os.getenv("COURSE")
    if course is None:
        print("Execute a célula que define o nome do curso. Exemplo: %env COURSE nome_curso", sys.stderr)
        return False, False
    ip = get_ipython()
    student_email = ip.getoutput("gcloud config get-value account")[0]
    token = ip.getoutput("gcloud auth print-access-token")[0]
    return course, student_email, token


def get_data(answers_status, exercise_number):
    from autograde.defs import datasets

    course = os.getenv("COURSE")
    if course is None:
        print("Execute a célula que define o nome do curso. Exemplo: %env COURSE nome_curso", sys.stderr)
        return False, False
    log_url, log_data_fields = datasets[course]["LOG_URL"].replace("|||", "=").split("&__data__")
    results_url = datasets[course]["RESULTS_URL"].replace("|||", "=")
    ip = get_ipython()
    student_email = ip.getoutput("gcloud config get-value account")[0]

    if answers_status:
        exercise_score = True
        log_url = f"{log_url}&emailAddress={quote(str(student_email))}"
        results_url = results_url.replace("__exercisenumber__", exercise_number.replace(".", "_"))\
                      .replace("__exercisescore__", str(exercise_score))\
                      .replace("__id__", f"{student_email}_{exercise_number}")
        request_url = f"{results_url}&emailAddress={quote(str(student_email))}"
        ret(request_url)
        log_url = log_url.replace("__exercisenumber__", exercise_number.replace(".", "_"))
        log_field, error_field = log_data_fields.split("&")
        current_log, current_errors = get_current_log_errors(ip)
        log_data = {log_field.split("=")[0]: current_log, error_field.split("=")[0]: current_errors}
        ret(log_url, log_data)
        return True, True
    else:
        return False, True


def ret(url, data=None):
    count = 0
    while count < 3:
        count += 1
        try:
            r = requests.post(url, data=data)
            break
        except:
            print("Error Occured!")
            time.sleep(2)


def get_current_log_errors(ip):
    global session_log
    if os.path.exists("./.commands"):
        os.remove("./.commands")
    ip.magic("history -o -f ./.commands")

    with open(".commands") as file:
        current_log = file.read()
    try:
        if not session_log:
            session_log = ""
    except:
        session_log = ""

    with open(".errors") as file:
        current_errors = file.read()
    open('.errors', 'w').close()
    tmp_log = f"{current_log}"
    current_log = current_log.replace(session_log, "")
    session_log = tmp_log
    return current_log, current_errors


def print_test_results(result):
    """
    Prints the test case results to the student, indicating which test cases passed and which did not.

    :param result: Dictionary containing the result data.
    """
    print(f"Codigo gerado: \n{result}")
    print(f"Codigo gerado: \n{result['code']}")

    # Check if there's only one test case
    if len(result["test_results"]) == 1:
        test = result["test_results"][0]
        if test["passed"]:
            print("\n✅ Passed the Test Case!")
            print(f"  Expected: {test['expected']}")
            print(f"  Delivered: {test['actual']}")
        else:
            print("\n❌ Failed the Test Case:")
            print(f'  Expected: {test["expected"]}')
            if test["actual"] is None or not test["actual"]:
                print(f'  Error: {test["error"]}')
            else:
                print(f'  Delivered: {test["actual"]}')

    else:
        # Separate passed and failed tests
        passed_tests = [test for test in result["test_results"] if test["passed"]]
        failed_tests = [test for test in result["test_results"] if not test["passed"]]

        # Print passed tests with details
        if passed_tests:
            print("\n✅ Passed Test Cases:")
            for test in passed_tests:
                print(f"  - Test ID: {test['testcase_id']}: {test['expected']}")
        else:
            print("\n✅ No tests passed.")

        # Print failed tests with detailed information
        if failed_tests:
            print("\n❌ Failed Test Cases:")
            for test in failed_tests:
                print(f"  - Test ID: {test['testcase_id']}")
                print(f"    Expected: {test['expected']}")
                if test["actual"] is None:
                    print(f"    Error while running the code: {test['error']}")
                else:
                    print(f"    Delivered: {test['actual']}")
        #else:
        #    print("\n❌ No tests failed.")


def validate(user_prompt, exercise_number):
    """
    :param user_prompt: Prompt describing the function
    :param exercise_number: Number of the exercise for submission
    :return:
    """

    course, email, token = get_support_data()
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(
        "https://seal-app-pmncf.ondigitalocean.app/api/validate",
        headers=headers,
        json={
                "prompt": user_prompt,
                "function_id": exercise_number,
                "user_email": email,
                "course": course
            }
        )

    if response.status_code >= 400:
        print(f"Error: {response.status_code} - {response.reason}")
        print("Details:", response.text)
    else:
        print_test_results(response.json())
        # print("Server Response:", response.json())


def init_log():
    ip = get_ipython()
    if not hasattr(ip, '_showtraceback_orig'):
        my_stderr = sys.stderr = open('.errors', 'w')
        ip._showtraceback_orig = ip._showtraceback

        def _showtraceback(self, etype, evalue, stb):
            my_stderr.write(datetime.now().strftime('\n' + "%m/%d/%Y, %H:%M:%S") + '\n')
            my_stderr.write(self.InteractiveTB.stb2text(stb) + '\n')
            my_stderr.flush()
            self._showtraceback_orig(etype, evalue, stb)

        ip._showtraceback = types.MethodType(_showtraceback, ip)


def gether_data(path):
    if not path:
        return None
    df_lista = [pd.read_csv(f, encoding='iso8859-1', skiprows=3, sep=';', engine='python') for f in path]
    df_concat = pd.concat(df_lista, ignore_index=True)
    return df_concat


def explode_and_merge(df, col, merge_on='id', split_on=";"):
    if df is None:
        return
    df_exp = df[[col, merge_on]].assign(**{col: df[col].str.split(split_on)}).explode(col)
    df_merged = df_exp.merge(right=df, on=merge_on, how='left', suffixes=["", "_y"])
    del df_merged[col+"_y"]
    return df_merged


def change_pct(df):
    if df is None:
        return
    df_reset = df.reset_index()
    df_reset['ontem'] = df_reset['date'].apply(lambda x: x + datetime.timedelta(days=1))
    df_merge = df_reset.merge(right=df_reset, left_on=['symbol','date'],
                              right_on=['symbol','ontem'], suffixes=["", "_desloc"])
    df_merge['change_pct'] = (df_merge['close'] - df_merge['close_desloc']) / df_merge['close_desloc']
    df_pivot = df_merge.pivot('date', 'symbol', 'change_pct')
    return df_pivot

if __name__ == "__main__":
    validate("crie uma função que recebe dois argumentos numericos e retorna a soma deles", "A2-E1")