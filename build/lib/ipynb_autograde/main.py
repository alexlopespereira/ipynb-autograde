from autograde import autograde


def init_log():
    autograde.init_log()


def validate(prompt, exercise_number):
    return autograde.validate(prompt, exercise_number)



# def validate2(func, inputs, outfunc, outputs, exercise_number):
#     return autograde.validate2(func, inputs, outfunc, outputs, exercise_number)

