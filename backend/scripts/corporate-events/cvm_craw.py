import pandas as pd


def extract_and_persist_company_info_cvm(db_engine):
    url = 'https://cvmweb.cvm.gov.br/SWB/Sistemas/SCW/CPublica/CiaAb/FormBuscaCiaAbOrdAlf.aspx?LetraInicial={}'
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWYXZ'
    for letter in alphabet:
        print(f'Processing letter {letter}')
        tables = pd.read_html(url.format(letter))
        assert len(tables) == 2
        tables[1].columns = ['cnpj', 'name', 'participant_type', 'cvm_code', 'registry_situation']
        tables[1] = tables[1].iloc[1:]
        tables[1].to_sql('cvm_company_info', con=db_engine, if_exists='append')
