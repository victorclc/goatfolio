import boto3
from boto3.dynamodb.conditions import Key

market_data = boto3.resource("dynamodb").Table("MarketData")

done = False
start_key = None

scan_kwargs = {"FilterExpression": Key("candle_date").eq("20211001")}
items = []
while not done:
    if start_key:
        scan_kwargs["ExclusiveStartKey"] = start_key
    response = market_data.scan(**scan_kwargs)
    start_key = response.get("LastEvaluatedKey", None)
    done = start_key is None
    items += [i["ticker"] for i in response.get("Items", [])]


done = False
start_key = None

scan_kwargs = {"FilterExpression": Key("candle_date").eq("20211101")}
november = []
while not done:
    if start_key:
        scan_kwargs["ExclusiveStartKey"] = start_key
    response = market_data.scan(**scan_kwargs)
    start_key = response.get("LastEvaluatedKey", None)
    done = start_key is None
    november += [i["ticker"] for i in response.get("Items", [])]

print([x for x in items if x not in november])
print("Symetric: ")
print(set(items).symmetric_difference(set(november)))
