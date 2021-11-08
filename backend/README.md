### Back-end

Back-end services that makes up the Goatfolio functionalities as of now:

Service | Language | Description
------------------------------------------------- | ------------------------------------------------- | ---------------------------------------------------------------------------------
[cei-crawler](./backend/cei-crawler/README.md) | Python | Responsible to craw all stock investments of a user contained in the CEI website.
[corporate-events](./backend/corporate-events/README.md) | Python | Responsible to craw and process corporate events data, validate if a corporate events its applicable to new investments added.  
[event-notifier](./backend/event-notifier/README.md) | Python | Send discord alerts and notifications.
[market-history](./backend/market-history/README.md) | Python | Responsible to craw and persist market history data (B3 cotahist)
[portfolio-api](./backend/portfolio-api/README.md) | Python | Handle CRUDs of the investments, consolidate those investments into a Portfolio, calculate its performance.
[push-notifications](./backend/push-notifications/README.md) | Python | Sends push notifications for the users
[vandelay-api](./backend/vandelay-api/README.md) | Python | Triggers the crawler, manage import status, process import result