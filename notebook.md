# General Design Paradigm:


# Files Docs:

## FMaster.py:

This code defines a class FMaster for managing a distributed file system's metadata.The class provides functions to keep track of which nodes have copies of specific files and to handle node failures by re-replicating files stored on the failed node

Funcionality:

'__init__': Initialize the instance variables, including dictionaries for maintaining the mapping of nodes to files and files to nodes, as well as locks for thread synchronization.

'repair': Handle the failure of a node by re-replicating files stored on that node to other available nodes.

'issue_repair': Send a repair command to a specific node to re-replicate a file.

'background': Continuously listen for incoming commands and handle them accordingly (e.g., fail_notice, put_notice, delete_notice).

'get_addr_thread': Continuously listen for incoming connections and send back the list of nodes storing a requested file.
run: Start the background and get_addr_thread and enter an interactive loop to handle user commands, such as printing the current state of node-to-file and file-to-node mappings.

The main script initializes an FMaster instance and calls its run() method to start the metadata management service. The code assumes that the system uses a single master node to manage file metadata, and the master communicates with other nodes through sockets.

## Node Failure:

When a node failure is detected, the background function handles it as follows:

The background function listens for incoming commands. When it receives a command with the command_type set to 'fail_notice', it processes the command.

The command content contains the list of failed IPs. The function iterates through this list of failed IPs, and for each failed IP, it starts a new thread to execute the repair method with the failed IP as an argument.

fail_ip = decoded_command['command_content']
for ip in fail_ip:
    t = threading.Thread(target=self.repair, args=(ip, ))
    t.start()

Inside the repair method, the code first acquires the lock for node_to_file and checks if the failed IP exists in the node_to_file dictionary. If it does, the method retrieves the list of file IDs stored on the failed node and removes the entry for the failed IP from the dictionary. The lock is then released.

The method iterates through each file ID in the retrieved list, acquires the lock for file_to_node, and checks if the file ID exists in the file_to_node dictionary. If it does, it retrieves the list of IPs storing the file and removes the failed IP from the list.

The method then iterates through the remaining IPs in the list, attempting to issue a repair for each IP using the issue_repair function. If the repair is successful (indicated by a return value of '1'), the method breaks out of the loop, assuming that the file has been re-replicated.

After iterating through all the file IDs, the method prints out the results, including the files re-replicated and the time consumed during the repair process.

In summary, when a node failure is detected, the code starts a repair process that removes the failed node from the relevant data structures and attempts to re-replicate the files stored on the failed node to other available nodes.

# Re-replication:


## Server.py
