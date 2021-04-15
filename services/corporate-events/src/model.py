from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from goatcommons.constants import InvestmentsType


@dataclass
class CompanyCorporateEventsData:
    company_name: str
    trading_name: str
    code: str
    segment: str
    code_cvm: str
    url: str


@dataclass
class CorporateEvent:
    proventos: str
    codigo_isin: str
    deliberado_em: datetime
    negocios_com_ate: datetime
    fator_de_grupamento_perc: Decimal
    ativo_emitido: str
    observacoes: str

    def __post_init__(self):
        if type(self.negocios_com_ate) is not datetime:
            self.negocios_com_ate = datetime.strptime(self.negocios_com_ate, '%d/%m/%Y')
        if type(self.deliberado_em) is not datetime:
            self.deliberado_em = datetime.strptime(self.deliberado_em, '%d/%m/%Y')


@dataclass
class AsyncInvestmentAddRequest:
    subject: str
    type: InvestmentsType
    investment: dict
