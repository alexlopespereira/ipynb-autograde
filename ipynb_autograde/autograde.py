import sys
from datetime import datetime
import requests
import time
from requests.utils import quote
import types
import numpy as np
import pandas as pd
import os


def format_values(values, data_type="EXERCISE"):
    result = {}
    if data_type == "EXERCISE":
        return {
        "entry.1269959472": values['student_id'],
        "entry.1799867692": str(values['exercise_number']).replace(".", "_"),
        "entry.886231469": values['exercise_score'],
        "entry.1342537331": values['id']
        }
    elif data_type == "LOG":
        return {
        "entry.39852643": values['student_id'],
        "entry.1437170782": str(values['exercise_number']).replace(".", "_"),
        "entry.304785533": values['log'],
        "entry.2060734065": values['errors']
        }
    elif data_type == "ERROR":
        return None
    else:
        return None
    

def send_form(url, data):
    count = 0
    while count < 3:
        count += 1
        try:
          r = requests.post(url, data=data)
          break
        except:
          print("Error Occured!")
          time.sleep(2)

            
def validate(func, inputs, outfunc, outputs, exercise_number):
  import os
  log_url = os.getenv("log_url").replace("|", "=")
  results_url = os.getenv("results_url").replace("|", "=")
  global session_log
  ip = get_ipython()
  student_email = ip.getoutput("gcloud config get-value account")[0]

  current_log = ""
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
  logvalues = {"exercise_number": exercise_number, "student_id": student_email,
                "log": f"{current_log}", "errors": f"{current_errors}"}
  log_data = format_values(logvalues, "LOG")

  send_form(f"{log_url}&emailAddress={quote(str(student_email))}", log_data)
        
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
      values = {"exercise_number": exercise_number, "student_id": student_email,
                "exercise_points": 1, "exercise_score": exercise_score, 
                "id": f"{student_email}_{exercise_number}"}
      final_data = format_values(values, "EXERCISE")
      send_form(f"{results_url}&emailAddress={quote(str(student_email))}", final_data)
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
