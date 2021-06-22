# Faca aqui a validacao do Exercicio 1.1
import numpy as np
import pandas as pd

from autograde.autograde import validate

# Faca aqui sua função do Exercício 1.1

def get_headers(dataframe):
    """
    Pega o nome das colunas de um dataframe
    :param dataframe:
    :return:
    """
    return dataframe.columns.values

def cal_variance(readings):
    """
    Calcula a variancia de uma lista ou series de entrada
    :param readings:
    :return:
    """

    # To calculate the variance we need the mean value
    # Calculating the mean value from the cal_mean function
    readings_mean = cal_mean(readings)
    # mean difference squared readings
    mean_difference_squared_readings = [pow((reading - readings_mean), 2) for reading in readings]
    variance = sum(mean_difference_squared_readings)
    return variance / float(len(readings) - 1)

# Faca aqui sua função do Exercício 1.2
def cal_mean(readings):
    """
    Calcula o a media de uma lista ou series de entrada
    :param readings:
    :return:
    """
    readings_total = sum(readings)
    number_of_readings = len(readings)
    mean = readings_total / float(number_of_readings)
    return mean

# input_path = 'https://github.com/4tune-ai/IDP/blob/main/data/input_data.csv?raw=true'
# house_price_dataset = pd.read_csv(input_path)
# entradas = [[house_price_dataset]]
# saidas = [np.array(['square_feet', 'price']),[]]
# validate(get_headers, entradas, lambda x: x, saidas, "1.1")
# Faca aqui sua função do Exercício 1.5
def simple_linear_regression(dataset):
    """
    Implementa uma regressão linear simples
    :param dataset:
    :return:
    """

    # Get the dataset header names
    dataset_headers = get_headers(dataset)

    # Calculating the mean of the square feet and the price readings
    square_feet_mean = cal_mean(dataset[dataset_headers[0]])
    price_mean = cal_mean(dataset[dataset_headers[1]])

    square_feet_variance = cal_variance(dataset[dataset_headers[0]])
    price_variance = cal_variance(dataset[dataset_headers[1]])

    # Calculating the regression
    covariance_of_price_and_square_feet = dataset.cov()[dataset_headers[0]][dataset_headers[1]]
    w1 = covariance_of_price_and_square_feet / float(square_feet_variance)

    w0 = price_mean - (w1 * square_feet_mean)

    # Predictions
    predicted_price = w0 + w1 * dataset[dataset_headers[0]]
    return predicted_price
# Faca aqui a validacao do Exercicio 1.5
input_path = 'https://github.com/4tune-ai/IDP/blob/main/data/input_data.csv?raw=true'
house_price_dataset = pd.read_csv(input_path)

d = {0: 6088.3, 1: 7527.1, 2: 8966.0, 3: 10404.8, 4: 11843.6, 5: 13282.4, 6: 19037.8}
ser = pd.Series(data=d, name="square_feet")
entradas = [[house_price_dataset]]
saidas = [ser]
validate(simple_linear_regression, entradas, lambda x: round(x, 1), saidas, "1.5")
