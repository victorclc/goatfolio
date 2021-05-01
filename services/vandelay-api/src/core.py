import logging
import re
from datetime import datetime

from adapters import ImportsRepository, CEIImportsQueue, PortfolioClient
from brutils.validations import NationalTaxIdUtils
from constants import ImportStatus
from exceptions import UnprocessableException, BatchSavingException
from goatcommons.models import StockInvestment
from goatcommons.notifications.client import PushNotificationsClient
from models import CEIInboundRequest, Import, CEIOutboundRequest, CEIImportResult

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _is_status_final(status):
    return ImportStatus.ERROR == status or ImportStatus.SUCCESS == status


class CEICore:
    def __init__(self, repo=ImportsRepository(), queue=CEIImportsQueue(), portfolio=PortfolioClient()):
        self.repo = repo
        self.queue = queue
        self.portfolio = portfolio
        self.push = PushNotificationsClient()

    def import_request(self, subject, request):
        logger.info(f'Processing import request from {subject}')
        self._validate_request(subject, request)

        now = int(datetime.now().timestamp())
        _import = Import(subject=subject, datetime=now, username=request.tax_id, status=ImportStatus.PROCESSING)
        outbound_request = CEIOutboundRequest(credentials=request, datetime=now, subject=subject)

        self.queue.send(outbound_request)
        self.repo.save(_import)

    def import_result(self, result: CEIImportResult):
        _import = self.repo.find(result.subject, result.datetime)
        _import.status = result.status
        _import.payload = result.payload

        if result.status == ImportStatus.ERROR:
            _import.error_message = result.payload
        else:
            try:
                investments = list(map(lambda i: StockInvestment(**i), result.payload))
                self.portfolio.batch_save(investments)
                self.push.send_message(result.subject, 'CEI_IMPORT_SUCCESS')
            except BatchSavingException:
                _import.status = ImportStatus.ERROR
                _import.error_message = 'Error on batch saving.'
            except TypeError as e:
                logger.error(f'Error on parsing payload: {str(e)}')
                _import.status = ImportStatus.ERROR
                _import.error_message = str(e)
        self.repo.save(_import)
        return _import

    def _validate_request(self, subject, request):
        if not self._is_request_valid(request):
            raise UnprocessableException("Invalid Username or Password")
        if self._has_open_requests(subject):
            raise UnprocessableException("Already has a pending import request")

    def _has_open_requests(self, subject):
        latest = self.repo.find_latest(subject)
        return latest and not _is_status_final(latest.status)

    def _is_request_valid(self, request: CEIInboundRequest):
        pattern = re.compile(
            r'^(?=.*[A-Za-z])(?=.*[!@#$&*])(?=.*[0-9]).{8,16}$')  # a least 1 letter, 1 number, 1
        # symbol and 8<=len<=16
        return NationalTaxIdUtils.is_valid(request.tax_id) and pattern.match(request.password)
