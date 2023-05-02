Our Code consists of two part, we will first discuss the Distributed Group Membership System, and then, we will expand the idea by Introducing the Distributed File System that is built upon the file system.

# Distributed Group Membership System

In this document, we will discuss the design choices and implementation of a distributed group membership system, focusing on the provided code(server.py).

## Design Choices

We will adapt a Gossip protocol here. In Gossip protocol, nodes in the network periodically exchange information with each other, usually by selecting a random or predetermined set of neighbors. The exchanged information can be any data, and here specifically for updates to the system state, new events, and failure detection. The protocol works in an asynchronous, decentralized manner and is resilient to node failures and network partitions

Key characteristics of Gossip protocols include:

1. Scalability: Gossip protocols can handle a large number of nodes, making them suitable for large-scale distributed systems.

2. Fault-tolerance: The protocol can tolerate node failures, as information dissemination does not rely on a single centralized point of communication. Even if some nodes fail, the information will still spread throughout the network.

3. Robustness: Gossip protocols are resistant to network partitions and can recover once the partitions are resolved. They can also adapt to changes in the network topology.

4. Simplicity: The protocol is simple to understand and implement, as it does not require complex algorithms or data structures.
### Node Representation and Initialization

Each node in the distributed system is represented by a `Node` class (lines 35). The class constructor initializes various parameters, such as the ping port (used for sending and receiving PING and ACK messages between the nodes in the distributed file system. PING messages are used to check the health of other nodes in the system, and the corresponding ACK messages are sent in response to acknowledge the receipt of PING messages), membership port (used for sending and receiving membership update messages between the nodes in the distributed file system. Membership updates are used to inform other nodes about changes in the membership list (e.g., adding or removing nodes).), and logging filepath (This is the file path where log information about the node is stored. The log information typically includes node activities like joining or leaving the system, as well as any errors or other relevant events), as well as several locks (preventing race conditions and ensuring the consistency of the data like membership_list, ack_cache, commands) and internal data structures (help maintain the system's state and allow efficient lookups and updates) to manage state and ensure thread safety.

When a node starts, the `join` method (lines 297) is called to register it with the group. The method assigns a unique ID to the node based on its host address and current timestamp (line 302). If the node is an introducer (The Master Node), it initializes its membership list with itself. Otherwise, it contacts the introducer to obtain the current membership list (311).
Then, we will start three threads to handle different aspects of the node's operation:

a. membership_thread: Handles membership-related tasks, such as updating the membership list.
b. ping_disseminate_thread: Handles the dissemination of ping messages to other nodes.
c. ping_ack_receive: Receives ping acknowledgments from other nodes.
### Membership Management

The membership list at each node is maintained using the `membership_list` attribute of the `Node` class. The `update_membership_list` method (lines 279) is responsible for adding or removing a node from the membership list based on the provided action and member_id. This method also generates log entries for join and leave events.

### Failure Detection and Fault Tolerance

The code implements a gossip-style failure detection mechanism. The `ping_disseminate_thread` method (lines 157) periodically sends ping messages to a subset of random nodes in the `ping_thread` (lines 198). The `ping_ack_receive` method (lines 177) listens for ping and ack messages and handles them accordingly using the `handle_ping` (lines 250) and `handle_ack` methods (lines 267). 

There is only one group at any point of time. Since we’re implementing the
crash/fail-stop model, when a machine rejoins, it must do so with an id that
includes a timestamp - this distinguishes successive incarnations of the same
machine (these are the ids held in the membership lists). Notice that the id also
has to contain the IP address.

A machine failure is reflected in at least one membership lists within 5
seconds (assuming synchronized clocks) – this is called time-bounded completeness,
A machine failure, join or leave must be reflected within 6 seconds at all membership lists,
assuming small network latencies (check Bandwidth).
### Bandwidth Efficiency

The code attempts to minimize bandwidth usage by using UDP and a selected subset of nodes for pinging (Lines 92,258). UDP is a connectionless protocol that doesn't guarantee the delivery of packets. It doesn't establish a connection before sending data and doesn't handle retransmissions or acknowledgments. This results in less overhead and lower bandwidth usage. Also, in a large distributed system, it would be inefficient for each node to communicate with every other node directly. Instead, the code selects a subset of nodes to send ping messages. This approach reduces the number of messages exchanged and the overall bandwidth usage.

We will use the `bandwidth` and `reset_time` commands (lines 245-252) can be used to monitor bandwidth usage.


With the above system, we will use the membership information to manage data storage, replication, and retrieval across nodes in the system. The membership system maintains a list of active nodes and their statuses, which helps the distributed file system make decisions about where and how to store and access data. The next step would be a distributed file system.

# Distributed File System 

## Overview

This documents the design and implementation of a distributed file system (DFS) based on the previous DMS. The DFS is a versioned file system that adheres to the following requirements:

1. Consistency levels with writes acknowledged by at least W (2) replicas, and reads by at least R (2) replicas.
2. Totally ordered updates for each file.
3. Reads return the latest written (and acknowledged) value.
4. A `get-versions` command that retrieves the specified number of versions for a given file.
5. Assumes num-versions is no more than 5 for simplicity
6. Ensures proper handling of node failures and rejoins.

## System Design
The system utilizes a previously implemented membership protocol to maintain a list of participating nodes. It also uses a file server to store and manage files in the distributed file system.

### Membership Protocol
The membership protocol is responsible for maintaining a list of active nodes in the system. It employs a ping-ack mechanism to monitor the status of nodes and updates the membership list accordingly ( see more details in the above section).

### File Server
The file server manages file storage and retrieval, ensuring consistency and versioning requirements. It communicates with other nodes using socket connections and follows the consistency levels of W and R replicas. The implementation uses W=2 and R=2, ensuring 2 ack is the least value that satisfies the consistency requirement.

## Code Walkthrough
The provided code (file_server.py) consists of a `FServer` class that serves as the main file server, managing both the membership protocol and the file system.

### Key Functions
1. `handle_put`: Handles the put operation for a file, sending the file to other nodes and updating the file table. (L284)
2. `handle_get`: Handles the get operation for a file, fetching the file from other nodes, and storing it in the local file cache. (L306)
3. `handle_delete`: Handles the delete operation for a file, sending the delete request to other nodes and updating the file table. (L341)
4. `handle_ls`: Handles the ls operation, updating the ls cache with the file information. (L364)
5. `handle_multiple_get`: Handles the get_versions command, fetching the specified number of versions for a given file. (L484-539)

### Key Data Structures
1. `FileTable`: A class that manages file storage, versioning, and metadata. (L73-187)
2. `file_cache`: A dictionary that stores the files fetched from other nodes. (L214)
3. `ls_cache`: A dictionary that caches the results of ls operations. (L215)
4. `put_ack_cache`: A dictionary that keeps track of put operation acknowledgments. (L216)
5. `get_ack_cache`: A dictionary that keeps track of get operation acknowledgments. (L217)

### Failure Handling
The system ensures proper handling of node failures and rejoins. When a node fails and rejoins, it wipes all file blocks/replicas it is storing before rejoining. The system handles failure scenarios, such as a node failing before or after receiving the confirmation notice.

Also, files are typically replicated across multiple nodes for fault tolerance and redundancy. When a node fails, the DFS will make sure that the files stored on the failed node are still available on other nodes in the network.

## Replication and Fault Tolerance in the Code

1. Replication: When a file is added to the system, the system stores replicas of the file on different nodes. This is handled outside the FMaster.py file. When the FMaster receives a 'put_notice' (L80-90), it updates the node_to_file and file_to_node mappings with the new file and node information. This ensures that the FMaster is aware of the location of each file replica.

2. Failure detection: In the FServer class, the ping_thread() method is responsible for detecting failures. It sends "ping" messages to other nodes in the system and waits for an "ack" (acknowledgment) response. If a node fails to send an acknowledgment within the specified ping_timeout, the system considers the node to have failed. The list of failed nodes' IP addresses is collected in the fail_ip list.

3. Recovery and fault tolerance: When a node is detected as failed, the FServer class sends a 'fail_notice' message to the FMaster class, containing the IP addresses of the failed nodes. The FMaster class then starts a new thread for each failed IP address and calls the repair() method.

The repair() method does the following:

a. Removes the failed node from the node_to_file and file_to_node dictionaries.
b. Re-replicates the files that were stored on the failed node to other available nodes. This is done by calling the issue_repair() method, which sends a 'repair' command to another node.

The other node that receives the 'repair' command in the FServer class executes the handle_repair_request() method. This method is responsible for ensuring the file is still available in the system after the node failure. It first checks if the file is present on the receiving node. If the file is present, no further action is needed, as the file is already replicated and available in the system. However, if the file is not present on the receiving node, the handle_repair_request() method calls the handle_replicate() method to replicate the file to another available node in the network. This step ensures that the file remains available and fault-tolerant, even if the original node has failed. It will try this to the next 3 nodes in the membership list that is not part of the deleted ips.

These mechanisms help to maintain fault tolerance in the distributed file system by ensuring that there are always multiple replicas of each file available on different nodes.

In summary, the code handles failure detection through periodic pinging and waiting for acknowledgments, just like what we did in the distributed file system. It achieves recovery and fault tolerance by re-replicating files from failed nodes to other available nodes in the system.

## Conclusion
The distributed file system implementation adheres to the requirements of consistency, versioning, and failure handling. It uses a membership protocol for maintaining active nodes and a file server for managing file storage and retrieval.

# Additional Notes

## Scalibility and Computing Resources:
We will be using the AWS EC2 machines. We will use 5 nodes VMs for the demo, but the code is expected to run on more than 5.

## FMaster

The FMaster class is responsible for managing the metadata of the distributed file system, handling node failures, and ensuring that files are properly replicated across the system. Here's a brief explanation of the methods and their roles in the system:

1. __init__(self, master_port: int, file_port: int): Initializes an FMaster object with the specified master and file port numbers, sets up the required data structures, and acquires the host IP address.

2. repair(self, ip): When a node failure is detected, this method is responsible for re-replicating the files that were stored on the failed node. It does this by iterating through the file IDs of the failed node, finding other nodes with the same file, and issuing a repair command to replicate the file to another available node.

3. issue_repair(self, sdfsfileid, ip, ips): This method sends a repair request to the specified IP address for the file with the provided file ID. It connects to the file server of the target node and sends the 'repair' command along with the file ID and a list of IPs where the file is currently stored.

4. background(self): This method runs the main background thread, which listens for incoming commands (fail_notice, put_notice, delete_notice) from other nodes. It processes these commands by either initiating the repair process for failed nodes, or updating the file-to-node and node-to-file mappings.

5. get_addr_thread(self): This method runs a separate thread that listens for incoming connections requesting the IP addresses of the nodes storing a specific file. When a connection is received, it sends back a list of IPs where the requested file is stored.

6. run(self): This method starts the FMaster service by running the main background thread and the address thread. It also provides a simple command-line interface for checking the state of the file-to-node and node-to-file mappings.

By managing the metadata, handling node failures, and ensuring proper replication, the FMaster class provides a robust and fault-tolerant distributed file system together with the DFS and DMS code above.


