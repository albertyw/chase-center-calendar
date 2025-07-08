Chase Center API Documentation
==============================

https://chasecenter.com has a graphql API which seems to contain all dynamic information as a CMS.

An interactive GraphiQL is exposed at https://content-api-dot-chasecenter-com.appspot.com/graphql.

GraphQL API for chase-center-calendar:

```graphql
# , filters: {field: "fields.ticketSoldOut", value: true}
{
  contentByType(id: "event") {
    items {
      fields {
        ... on event {
          id
          slug
          title
          subtitle
          date
          locationName
          locationType
          ticketRequired
          ticketAvailable
          ticketSoldOut
          hideRoadGame
        }
      }
    }
  }
}
```

Oracle Park API Documentation
=============================

Oracle Park's official website does not contain an up-to-date comprehensive list of events.
Therefore, this site uses dothebay.com's data which does seem more complete.  This site
therefore parses its Oracle Park events from https://dothebay.com/venues/oracle-park/events.
