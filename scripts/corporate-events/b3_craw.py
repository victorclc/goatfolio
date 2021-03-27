import traceback
from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


def extract_and_persist_corporate_events(db_engine, cvm_code):
    url = f'http://bvmf.bmfbovespa.com.br/cias-listadas/empresas-listadas/ResumoEventosCorporativos.aspx?codigoCvm={cvm_code}&tab=3&idioma=pt-br'
    tables = pd.read_html(url)
    print(f'TABLES FOUND: {len(tables)}')
    counter = 0
    for table in tables:
        print(f'Saving csv: b3data/{cvm_code}-{counter}')
        table.to_csv(f'b3data/{cvm_code}-{counter}.csv')
        counter = counter + 1


if __name__ == '__main__':
    processing_start = datetime.now().timestamp()
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')
    # extract_and_persist_company_info_cvm(engine)
    cvm_codes = []
    with engine.connect() as con:
        response = con.execute("select cvm_code from cvm_company_info where registry_situation not like 'Cancelado%%'")
        for row in response:
            cvm_codes.append(row[0])
    errors = []
    count = 0
    length = len(cvm_codes)
    for code in cvm_codes:
        print(f'Processing: {code} ({count} of {length})')
        if Path(f'b3data/{code}-0.csv').exists():
            print('already processed')
            count = count + 1
            continue
        try:
            extract_and_persist_corporate_events(engine, code)
        except Exception:
            traceback.print_exc()
            print('Exception Caught')
            errors.append(code)
        count = count + 1
    processing_end = datetime.now().timestamp()
    # erros = ['23396', '516147', '25658', '511404', '23442', '24120', '24210', '21989', '22004', '21997', '21970',
    #          '21962', '21466', '15822', '24970', '24775', '508438', '25500', '24627', '24287', '23930', '24830',
    #          '23132', '23850', '23841', '15717', '23795', '23353', '14168', '24643', '23620', '16675', '24597', '25577',
    #          '16373', '3328', '19429', '16748', '3115', '18627', '25216', '18287', '23531', '24724', '25178', '23809',
    #          '24422', '24430', '24155', '3395', '3450', '21709', '14311', '22080', '500160', '24147', '24511', '24520',
    #          '25593', '25020', '25267', '25127', '23868', '22144', '23892', '24104', '25356', '23833', '21849', '24139',
    #          '22071', '23922', '4685', '25054', '24899', '24740', '501492', '19470', '25100', '500836', '23493',
    #          '23884', '23582', '22810', '17485', '25569', '14176', '25348', '23701', '21938', '24864', '24589', '24341',
    #          '24457', '24481', '25380', '25429', '24333', '15024', '22977', '21814', '506842', '6017', '24732', '23019',
    #          '22489', '23566', '509850', '23370', '24040', '20222', '19569', '16632', '516996', '25321', '25011',
    #          '25186', '24694', '4669', '24562', '21628', '13366', '24392', '14850', '25402', '20877', '6629', '25364',
    #          '6700', '511641', '25313', '21431', '23175', '22560', '7510', '7595', '21750', '25453', '24279', '18775',
    #          '18589', '6041', '11932', '510971', '20818', '19364', '19348', '21156', '24473', '25631', '4146', '22446',
    #          '505943', '23558', '23000', '24937', '23680', '23671', '24880', '24813', '23477', '25542', '23612',
    #          '516775', '8397', '16268', '12980', '22861', '25232', '8605', '8745', '8818', '25151', '21520', '23906',
    #          '24783', '24015', '14613', '17540', '24988', '25097', '502596', '24708', '23426', '25143', '18554',
    #          '25305', '9520', '24791', '23523', '9717', '23469', '23760', '9989', '22802', '21636', '21440', '25623',
    #          '18368', '24368', '24996', '19151', '24686', '24538', '17850', '24490', '19186', '15199', '25410', '10561',
    #          '23698', '14966', '24252', '14303', '16241', '501646', '23957', '519707', '505862', '505838', '7544',
    #          '22225', '20443', '25240', '24082', '25194', '11398', '22420', '6343', '18465', '11592', '24856', '25437',
    #          '24945', '519146', '24767', '24309', '23990', '6505', '22926', '25607', '22543', '518034', '21075',
    #          '21202', '15741', '16551', '23604', '512214']
    print(len(errors))
    print(f'Exception codes: {errors}')
    print(f'Execution time: {processing_end - processing_start} seconds')
