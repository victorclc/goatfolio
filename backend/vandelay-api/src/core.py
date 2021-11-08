import logging
import re
from datetime import datetime

from brutils.validations import NationalTaxIdUtils
from constants import ImportStatus
from exceptions import UnprocessableException, BatchSavingException
from models import (
    CEIInboundRequest,
    Import,
    CEIOutboundRequest,
    CEIImportResult,
    CEIInfo,
    StockInvestment,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _is_status_final(status):
    return ImportStatus.ERROR == status or ImportStatus.SUCCESS == status


class CEICore:
    def __init__(self, repo, queue, portfolio, push, cei_repo):
        self.repo = repo
        self.queue = queue
        self.portfolio = portfolio
        self.push = push
        self.info_queue = cei_repo

    def import_request(self, subject, request):
        logger.info(f"Processing import request from {subject}")
        self._validate_request(subject, request)

        now = int(datetime.now().timestamp())
        _import = Import(
            subject=subject,
            datetime=now,
            username=request.tax_id,
            status=ImportStatus.PROCESSING,
        )
        outbound_request = CEIOutboundRequest(
            credentials=request, datetime=now, subject=subject
        )

        self.queue.send(outbound_request)
        self.repo.save(_import)

        return {"datetime": _import.datetime, "status": _import.status}

    def import_result(self, result: CEIImportResult):
        _import = self.repo.find(result.subject, result.datetime)
        _import.status = result.status
        _import.payload = result.payload

        if result.status == ImportStatus.ERROR:
            _import.error_message = result.payload
            if result.login_error:
                self.push.send_message(result.subject, "CEI_IMPORT_LOGIN_ERROR")
            else:
                self.push.send_message(result.subject, "CEI_IMPORT_ERROR")
        else:
            try:
                investments = list(
                    map(lambda i: StockInvestment(**i), result.payload["investments"])
                )
                self.portfolio.batch_save(investments)
                if "assets_quantities" in result.payload:
                    self.info_queue.send(
                        CEIInfo(
                            subject=result.subject,
                            asset_quantities={
                                k: v
                                for k, v in result.payload["assets_quantities"].items()
                                if self.is_valid_ticker_name(k)
                            },
                        )
                    )
                self.push.send_message(result.subject, "CEI_IMPORT_SUCCESS")
            except BatchSavingException:
                _import.status = ImportStatus.ERROR
                _import.error_message = "Error on batch saving."
            except TypeError as e:
                logger.exception(f"Error on parsing payload", e)
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

    def is_valid_ticker_name(self, ticker: str):
        pattern = re.compile(r"^([A-Z]{4}[0-9]{1,2})")

        return pattern.match(ticker)

    def _is_request_valid(self, request: CEIInboundRequest):
        pattern = re.compile(
            r"^(?=.*[A-Za-z])(?=.*[!@#%$&*])(?=.*[0-9]).{8,16}$"
        )  # a least 1 letter, 1 number, 1
        # symbol and 8<=len<=16
        return NationalTaxIdUtils.is_valid(request.tax_id) and pattern.match(
            request.password
        )

    def cei_info_request(self, subject):
        assert subject
        info = self.info_queue.find(subject=subject)
        if info:
            return info.assets_quantities

    def import_status(self, subject, date):
        return self.repo.find(subject, date)
