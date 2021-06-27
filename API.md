Chase Center API Documentation
==============================

https://chasecenter.com has a graphql API which seems to contain all dynamic information as a CMS.

An interactive GraphiQL is exposed at https://content-api-dot-chasecenter-com.appspot.com/graphql.

GraphQL API for chase-center-calendar:

```grqphql
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
