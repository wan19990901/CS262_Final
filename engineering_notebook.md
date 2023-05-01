Our Code consists of two part

# Distributed Group Membership System

In this document, we will discuss the design choices and implementation of a distributed group membership system, focusing on the provided code(server.py) and its adherence to the requirements outlined in the prompt. 

## Design Choices

### Node Representation and Initialization

Each node in the distributed system is represented by a `Node` class (lines 16-30). The class constructor initializes various parameters, such as the ping port, membership port, and logging filepath, as well as several locks and internal data structures to manage state and ensure thread safety.

When a node starts, the `join` method (lines 175-203) is called to register it with the group. The method assigns a unique ID to the node based on its host address and current timestamp (line 179). If the node is an introducer (The Master Node), it initializes its membership list with itself. Otherwise, it contacts the introducer to obtain the current membership list (lines 193-200).

### Membership Management

The membership list at each node is maintained using the `membership_list` attribute of the `Node` class. The `update_membership_list` method (lines 143-160) is responsible for adding or removing a node from the membership list based on the provided action and member_id. This method also generates log entries for join and leave events.

### Failure Detection

The provided code implements a gossip-style failure detection mechanism. The `ping_disseminate_thread` method (lines 58-104) periodically sends ping messages to a random subset of nodes. The `ping_ack_receive` method (lines 105-137) listens for ping and ack messages and handles them accordingly using the `handle_ping` (lines 31-43) and `handle_ack` methods (lines 44-49). 

### Fault Tolerance

The system attempts to ensure fault tolerance by allowing up to three simultaneous failures. While the code implements a gossip-style failure detection mechanism, it is not clear whether the ring backbone is used as described in the prompt. The implementation should ensure that the ring backbone is maintained and utilized for failure detection and membership list updates, especially in the case of multiple simultaneous failures.

### Scalability

Although the provided code should work with a small number of nodes (N > 5), it is essential to thoroughly test the system with larger numbers of machines to evaluate its scalability.

### Bandwidth Efficiency

While the code attempts to minimize bandwidth usage by using UDP and a selected subset of nodes for pinging, it would be useful to track and log the bandwidth usage during runtime to ensure that the system remains bandwidth-efficient under various conditions. The `bandwidth` and `reset_time` commands (lines 245-252) can be used to monitor bandwidth usage.

## Evaluation of the Provided Code

The provided code appears to implement most of the design choices and requirements outlined in the prompt. However, there are a few potential areas for improvement or clarification:

1. Message Marshaling: The code does not explicitly demonstrate the marshaling of platform-dependent fields into a platform-independent format. It is crucial to ensure that messages are properly encoded and decoded between nodes with potentially different architectures.

2. Ring Backbone: As mentioned earlier, it is not clear whether the ring backbone is used as described in the prompt. The implementation should ensure that the ring backbone is maintained and utilized for failure detection and membership list updates.

3. Scalability: The provided code should be tested with larger numbers of machines to evaluate its scalability.

4. Bandwidth Efficiency: Monitoring and logging the bandwidth usage during runtime would be useful to ensure that the system remains bandwidth-efficient under various conditions.

In conclusion, the provided code is a solid starting point for implementing the distributed group membership system. By addressing the areas for improvement mentioned above and ensuring that the system.

With the distributed membership system, we further build a distributed file system based on the existing code.

# Distributed File System 

## Overview
This  documents the design and implementation of a distributed file system (DFS) based on the code. The DFS is a versioned file system that adheres to the following requirements:

1. Consistency levels with writes acknowledged by at least W replicas, and reads by at least R replicas.
2. Totally ordered updates for each file.
3. Reads return the latest written (and acknowledged) value.
4. A `get-versions` command that retrieves the specified number of versions for a given file.
5. Assumes num-versions is no more than 5.
6. Ensures proper handling of node failures and rejoins.

## System Design
The system utilizes a membership protocol to maintain a list of participating nodes. It also uses a file server to store and manage files in the distributed file system.

### Membership Protocol
The membership protocol is responsible for maintaining a list of active nodes in the system. It employs a ping-ack mechanism to monitor the status of nodes and updates the membership list accordingly.

### File Server
The file server manages file storage and retrieval, ensuring consistency and versioning requirements. It communicates with other nodes using socket connections and follows the consistency levels of W and R replicas. The implementation uses W=2 and R=2, ensuring (W+R) is the least value that satisfies the consistency requirement.

## Code Walkthrough
The provided code consists of a `FServer` class that serves as the main file server, managing both the membership protocol and the file system.

### Key Functions
1. `handle_put`: Handles the put operation for a file, sending the file to other nodes and updating the file table. (L342-394)
2. `handle_get`: Handles the get operation for a file, fetching the file from other nodes, and storing it in the local file cache. (L396-448)
3. `handle_delete`: Handles the delete operation for a file, sending the delete request to other nodes and updating the file table. (L450-463)
4. `handle_ls`: Handles the ls operation, updating the ls cache with the file information. (L465-482)
5. `handle_multiple_get`: Handles the get_versions command, fetching the specified number of versions for a given file. (L484-539)

### Key Data Structures
1. `FileTable`: A class that manages file storage, versioning, and metadata. (L73-187)
2. `file_cache`: A dictionary that stores the files fetched from other nodes. (L214)
3. `ls_cache`: A dictionary that caches the results of ls operations. (L215)
4. `put_ack_cache`: A dictionary that keeps track of put operation acknowledgments. (L216)
5. `get_ack_cache`: A dictionary that keeps track of get operation acknowledgments. (L217)

### Failure Handling
The system ensures proper handling of node failures and rejoins. When a node fails and rejoins, it wipes all file blocks/replicas it is storing before rejoining. The system handles failure scenarios, such as a node failing before or after receiving the confirmation notice.

## Replication and Fault Tolerance in the Code
1. Replication: When a file is added to the system, the system stores replicas of the file on different nodes. This is handled outside the FMaster.py file. When the FMaster receives a 'put_notice' (L80-90), it updates the node_to_file and file_to_node mappings with the new file and node information. This ensures that the FMaster is aware of the location of each file replica.

2. Fault Tolerance: When a node fails, the FMaster re-replicates the files that were stored on the failed node (L31-60). This is done as follows:

The FMaster receives a 'fail_notice' (L67-74) containing the IP addresses of the failed nodes.

For each failed node, the FMaster calls the repair function (L31-60) in a new thread.

In the repair function, the FMaster removes the failed node from the node_to_file mapping and retrieves the list of files that were stored on the failed node (L12-22).

For each file in the list, the FMaster attempts to find another node that has a replica of the file (L27-41). If it finds such a node, it sends a 'repair' command to the node along with the necessary information (e.g., the file ID and the list of other nodes that stored the file). The node then re-replicates the file to other nodes, ensuring that the desired replication factor is maintained.

These mechanisms help to maintain fault tolerance in the distributed file system by ensuring that there are always multiple replicas of each file available on different nodes.

## Conclusion
The distributed file system implementation adheres to the requirements of consistency, versioning, and failure handling. It uses a membership protocol for maintaining active nodes and a file server for managing file storage and retrieval.



