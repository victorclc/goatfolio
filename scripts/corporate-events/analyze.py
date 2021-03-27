from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


def analyze():
    pass


if __name__ == '__main__':
    processing_start = datetime.now().timestamp()
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')
    # extract_and_persist_company_info_cvm(engine)
    cvm_codes = []
    with engine.connect() as con:
        response = con.execute("select cvm_code from cvm_company_info where registry_situation not like 'Cancelado%%'")
        for row in response:
            cvm_codes.append(row[0])

    for code in cvm_codes:
        counter = 0
        ticker = None
        while Path(f'b3data/{code}-{counter}.csv').exists():
            table = pd.read_csv(f'b3data/{code}-{counter}.csv')
            if set(table.columns) == {'Unnamed: 0', '0', '1'}:  # first table, with company data
                for index, row in table.iterrows():
                    if row['0'] == 'Código:':
                        ticker = row['1']
            elif set(table.columns) == {'Unnamed: 0', 'Proventos', 'Código ISIN', 'Deliberado em',
                                        'Negócios com até', '% / Fator de Grupamento', 'Ativo Emitido',
                                        'Observações'}:
                table.drop('Unnamed: 0', inplace=True, axis=1)
                table['ticker'] = [ticker] * len(table)
                table.columns = ['proventos', 'codigo_isin', 'deliberado_em', 'negocios_com_ate',
                                 'fator_de_grupamento_perc', 'ativo_emitido', 'observacoes', 'ticker']
                print(f'{ticker} add to corporate events')
                table.to_sql('b3_corporate_events', con=engine, if_exists='append')
            counter = counter + 1
