import unittest
from unittest.mock import MagicMock
from server import Node

class NodeTestCase(unittest.TestCase):

    def setUp(self):
        self.node = Node(ping_port=20240, membership_port=20241, ping_timeout=2, ping_interval=2.5, log_filepath='test.log')

    def test_encode_command(self):
        result = self.node.encode_command('id123', {'test': 'command'})
        self.assertEqual(result, b'{"id": "id123", "command": {"test": "command"}}')

    def test_decode_command(self):
        id, command = self.node.decode_command(b'{"id": "id123", "command": {"test": "command"}}')
        self.assertEqual(id, 'id123')
        self.assertEqual(command, {'test': 'command'})

    def test_encode_ping_ack(self):
        result = self.node.encode_ping_ack('id123', 'ping')
        self.assertEqual(result, b'{"id": "id123", "type": "ping"}')

    def test_decode_ping_ack(self):
        id, type = self.node.decode_ping_ack(b'{"id": "id123", "type": "ping"}')
        self.assertEqual(id, 'id123')
        self.assertEqual(type, 'ping')

    # Add more test cases for other methods in the Node class.

if __name__ == '__main__':
    unittest.main()

