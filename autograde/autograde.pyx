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

def get_data(answers_status, exercise_number):
    import os
    log_url, log_data_fields = os.getenv("log_url").replace("|||", "=").split("&__data__")
    results_url = os.getenv("results_url").replace("|||", "=")
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
        return True
    else:
        return False


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
    # Clear errors
    open('.errors', 'w').close()
    tmp_log = f"{current_log}"
    current_log = current_log.replace(session_log, "")
    session_log = tmp_log
    return current_log, current_errors


def validate(func, inputs, outfunc, outputs, exercise_number):
    answers_status = True
    validate_output = "Parabéns!"
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
        df = gether_data("")
        df2 = explode_and_merge(df, "id")
        df3 = change_pct(df2)
        out = get_data(answers_status, exercise_number)
        return out, validate_output


def validate2(func, inputs, outfunc, outputs, exercise_number):
    answers_status = True
    outputs = [True for x in inputs] if outputs == None else outputs
    validate_output = "Parabéns!"

    for k, v in zip(inputs, outputs):
        ans = func(*k)
        result = None
        try:
            result = outfunc(ans, k) == v
            if not result:
                answers_status = False
                print(f"Resposta incorreta. {func.__name__}({k}) deveria ser {v}, mas retornou {ans}")
        except ValueError:
            pass
            if not result.all():
                answers_status = False
                print(f"Resposta incorreta. {func.__name__}({k}) deveria ser {v}, mas retornou {ans}")
    df = gether_data("")
    df2 = explode_and_merge(df, "id")
    df3 = change_pct(df2)
    out = get_data(answers_status, exercise_number)
    return out, validate_output

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
