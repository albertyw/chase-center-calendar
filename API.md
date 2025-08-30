Chase Center API Documentation
==============================

https://chasecenter.com has an API which seems to contain all dynamic information as a CMS.

The API endpoint is exposed at https://t6ky1u2if62shkupuk.us-central1.gcp.squid.cloud/query/batchQueries and responds to POST requests with the body:

```json
[
  {
    "query": {
      "integrationId": "built_in_db",
      "collectionName": "events",
      "conditions": [
        {
          "fieldName": "datetime",
          "operator": ">",
          "value": "2025-08-22T21:04:47.263585"
        }
      ],
      "limit": 60,
      "sortOrder": [
        {
          "asc": true,
          "fieldName": "datetime"
        }
      ]
    },
    "clientRequestId": "85ca30bc-cf7d-4a38-9f65-f97245227517'",
    "subscribe": false
  }
]
```

with the headers:

```
Content-Type: application/json
X-Squid-ClientID: 85ca30bc-cf7d-4a38-9f65-f97245227517
```

Oracle Park API Documentation
=============================

Oracle Park's official website does not contain an up-to-date comprehensive list of events.
Therefore, this site uses dothebay.com's data which does seem more complete.  This site
therefore parses its Oracle Park events from https://dothebay.com/venues/oracle-park/events.
