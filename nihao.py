import socket
import netifaces as ni

def get_active_ip_address():
    # Get the default gateway to identify the active network interface
    default_gateway = ni.gateways()['default'][ni.AF_INET][1]

    # Get the IP address associated with the active network interface
    ip_address = ni.ifaddresses(default_gateway)[ni.AF_INET][0]['addr']

    return ip_address

if __name__ == "__main__":
    ip_address = get_active_ip_address()
    print(f"Your active IP address is: {ip_address}")
    print('1231234')
