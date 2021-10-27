import logging
from dataclasses import asdict
from http import HTTPStatus

import goatcommons.utils.aws as awsutils
import goatcommons.utils.json as jsonutils
from adapters import (
    ImportsRepository,
    CEIImportsQueue,
    PortfolioClient,
    CEIInfoRepository,
)
from core import CEICore
from event_notifier.decorators import notify_exception
from event_notifier.models import NotifyLevel
from exceptions import UnprocessableException
from goatcommons.notifications.client import PushNotificationsClient
from models import CEIInboundRequest, CEIImportResult

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

core = CEICore(
    repo=ImportsRepository(),
    queue=CEIImportsQueue(),
    portfolio=PortfolioClient(),
    push=PushNotificationsClient(),
    cei_repo=CEIInfoRepository(),
)


def cei_import_request_handler(event, context):
    try:
        request = CEIInboundRequest(**jsonutils.load(event["body"]))
        subject = awsutils.get_event_subject(event)

        response = core.import_request(subject, request)
        return {
            "statusCode": HTTPStatus.ACCEPTED.value,
            "body": jsonutils.dump(response),
        }
    except TypeError as e:
        logger.exception(e)
        return {
            "statusCode": HTTPStatus.BAD_REQUEST.value,
            "body": jsonutils.dump({"message": str(e)}),
        }
    except UnprocessableException as e:
        logger.exception(e)
        return {
            "statusCode": HTTPStatus.UNPROCESSABLE_ENTITY.value,
            "body": jsonutils.dump({"message": str(e)}),
        }


@notify_exception(Exception, NotifyLevel.ERROR)
def cei_import_result_handler(event, context):
    logger.info(f"EVENT: {event}")

    for message in event["Records"]:
        core.import_result(CEIImportResult(**jsonutils.load(message["body"])))
    return {
        "statusCode": HTTPStatus.OK.value,
        "body": jsonutils.dump({"message": HTTPStatus.OK.phrase}),
    }


def cei_info_request_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        subject = awsutils.get_event_subject(event)
        response = core.cei_info_request(subject)
        return {
            "statusCode": HTTPStatus.OK.value,
            "body": jsonutils.dump(response) if response else [],
        }
    except TypeError as e:
        logger.exception(e)
        return {
            "statusCode": HTTPStatus.BAD_REQUEST.value,
            "body": jsonutils.dump({"message": str(e)}),
        }
    except UnprocessableException as e:
        logger.exception(e)
        return {
            "statusCode": HTTPStatus.UNPROCESSABLE_ENTITY.value,
            "body": jsonutils.dump({"message": str(e)}),
        }


def import_status_handler(event, context):
    logger.info(f"EVENT: {event}")
    try:
        subject = awsutils.get_event_subject(event)
        date = awsutils.get_query_param(event, "datetime")
        response = core.import_status(subject, date)
        if not response:
            return {
                "statusCode": HTTPStatus.NOT_FOUND.value,
                "body": jsonutils.dump({"message": HTTPStatus.OK.phrase}),
            }
        return {
            "statusCode": HTTPStatus.OK.value,
            "body": jsonutils.dump(asdict(response)),
        }
    except TypeError as e:
        logger.exception(e)
        return {
            "statusCode": HTTPStatus.BAD_REQUEST.value,
            "body": jsonutils.dump({"message": str(e)}),
        }
    except UnprocessableException as e:
        logger.exception(e)
        return {
            "statusCode": HTTPStatus.UNPROCESSABLE_ENTITY.value,
            "body": jsonutils.dump({"message": str(e)}),
        }


event = {'Records': [{'messageId': '75954d6d-535a-4581-bc6c-8cc07f4d722b', 'receiptHandle': 'AQEBzXDiarlPS4BAEFedvrFZW3D/r5PMm4yxiKnxIeFzdt1DIxMTjtrjKG1Toz4p3ii118S7UysOKXzCjAFP4YP1Gv6q269foVWDTsKK6q0plnqAvpIqQOG2Ar13k2m3umr5TwdkRGj6kNGSP+8aN+E5yqTRcOu4OtmJMNw/Kty3778b0OA+CQrBICMB04PxJI+vfAJKLOwG3TiC1JODBevDPr81MOKa2HHZgQQtIUGKhULOoAqFlvhfV1029F+WHDkf9oThFKeHbCA1PKgvtwgDgHRaevjeGi0PmCBHv2N9qkEADIyFA39eSMEvsc1lT+lyuedmSafHXYoTeOVQpeyFFuJZ3IlUd7etc4X7HgOCndBXxnyxXqnd0kK20ImyKSbbay6ryVgkjdYZvzrz2PJffw==', 'body': '{"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "datetime": 1635372502, "status": "SUCCESS", "payload": {"investments": [{"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201109, "type": "STOCK", "operation": "SELL", "broker": "308 - CLEAR CORRETORA - GRUPO XP", "ticker": "MDIA3", "amount": 100.0, "price": 35.14, "costs": 0.0, "id": "CEIMDIA3160488000010035141", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201109, "type": "STOCK", "operation": "SELL", "broker": "308 - CLEAR CORRETORA - GRUPO XP", "ticker": "WEGE3", "amount": 100.0, "price": 83.71, "costs": 0.0, "id": "CEIWEGE3160488000010083711", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201109, "type": "STOCK", "operation": "BUY", "broker": "308 - CLEAR CORRETORA - GRUPO XP", "ticker": "ITSA4", "amount": 1.0, "price": 10.38, "costs": 0.0, "id": "CEIITSA41604880000110381", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201109, "type": "STOCK", "operation": "BUY", "broker": "308 - CLEAR CORRETORA - GRUPO XP", "ticker": "ITSA4", "amount": 62.0, "price": 10.38, "costs": 0.0, "id": "CEIITSA416048800006210381", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201109, "type": "STOCK", "operation": "BUY", "broker": "308 - CLEAR CORRETORA - GRUPO XP", "ticker": "ITSA4", "amount": 21.0, "price": 10.38, "costs": 0.0, "id": "CEIITSA416048800002110381", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201109, "type": "STOCK", "operation": "SELL", "broker": "308 - CLEAR CORRETORA - GRUPO XP", "ticker": "ARZZ3", "amount": 10.0, "price": 64.18, "costs": 0.0, "id": "CEIARZZ316048800001064181", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201109, "type": "STOCK", "operation": "SELL", "broker": "308 - CLEAR CORRETORA - GRUPO XP", "ticker": "BIDI11", "amount": 40.0, "price": 60.06, "costs": 0.0, "id": "CEIBIDI1116048800004060061", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201109, "type": "STOCK", "operation": "SELL", "broker": "308 - CLEAR CORRETORA - GRUPO XP", "ticker": "FLRY3", "amount": 13.0, "price": 28.88, "costs": 0.0, "id": "CEIFLRY316048800001328881", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201109, "type": "STOCK", "operation": "SELL", "broker": "308 - CLEAR CORRETORA - GRUPO XP", "ticker": "MDIA3", "amount": 56.0, "price": 35.11, "costs": 0.0, "id": "CEIMDIA316048800005635111", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201109, "type": "STOCK", "operation": "SELL", "broker": "308 - CLEAR CORRETORA - GRUPO XP", "ticker": "SQIA3", "amount": 5.0, "price": 22.5, "costs": 0.0, "id": "CEISQIA31604880000522501", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201109, "type": "STOCK", "operation": "SELL", "broker": "308 - CLEAR CORRETORA - GRUPO XP", "ticker": "SQIA3", "amount": 4.0, "price": 22.5, "costs": 0.0, "id": "CEISQIA31604880000422501", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201109, "type": "STOCK", "operation": "SELL", "broker": "308 - CLEAR CORRETORA - GRUPO XP", "ticker": "SQIA3", "amount": 6.0, "price": 22.5, "costs": 0.0, "id": "CEISQIA31604880000622501", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20200520, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "ALZR11", "amount": 16.0, "price": 107.9, "costs": 0.0, "id": "CEIALZR11158993280016107901", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20200520, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "ALZR11", "amount": 4.0, "price": 107.9, "costs": 0.0, "id": "CEIALZR1115899328004107901", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20200520, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "BCFF11", "amount": 12.0, "price": 84.4, "costs": 0.0, "id": "CEIBCFF1115899328001284401", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20200520, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "IVVB11", "amount": 10.0, "price": 181.92, "costs": 0.0, "id": "CEIIVVB11158993280010181921", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20200709, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "IVVB11", "amount": 10.0, "price": 179.46, "costs": 0.0, "id": "CEIIVVB11159425280010179461", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20200709, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "RBRP11", "amount": 23.0, "price": 90.2, "costs": 0.0, "id": "CEIRBRP1115942528002390201", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20200721, "type": "STOCK", "operation": "SELL", "broker": "1099 - INTER DTVM LTDA", "ticker": "AZUL4", "amount": 100.0, "price": 21.92, "costs": 0.0, "id": "CEIAZUL4159528960010021921", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20200721, "type": "STOCK", "operation": "SELL", "broker": "1099 - INTER DTVM LTDA", "ticker": "VVAR3", "amount": 100.0, "price": 20.8, "costs": 0.0, "id": "CEIVVAR3159528960010020801", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20200721, "type": "STOCK", "operation": "SELL", "broker": "1099 - INTER DTVM LTDA", "ticker": "VVAR3", "amount": 100.0, "price": 20.76, "costs": 0.0, "id": "CEIVVAR3159528960010020761", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20200811, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "RBRP11", "amount": 19.0, "price": 88.1, "costs": 0.0, "id": "CEIRBRP1115971040001988101", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20200811, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "RBRP11", "amount": 22.0, "price": 88.1, "costs": 0.0, "id": "CEIRBRP1115971040002288101", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20200910, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "RBRP11", "amount": 16.0, "price": 91.07, "costs": 0.0, "id": "CEIRBRP1115996960001691071", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20200921, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "ITSA4", "amount": 100.0, "price": 8.97, "costs": 0.0, "id": "CEIITSA416006464001008971", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20200921, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "BIDI11", "amount": 25.0, "price": 51.5, "costs": 0.0, "id": "CEIBIDI1116006464002551501", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201009, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "BCFF11", "amount": 5.0, "price": 90.57, "costs": 0.0, "id": "CEIBCFF111602201600590571", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201009, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "BCFF11", "amount": 4.0, "price": 90.57, "costs": 0.0, "id": "CEIBCFF111602201600490571", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201009, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "BCFF11", "amount": 4.0, "price": 90.57, "costs": 0.0, "id": "CEIBCFF111602201600490572", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201009, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "BCFF11", "amount": 5.0, "price": 90.57, "costs": 0.0, "id": "CEIBCFF111602201600590572", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201009, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "BCFF11", "amount": 2.0, "price": 90.57, "costs": 0.0, "id": "CEIBCFF111602201600290571", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201009, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "BCFF11", "amount": 3.0, "price": 90.57, "costs": 0.0, "id": "CEIBCFF111602201600390571", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201009, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "MGLU3", "amount": 10.0, "price": 95.7, "costs": 0.0, "id": "CEIMGLU316022016001095701", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201009, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "MGLU3", "amount": 32.0, "price": 95.7, "costs": 0.0, "id": "CEIMGLU316022016003295701", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201112, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "RBRP11", "amount": 36.0, "price": 92.2, "costs": 0.0, "id": "CEIRBRP1116051392003692201", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20201112, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "RBRP11", "amount": 10.0, "price": 92.2, "costs": 0.0, "id": "CEIRBRP1116051392001092201", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20210209, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "VGIP11", "amount": 71.0, "price": 114.4, "costs": 0.0, "id": "CEIVGIP11161282880071114401", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20210222, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "BBAS3", "amount": 200.0, "price": 29.01, "costs": 0.0, "id": "CEIBBAS3161395200020029011", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20210226, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "VALE3", "amount": 100.0, "price": 96.55, "costs": 0.0, "id": "CEIVALE3161429760010096551", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20210305, "type": "STOCK", "operation": "SELL", "broker": "1099 - INTER DTVM LTDA", "ticker": "VALE3", "amount": 100.0, "price": 94.6, "costs": 0.0, "id": "CEIVALE3161490240010094601", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20210305, "type": "STOCK", "operation": "SELL", "broker": "1099 - INTER DTVM LTDA", "ticker": "BIDI11", "amount": 7.0, "price": 160.5, "costs": 0.0, "id": "CEIBIDI1116149024007160501", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20210305, "type": "STOCK", "operation": "SELL", "broker": "1099 - INTER DTVM LTDA", "ticker": "BIDI11", "amount": 22.0, "price": 160.5, "costs": 0.0, "id": "CEIBIDI11161490240022160501", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20210309, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "XINA11", "amount": 100.0, "price": 11.93, "costs": 0.0, "id": "CEIXINA11161524800010011931", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20210412, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "AAPL34", "amount": 100.0, "price": 74.65, "costs": 0.0, "id": "CEIAAPL34161818560010074651", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20210412, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "BABA34", "amount": 100.0, "price": 49.2, "costs": 0.0, "id": "CEIBABA34161818560010049201", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20210412, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "BCFF11", "amount": 19.0, "price": 85.65, "costs": 0.0, "id": "CEIBCFF1116181856001985651", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20210412, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "BCFF11", "amount": 2.0, "price": 85.65, "costs": 0.0, "id": "CEIBCFF111618185600285651", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20210412, "type": "STOCK", "operation": "BUY", "broker": "1099 - INTER DTVM LTDA", "ticker": "BCFF11", "amount": 3.0, "price": 85.65, "costs": 0.0, "id": "CEIBCFF111618185600385651", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20210412, "type": "STOCK", "operation": "SELL", "broker": "1099 - INTER DTVM LTDA", "ticker": "BIDI11", "amount": 31.0, "price": 188.02, "costs": 0.0, "id": "CEIBIDI11161818560031188021", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20210412, "type": "STOCK", "operation": "SELL", "broker": "1099 - INTER DTVM LTDA", "ticker": "BIDI11", "amount": 6.0, "price": 188.01, "costs": 0.0, "id": "CEIBIDI1116181856006188011", "alias_ticker": "", "external_system": "CEI"}, {"subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a", "date": 20210412, "type": "STOCK", "operation": "SELL", "broker": "1099 - INTER DTVM LTDA", "ticker": "BIDI11", "amount": 45.0, "price": 188.01, "costs": 0.0, "id": "CEIBIDI11161818560045188011", "alias_ticker": "", "external_system": "CEI"}], "assets_quantities": {"AESB3": 420.0, "ITSA4": 941.0, "WEGE3": 340.0, "FLRY3": 145.0, "HGBS11": 15.0, "HGLG11": 12.0, "KNRI11": 10.0, "1041": 2, "R$ 10,41": 2, "AAPL34": 100.0, "ALZR11": 20.0, "BABA34": 100.0, "BBAS3": 200.0, "BCFF11": 59.0, "BIDI11": 300.0, "IVVB11": 20.0, "MGLU3": 428.0, "MYPK3": 100.0, "NINJ3": 500.0, "RBRP11": 184.0, "SQIA3": 240.0, "VGIP11": 102.0, "VIIA3": 100.0, "XINA11": 100.0}}, "login_error": false}', 'attributes': {'ApproximateReceiveCount': '2', 'SentTimestamp': '1635372571445', 'SenderId': 'AROASAORJHNPF42FTSGDK:cei-crawler-dev-ceiExtractHandler', 'ApproximateFirstReceiveTimestamp': '1635372571453'}, 'messageAttributes': {}, 'md5OfBody': 'e3b4fff3dc6e31154afd49c15d7c31a2', 'eventSource': 'aws:sqs', 'eventSourceARN': 'arn:aws:sqs:sa-east-1:138414734174:CeiImportResult', 'awsRegion': 'sa-east-1'}]}
cei_import_result_handler(event, None)