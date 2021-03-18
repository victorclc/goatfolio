from datetime import datetime
from decimal import Decimal

INPUT_FILE = 'COTAHIST_A2018.TXT'
OUTPUT_FILE = 'COTAHIST_A2018_ALL.sql'


class B3DaySeries:
    def __init__(self, line: str):
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

    def create_statement(self):
        return f'INSERT INTO b3_daily_chart ' \
               f'(ticker, candle_date, company_name, open_price, close_price, average_price, max_price, min_price, best_ask, best_bid, volume) values ' \
               f'(\'{self.codigo_negociacao}\', \'{self.data_pregao}\', \'{self.nome_resumido_empresa_emissora}\', {self.preco_abertura}, {self.preco_ultimo}, {self.preco_medio}, {self.preco_maximo}, {self.preco_minimo}, {self.preco_melhor_oferta_compra}, {self.preco_melhor_oferta_venda}, {self.numero_de_negocios});\n'


counter = 0
start = datetime.now().timestamp()
with open(INPUT_FILE, 'r') as fp:
    with open(OUTPUT_FILE, 'w+') as out:
        for line in fp:
            if line.startswith('99COTAHIST') or line.startswith('00COTAHIST'):
                continue
            y = B3DaySeries(line)
            if y.codigo_bdi not in ['02', '12', '14']:  # ,
                continue
            counter = counter + 1
            out.write(y.create_statement())

end = datetime.now().timestamp()
print(f'TEMPO GASTO: {end - start}')
print(f'QTD LINHAS: {counter}')
