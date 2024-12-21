
PYTHON_ENAP_LOG_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfRtpAVNRGKDmTxh9FhJKucyNMGeQ8Es_JRyG_HcUUVmM_zQg/formResponse?usp|||pp_url&entry.1956860070|||mbacd&entry.205464053|||2021&entry.1885440499|||CienciaDeDados&entry.1437170782|||__exercisenumber__&__data__entry.304785533|||__log__&entry.2060734065|||__errors__"
PYTHON_ENAP_RESULTS_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeASSC8-w8FmfodZ4lBnuSEAvYuE4vatIBowLIREG1f-2pIpA/formResponse?usp|||pp_url&entry.1986154915|||mbacd&entry.513694412|||2021&entry.1914621244|||CienciaDeDados&entry.1799867692|||__exercisenumber__&entry.886231469|||__exercisescore__&entry.1342537331|||__id__"

PYTHON_SGD_LOG_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeS3yygfVdlO-78HCyQq5tRAky6LxqgpAiMQK1mVG_Gd7uaZw/formResponse?usp|||pp_url&entry.1956860070|||cienciadados&entry.205464053|||tribosgd&entry.1885440499|||python&entry.1437170782|||__exercisenumber__&__data__entry.304785533|||__log__&entry.2060734065|||__errors__"
PYTHON_SGD_RESULTS_URL = "https://docs.google.com/forms/d/e/1FAIpQLScb47A8PDUj0GhD3H5gkvGcN22vxzknpzbio3jhcim-jMfZdg/formResponse?usp|||pp_url&entry.1986154915|||cienciadados&entry.513694412|||tribosgd&entry.1914621244|||python&entry.1799867692|||__exercisenumber__&entry.886231469|||__exercisescore__&entry.1342537331|||__id__"

datasets = {
    "python_tribosgd":
        {"RESULTS_URL": PYTHON_SGD_RESULTS_URL,
         "LOG_URL": PYTHON_SGD_LOG_URL,
         "errors_spreadsheet_id": "1OVxeKMyzPdPO80A-xBm8sGW3-bDz5k-vERvoet-IXQ0"
         },
    "python_enap":
        {"RESULTS_URL": PYTHON_ENAP_RESULTS_URL,
         "LOG_URL": PYTHON_ENAP_LOG_URL,
         "errors_spreadsheet_id": "1h0WZrH3rQOwP6XOvnfqpH_qSF6nrYTXWFNjVln-e-l8"
        }
}

SOLVE_URL = "https://seal-app-pmncf.ondigitalocean.app/"
