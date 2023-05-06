import socket
import threading
import time
import unittest
from unittest.mock import Mock, patch
from FMaster import FMaster, MASTER_PORT, FILE_PORT

class TestFMaster(unittest.TestCase):

    def setUp(self):
        self.master = FMaster(MASTER_PORT, FILE_PORT)

    @patch('socket.socket')
    def test_issue_repair(self, mock_socket):
        mock_socket_instance = Mock()
        mock_socket.return_value = mock_socket_instance
        sdfsfileid = "file1"
        ip = "192.168.0.1"
        ips = ["192.168.0.1", "192.168.0.2"]
        mock_socket_instance.recv.return_value = b'1'

        result = self.master.issue_repair(sdfsfileid, ip, ips)
        self.assertEqual(result, '1')
        mock_socket_instance.connect.assert_called_once_with((ip, FILE_PORT))
        mock_socket_instance.send.assert_called()
        mock_socket_instance.recv.assert_called_once_with(1)

    @patch('socket.socket')
    def test_get_addr_thread(self, mock_socket):
        mock_socket_instance = Mock()
        mock_socket.return_value = mock_socket_instance
        conn = Mock()
        addr = ("192.168.0.1", 12345)
        mock_socket_instance.accept.return_value = (conn, addr)
        conn.recv.return_value = "file1".encode()
        test_ips = ["192.168.0.1", "192.168.0.2"]
        self.master.file_to_node = {"file1": set(test_ips)}

        with patch.object(self.master, "get_addr_thread", wraps=self.master.get_addr_thread) as wrapped:
            t = threading.Thread(target=self.master.get_addr_thread)
            t.start()
            time.sleep(1)  # Give some time for the thread to run
            t.join(timeout=1)  # Stop the thread

            self.master.ftn_lock.acquire()
            self.assertEqual(self.master.file_to_node, {"file1": set(test_ips)})
            self.master.ftn_lock.release()
            conn.send.assert_called_once_with(json.dumps(test_ips).encode())

    # Additional unit tests for other methods go here

if __name__ == "__main__":
    unittest.main()
