# Azure Function that implements GraphQL against a CosmosDB SQL endpoint

This is a ready to use Azure Function, based on the v4 runtime and Python 3.9. It creates a [GraphQL] endpoint to query against a CosmosDB SQL endpoint, with a GET to the `/api/graphql` endpoint you get a portal you can then use to query against the DB (with POST requests).

The documents for this are the sample documents you get when creating a CosmosDB, they have just an address as field (and that field is also the partition_key), as well as all CosmosDB default fields.

This project uses [Ariadne], which is a schema-first GraphQL package. So in this case the schema of your Cosmos DB document needs to be included in the schemas folder, the [Container schema](graphql//schemas//container.graphql) is a good starting place. Also provided are interfaces for [Cosmos](graphql//schemas//interface_cosmos.graphql) (other API's) and [Cosmos SQL](graphql//schemas//interface_cosmos_sql.graphql) that can be used to kickstart your schema.

Queries are done against the schema, where `Address` and `ID` are fields that can be included, if both are included then Cosmos will do a point lookup, otherwise a query is used, if `address` is not given that is a cross-partition query, which is potentially more expensive, so including the partititon key (in this case `address`) is advisable.

The mutation function uses the `upsert_item` function in Cosmos, so if the `ID` is given (`address` is mandatory) it will update that item with the new `address`, otherwise a new item is created.

### Query
[Query schema](graphql//schemas//query.graphql)
```graphql
{
  container(address: "2007, NE 37TH PL") {
  	address
    id
    timestamp
    _ts
  }
  costs
}
```

### Mutation
[Mutation schema](graphql//schemas//mutation.graphql)
```graphql
mutation {
  container(input: { address: "4200, 54th Avenue South" })
  costs
}
```

### Introspection
```graphql
{
  __type(name: "Container") {
    name
    description
    fields {
      name
      description
      type {
        name
        kind
      }
    }
  }
}```



[GraphQL]: https://graphql.org/
[Ariadne]: https://ariadnegraphql.org/