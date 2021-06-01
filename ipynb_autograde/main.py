import autograde


def init_log():
    autograde.init_log()


def validate(func, inputs, outfunc, outputs, exercise_number):
    return autograde.validate(func, inputs, outfunc, outputs, exercise_number)


def validate2(func, inputs, outfunc, outputs, exercise_number):
    return autograde.validate2(func, inputs, outfunc, outputs, exercise_number)

