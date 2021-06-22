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

input_path = 'https://github.com/4tune-ai/IDP/blob/main/data/input_data.csv?raw=true'
house_price_dataset = pd.read_csv(input_path)
entradas = [[house_price_dataset]]
saidas = [np.array(['square_feet', 'price']),[]]
validate(get_headers, entradas, lambda x: x, saidas, "1.1")

