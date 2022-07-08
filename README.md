# Azure Function that implements GraphQL against a CosmosDB SQL endpoint

This is a ready to use Azure Function, based on the v4 runtime and Python 3.9. It creates a [GraphQL] endpoint to query against a CosmosDB SQL endpoint, with a GET to the `/api/graphql` endpoint you get a portal you can then use to query against the DB (with POST requests).

The documents for this are the sample documents you get when creating a CosmosDB, they have just an address as field (and that field is also the partition_key), as well as all CosmosDB default fields.

This project uses [Ariadne], which is a schema-first GraphQL package. So in this case the schema of your Cosmos DB document needs to be included in the schemas folder, the [Container schema](schemas//container.graphql) is a good starting place. Also provided are interfaces for [Cosmos](schemas//interface_cosmos.graphql) (other API's) and [Cosmos SQL](schemas//interface_cosmos_sql.graphql) that can be used to kickstart your schema. The container schema is the return type of a query to container

Queries are done against the schema, where `address` and `ID` are fields that can be included as a filter, if both are included then Cosmos will do a point lookup, otherwise a query is used, if `address` is not given that is a cross-partition query, which is potentially more expensive, so including the partititon key (in this case `address`) is advisable. The fields of `Container` can be selected in the query.

The mutation function uses the `upsert_item` function in Cosmos, so if the `ID` is given (`address` is mandatory), if you change the `address` it will actually create a new item in the updated partition, if you change something other then the partition key (`address` in this case) it will update the item.

For all details of how to implement the graphql refer to the [Ariadne] documentation. But there are four places that need to be updated to adopt this to your schema.

1. Schema's in the [schema](schema//) folder: 
    1. the container.graphql (also shown below) is the most important one to adopt, no need to change the name `Container`, it is internal only.
    1. the query and mutation schema's, remember that the return type of the Query is Container, the word `container` (no cap) can be changed to represent the type of object you want to query.
1. [Resolvers](graphql//resolvers//), you only need a resolver if you want to change a field's representation, if you want to create additional fields, or if you have to change the name between the item in Cosmos and the field name in the query, the [resolvers_specific.py](graphql//resolvers//resolvers_specific.py) file has an example of a resolver that takes the timestamp, converts it into a local timestamp and returns that as a ISO formatted field.
1. [Schema.py](graphql//schema.py) here the resolvers are added to the ObjectTypes (Ariadne specific thing) and linked to specific fields. 
1. Environment variables, if running this locally using the azure-func-tools, create a `local.settings.json` based on the [sample](sample.settings.json), if necessary (for instance if you want to use AAD auth with Cosmos instead of Key-based), change the way these are imported and used in [const](graphql//const.py) and [cosmos](graphql//cosmos.py). If you deploy this function to Azure make sure to sync the settings (VSCode can do this with a command) to the app settings there so that it works.

### Container definition
Container definition without descriptions, [full schema here][Container schema].
```graphql
type Container implements CosmosSQL {
    id: ID
    partition_key: String
    partition_key_field: String
    address: String
    _rid: String
    _self: String
    _etag: String
    _attachments: String
    _ts: Int
    timestamp: String
}
```

### Query
[Query schema](schemas//query.graphql)
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
[Mutation schema](schemas//mutation.graphql)
```graphql
mutation {
  container(input: { address: "4200, 54th Avenue South" })
  costs
}
```

### Introspection
[Introspection documentation](https://graphql.org/learn/introspection/)
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
}
```

[GraphQL]: https://graphql.org/
[Ariadne]: https://ariadnegraphql.org/
[Container schema]: schemas//container.graphql
