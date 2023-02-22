# Locking Overview

We use two locks for fine grained access protection of server-wide user metadata. There are three main structures that we need to provide access protection to. 

1. The `user_metadata_store`. This contains the information about the user's username, password and full name details. The requests that it interacts with are `ListAccount`, `DeleteAccount`, `CreateAccount` and `LoginRequest`. There are obvious contention issues here, such as a delete account being called concurrenty with a list account. To ensure consistency. Both requests must have contention with the `app.metadata_lock`. The same goes for the other aforementioned interactions as well. 

2. The `token_hub`. This contains a mapping between active tokens registered under usernames and their associated timestamps for expired connection permissions. The requests that it interacts with are `ListAccount`, `DeleteAccount`, `CreateAccount`, `RefreshRequest`, `MessageRequest` and `LoginRequest`. Every time this hub is consulted in the `ValidateToken` method, it is called using protection of the `app.metadata_lock`. 

3. The last object is the `user_inbox`. This is a dictionary with nested message queues for undelivered messages that are mapped with keys corresponding to usernames. This is likely the most contended with object in the Chat Server, hence there is another lock for ensuring its protection. This is the `app.inbox_lock`. The lock is called after the metadata lock at times and sometime without it. It functions independently allowing for less contention than in a scenario where a global big lock would serialize all requests. 

## Locking Usage

We ensure that all locking is called using the `with` pythonic syntax that ensures that the lock is not held, even when a function returns or a scope is suddenly (unexpectedly) terminated. Moreover, we never keep any lock for a thread when yielding as this can lead to a host of problems and thread unfairness. 

## Locking Hierarchy

In order to prevent deadlocks, we maintain the following locking structure.

(1) `app.metadata_lock`

(2) `app.inbox_lock`

At any given time this is the order in which they are held, and the reverse in which they are released. We use nested `with` statements to prevent locking scope issues. 