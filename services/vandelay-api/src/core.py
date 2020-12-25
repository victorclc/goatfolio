from datetime import datetime
import re

from adapters import ImportsRepository, CEIImportsQueue
from brutils.validations import NationalTaxIdUtils
from constants import ImportStatus
from exceptions import UnprocessableException
from models import CEIInboundRequest, Import, CEIOutboundRequest


def _is_status_final(status):
    return ImportStatus.ERROR == status or ImportStatus.SUCCESS == status


class CEICore:
    def __init__(self, repo=ImportsRepository(), queue=CEIImportsQueue()):
        self.repo = repo
        self.queue = queue

    def cei_import_request(self, subject, request):
        self._validate_request(subject, request)

        now = int(datetime.now().timestamp())
        _import = Import(subject=subject, datetime=now, username=request.tax_id, status=ImportStatus.PROCESSING)
        outbound_request = CEIOutboundRequest(credentials=request, datetime=now, subject=subject)

        self.queue.send(outbound_request)
        self.repo.save(_import)

    def _validate_request(self, subject, request):
        if self._has_open_requests(subject):
            raise UnprocessableException("Already has a pending import request")
        if self._is_request_valid(request):
            raise UnprocessableException("Invalid Username or Password")

    def _has_open_requests(self, subject):
        latest = self.repo.find_latest(subject)
        return latest and _is_status_final(latest.status)

    def _is_request_valid(self, request: CEIInboundRequest):
        pattern = re.compile(
            r'^(?=.*[A-Za-z])(?=.*[!@#$&*])(?=.*[0-9]).{8,16}$')  # a least 1 letter, 1 number, 1 symbol and 8<=len<=16
        return NationalTaxIdUtils.is_valid(request.tax_id) and pattern.match(request.password)
