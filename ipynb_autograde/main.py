import autograde


def init_log():
    autograde.init_log()

def validate(func, inputs, outfunc, outputs, exercise_number):
    return autograde.validate(func, inputs, outfunc, outputs, exercise_number)


