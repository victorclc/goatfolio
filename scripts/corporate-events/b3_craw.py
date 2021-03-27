import pandas as pd


def extract_and_persist_corporate_events(db_engine, cvm_code):
    url = f'http://bvmf.bmfbovespa.com.br/cias-listadas/empresas-listadas/ResumoEventosCorporativos.aspx?codigoCvm={cvm_code}&tab=3&idioma=pt-br'
    tables = pd.read_html(url)
    print(f'TABLES FOUND: {len(tables)}')
    counter = 0
    for table in tables:
        print(f'Saving csv: b3data/{cvm_code}-{counter}')
        table.to_csv(f'b3data/{cvm_code}-{counter}.csv')
        counter = counter + 1
