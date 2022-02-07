from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Attr, Key

DATE = "20220101"
table = boto3.resource("dynamodb").Table("MarketData")

done = False
start_key = None
scan_kwargs = {"FilterExpression": Key("candle_date").eq(DATE)}
items = []

while not done:
    if start_key:
        scan_kwargs["ExclusiveStartKey"] = start_key
    response = table.scan(**scan_kwargs)
    start_key = response.get("LastEvaluatedKey", None)
    done = start_key is None
    items += response.get("Items", [])

for item in items:
    if item["open_price"] == 0:
        continue
    print(item["ticker"] + ";" + str(
        Decimal(((item["close_price"] * 100) / item["open_price"]) - 100).quantize(Decimal("0.01"))))
