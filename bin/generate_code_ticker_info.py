import boto3
from boto3.dynamodb.conditions import Key

ticker_data = boto3.resource("dynamodb").Table("TickerInfo")

done = False
start_key = None

scan_kwargs = {}
items = []

while not done:
    if start_key:
        scan_kwargs["ExclusiveStartKey"] = start_key
    response = ticker_data.scan(**scan_kwargs)
    start_key = response.get("LastEvaluatedKey", None)
    done = start_key is None
    items += response.get("Items", [])

print(items)

for item in items:
    item["code"] = item["ticker"][:4]
    # ticker_data.put_item(Item=item)

print("arrumei a porra toda")

with ticker_data.batch_writer() as batch:
    for item in items:
        batch.put_item(Item=item)
