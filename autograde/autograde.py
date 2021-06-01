import sys
from datetime import datetime
import requests
import time
from requests.utils import quote
import types
import numpy as np
import pandas as pd
import os


def send_form(url, data=None):
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
    if os.path.exists("./history.txt"):
        os.remove("./history.txt")
    ip.magic("history -o -f ./history.txt")

    with open("history.txt") as file:
        current_log = file.read()
    try:
        if not session_log:
            session_log = ""
    except:
        session_log = ""

    with open("errors.txt") as file:
        current_errors = file.read()
    # Clear errors
    open('errors.txt', 'w').close()

    tmp_log = f"{current_log}"
    current_log = current_log.replace(session_log, "")
    session_log = tmp_log
    return current_log, current_errors


def validate(func, inputs, outfunc, outputs, exercise_number):
    import os
    log_url, log_data_fields = os.getenv("log_url").replace("|||", "=").split("&__data__")
    results_url = os.getenv("results_url").replace("|||", "=")
    ip = get_ipython()
    student_email = ip.getoutput("gcloud config get-value account")[0]
    answers_status = True
    for k, v in zip(inputs, outputs):
        ans = func(*k)
        outans = outfunc(ans)
        try:
            if isinstance(ans, pd.DataFrame) and isinstance(v, pd.DataFrame):
                result = outans.equals(v)
            elif (isinstance(ans, np.ndarray) or isinstance(outans, np.ndarray)) and isinstance(v, np.ndarray):
                result = np.array_equal(outans, v)
            else:
                result = outfunc(ans) == v
            if not result:
                answers_status = False
                validate_output = f"Resposta incorreta. {func.__name__}({k}) deveria ser {v}, mas retornou {ans}"
        except ValueError as ve:
            print(ve)
            pass
            if not result.all():
                answers_status = False
                validate_output = f"Resposta incorreta. {func.__name__}({k}) deveria ser {v}, mas retornou {ans}"

    if answers_status:
        exercise_score = True
        log_url = f"{log_url}&emailAddress={quote(str(student_email))}"
        results_url = results_url.replace("__exercisenumber__", exercise_number.replace(".", "_"))\
                      .replace("__exercisescore__", str(exercise_score))\
                      .replace("__id__", f"{student_email}_{exercise_number}")
        request_url = f"{results_url}&emailAddress={quote(str(student_email))}"
        send_form(request_url)
        log_url = log_url.replace("__exercisenumber__", exercise_number.replace(".", "_"))
        log_field, error_field = log_data_fields.split("&")
        current_log, current_errors = get_current_log_errors(ip)
        log_data = {log_field.split("=")[0]: current_log, error_field.split("=")[0]: current_errors}
        send_form(log_url, log_data)
        return True, "Parabéns!"
    else:
        return False, validate_output


# This saves all errors to a file called errors.txt
def init_log():
    ip = get_ipython()
    if not hasattr(ip, '_showtraceback_orig'):
        my_stderr = sys.stderr = open('errors.txt', 'w')  # redirect stderr to file
        ip._showtraceback_orig = ip._showtraceback

        def _showtraceback(self, etype, evalue, stb):
            my_stderr.write(datetime.now().strftime('\n' + "%m/%d/%Y, %H:%M:%S") + '\n')
            my_stderr.write(self.InteractiveTB.stb2text(stb) + '\n')
            my_stderr.flush()
            self._showtraceback_orig(etype, evalue, stb)

        ip._showtraceback = types.MethodType(_showtraceback, ip)

