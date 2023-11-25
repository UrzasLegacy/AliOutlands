# from scapy.all import sniff
# from scapy.layers.http import HTTPRequest

# def monitor_packet(packet):
#     if packet.haslayer(HTTPRequest):
#         # Check if the packet's Host header contains the specific URL
#         #if 'https://uooutlands.com/wiki/Main_Page' in packet[HTTPRequest].Host.decode():
#         print(f"Accessed URL: {packet[HTTPRequest].Host.decode()}")

# def main():
#     print("Starting network monitoring")
#     sniff(filter="tcp port 80 or tcp port 443", prn=monitor_packet, store=False)

# if __name__ == "__main__":
#     main()


from scapy.all import sniff

def monitor_packet(packet):
    print(packet.summary())

sniff(filter="tcp", prn=monitor_packet, store=False)