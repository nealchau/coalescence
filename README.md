# Coalescense API 
This API queries several upstream base URLS for plan information given a
particular `member_id`.  The API coalesces the results, by default using the
arithmetic mean. The user can also optionally send weights to the API to
specify a strategy that weights the results' mean, median and mode. The API
can be imported as a Python API or can be instantiated as a Flask app. 

### Missing Data
If any upstream base URLs are unavailable, their data is skipped, and the data
which is acquired is used according to the coalescence strategy. If there is
no data available for a particular member, or if the query is malformed, then
"no data" is returned in a dict and rendered by Flask.

### Testing and Flask
The repository includes pytest tests for the python API and the Flask app.

## Dependency Inversion
The API is designed according to the [dependency inversion principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle) in the
functionality of requesting upstream data. In particular, the high-level
business logic of coalescing the plan information is independent of the
low-level API querying mechanism. This allows the API to query the upstream
APIs using the requests or urllib libraries through provided adaptors without
modification, and likewise enables the testing framework to provide simulated
results without modification. (In a production environment the choice of
adaptor could be defaulted or wrapped with a particular choice for end
users.)
