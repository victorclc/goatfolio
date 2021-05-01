from datetime import datetime
from decimal import Decimal
from typing import List

import boto3
import requests
from dateutil.relativedelta import relativedelta

from auroradata.aurora import AuroraData


class B3CotaHistData:
    def __init__(self):
        self.codigo_negociacao = None
        self.data_pregao = None
        self.nome_resumido_empresa_emissora = None
        self.preco_abertura = None
        self.preco_ultimo = None
        self.preco_medio = None
        self.preco_maximo = None
        self.preco_minimo = None
        self.preco_melhor_oferta_compra = None
        self.preco_melhor_oferta_venda = None
        self.numero_de_negocios = None
        self.codigo_do_papel_no_sistema_isin_ou_codigo_interno_papel = None

        self.tipo_registro = None
        self.codigo_bdi = None
        self.tipo_mercado = None
        self.especificacao_papel = None
        self.prazo_dias_mercado_a_termo = None
        self.moeda_referencia = None
        self.quantidade_total_titulos_negociados = None
        self.volume_total_titulos_negociados = None
        self.preco_exercicio_mercado_opcoes_ou_valor_contrato_mercado_termo_secundario = None
        self.indicador_correcao_precos_exercicios_ou_valores_contrato_mercado_termo_secundario = None
        self.data_vencimento_mercado_opcoes_ou_termo = None
        self.fator_de_cotacao = None
        self.preco_exercicio_para_opcoes_referenciadas_em_dolar = None
        self.numero_distribuicao_papel = None

    def load_essentials(self, codigo_negociacao, data_pregao, nome_resumido_empresa_emissora, preco_abertura,
                        preco_ultimo,
                        preco_medio, preco_maximo, preco_minimo, preco_melhor_oferta_compra, preco_melhor_oferta_venda,
                        numero_de_negocios, codigo_do_papel_no_sistema_isin_ou_codigo_interno_papel):
        self.codigo_negociacao = codigo_negociacao
        self.data_pregao = data_pregao
        self.nome_resumido_empresa_emissora = nome_resumido_empresa_emissora
        self.preco_abertura = preco_abertura
        self.preco_ultimo = preco_ultimo
        self.preco_medio = preco_medio
        self.preco_maximo = preco_maximo
        self.preco_minimo = preco_minimo
        self.preco_melhor_oferta_compra = preco_melhor_oferta_compra
        self.preco_melhor_oferta_venda = preco_melhor_oferta_venda
        self.numero_de_negocios = numero_de_negocios
        self.codigo_do_papel_no_sistema_isin_ou_codigo_interno_papel = codigo_do_papel_no_sistema_isin_ou_codigo_interno_papel

    def load_line(self, line: str):
        self.tipo_registro = line[0:2]
        self.data_pregao = f'{line[2:6]}-{line[6:8]}-{line[8:10]}'
        self.codigo_bdi = line[10:12]
        self.codigo_negociacao = line[12:24].strip()
        self.tipo_mercado = line[24:27]
        self.nome_resumido_empresa_emissora = line[27:39].strip()
        self.especificacao_papel = line[39:49]
        self.prazo_dias_mercado_a_termo = line[49:52]
        self.moeda_referencia = line[52:56]
        self.preco_abertura = (Decimal(line[56:69]) / 100).quantize(Decimal('0.01'))
        self.preco_maximo = (Decimal(line[69:82]) / 100).quantize(Decimal('0.01'))
        self.preco_minimo = (Decimal(line[82:95]) / 100).quantize(Decimal('0.01'))

        self.preco_medio = (Decimal(line[95:108]) / 100).quantize(Decimal('0.01'))
        self.preco_ultimo = (Decimal(line[108:121]) / 100).quantize(Decimal('0.01'))
        self.preco_melhor_oferta_compra = (Decimal(line[121:134]) / 100).quantize(Decimal('0.01'))
        self.preco_melhor_oferta_venda = (Decimal(line[134:147]) / 100).quantize(Decimal('0.01'))
        self.numero_de_negocios = (Decimal(line[147:152]) / 100).quantize(Decimal('0.01'))
        self.quantidade_total_titulos_negociados = line[152:170]
        self.volume_total_titulos_negociados = line[170:188]
        self.preco_exercicio_mercado_opcoes_ou_valor_contrato_mercado_termo_secundario = line[188:201]
        self.indicador_correcao_precos_exercicios_ou_valores_contrato_mercado_termo_secundario = line[201:202]

        self.data_vencimento_mercado_opcoes_ou_termo = line[202:210]
        self.fator_de_cotacao = line[210:217]
        self.preco_exercicio_para_opcoes_referenciadas_em_dolar = line[217:230]
        self.codigo_do_papel_no_sistema_isin_ou_codigo_interno_papel = line[230:242]
        self.numero_distribuicao_papel = line[242:245]

    def to_dict(self):
        return {
            'ticker': self.codigo_negociacao, 'candle_date': self.data_pregao,
            'company_name': self.nome_resumido_empresa_emissora, 'open_price': self.preco_abertura,
            'close_price': self.preco_ultimo, 'average_price': self.preco_medio, 'max_price': self.preco_maximo,
            'min_price': self.preco_minimo, 'volume': self.numero_de_negocios,
            'isin_code': self.codigo_do_papel_no_sistema_isin_ou_codigo_interno_papel
        }


class CotaHistRepository:
    def __init__(self):
        self.__table = boto3.resource('dynamodb').Table('MarketData')

    def save(self, data: B3CotaHistData):
        self.__table.put_item(Item=data.to_dict())

    def batch_save(self, series: List[B3CotaHistData]):
        with self.__table.batch_writer() as batch:
            for data in series:
                batch.put_item(Item=data.to_dict())


if __name__ == '__main__':
    response = \
        requests.get('https://query1.finance.yahoo.com/v7/finance/chart/^BVSP?range=max&interval=1mo').json()['chart'][
            'result'][0]

    quote = response['indicators']['quote'][0]
    timestamp = response['timestamp'][:-1]
    entries = []

    secret = "arn:aws:secretsmanager:us-east-2:831967415635:secret:rds-db-credentials/cluster-B7EKYQNIWMBMYI6I6DNK6ICBEE/postgres-z9xJqf"
    cluster = "arn:aws:rds:us-east-2:831967415635:cluster:serverless-goatfolio-dev-marketdatardscluster-dq6ryzdhjru0"
    database = "marketdata"

    aurora_data = AuroraData(cluster, secret, database)
    sql = 'INSERT INTO b3_monthly_chart (ticker, candle_date, company_name, open_price, close_price, max_price, min_price, volume) values (:ticker, :candle_date, :company_name, :open_price, :close_price, :max_price, :min_price, :volume)'
    for i in range(len(timestamp)):
        date = datetime.fromtimestamp(timestamp[i])
        if date.day != 1:
            date = datetime(date.year, date.month, 1) + relativedelta(months=1)

        entry = [
            {'name': 'ticker', 'value': {'stringValue': 'IBOVESPA'}},
            {'name': 'candle_date', 'typeHint': 'DATE', 'value': {'stringValue': date.strftime('%Y-%m-%d')}},
            {'name': 'company_name', 'value': {'stringValue': 'Indice Ibovespa'}},
            {'name': 'open_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f"{quote['open'][i]}"}},
            {'name': 'close_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f"{quote['close'][i]}"}},
            {'name': 'max_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f"{quote['high'][i]}"}},
            {'name': 'min_price', 'typeHint': 'DECIMAL', 'value': {'stringValue': f"{quote['low'][i]}"}},
            {'name': 'volume', 'typeHint': 'DECIMAL', 'value': {'stringValue': f"{quote['volume'][i]}"}}
        ]
        data = B3CotaHistData()
        data.load_essentials('IBOVESPA', date.strftime('%Y%m%d'), 'Indice Ibovespa', Decimal(quote['open'][i]).quantize(Decimal('0.01')),
                             Decimal(quote['close'][i]).quantize(Decimal('0.01')),
                             None, Decimal(quote['high'][i]).quantize(Decimal('0.01')),
                             Decimal(quote['low'][i]).quantize(Decimal('0.01')), None, None,
                             Decimal(quote['volume'][i]).quantize(Decimal('0.01')), None)
        entries.append(data)

    CotaHistRepository().batch_save(entries)

