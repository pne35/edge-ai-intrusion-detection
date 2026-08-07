import socket
import struct
import sys
import time
import csv
import queue
import threading
from collections import deque

# --- CONFIGURATION & STORAGE TARGETS ---
TARGET_IP = "192.168.99.2"
OUTPUT_CSV = "network_telemetry.csv"
WINDOW_SIZE_SEC = 1.0

packet_queue = queue.Queue()
shutdown_event = threading.Event()
sliding_window = deque()
window_lock = threading.Lock()

def parse_ip_address(byte_string):
    return '.'.join(str(b) for b in byte_string)

def async_writer_worker():
    """Consumes parsed vectors from the queue and flushes them to disk asynchronously."""
    import os
    file_exists = os.path.isfile(OUTPUT_CSV)
    with open(OUTPUT_CSV, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "Timestamp", "Packet_Length", "Proto_TCP", "Proto_UDP", 
                "Proto_ICMP", "TCP_SYN", "TCP_ACK", "TCP_RST", "Packet_Rate_1s"
            ])

        while not shutdown_event.is_set() or not packet_queue.empty():
            try:
                data = packet_queue.get(timeout=0.5)
                arrival_time, total_length, proto_tcp, proto_udp, proto_icmp, flag_syn, flag_ack, flag_rst = data
                
                # Dynamic stateful window evaluation
                with window_lock:
                    sliding_window.append(arrival_time)
                    cutoff = arrival_time - WINDOW_SIZE_SEC
                    while sliding_window and sliding_window[0] < cutoff:
                        sliding_window.popleft()
                    packet_rate = len(sliding_window) / WINDOW_SIZE_SEC

                writer.writerow([
                    f"{arrival_time:.6f}", total_length, proto_tcp, proto_udp, 
                    proto_icmp, flag_syn, flag_ack, flag_rst, packet_rate
                ])
                packet_queue.task_done()
            except queue.Empty:
                continue

def main():
    try:
        raw_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
    except PermissionError:
        print("[-] Error: Script must be executed with root privileges (sudo).")
        sys.exit(1)

    print("[+] Ingestion layer active. Capturing and serializing to disk...")
    
    # Spin up disk I/O daemon
    writer_thread = threading.Thread(target=async_writer_worker, daemon=True)
    writer_thread.start()

    try:
        while True:
            raw_data, _ = raw_socket.recvfrom(65535)
            arrival_time = time.time()

            eth_header = raw_data[:14]
            _, _, eth_proto = struct.unpack('! 6s 6s H', eth_header)
            
            if eth_proto != 0x0800:
                continue

            ip_header_raw = raw_data[14:34]
            ip_header = struct.unpack('! B B H H H B B H 4s 4s', ip_header_raw)
            
            ihl = (ip_header[0] & 0x0F) * 4
            total_length = ip_header[2]
            protocol_id = ip_header[6]
            dest_ip = parse_ip_address(ip_header[9])

            # Filter out frames not bound for our target interface node
            if dest_ip != TARGET_IP:
                continue

            # Default flag/protocol states
            proto_tcp = proto_udp = proto_icmp = 0
            flag_syn = flag_ack = flag_rst = 0

            if protocol_id == 6:  # TCP
                proto_tcp = 1
                tcp_start = 14 + ihl
                tcp_header_raw = raw_data[tcp_start:tcp_start + 20]
                if len(tcp_header_raw) >= 20:
                    tcp_header = struct.unpack('! H H L L B B H H H', tcp_header_raw)
                    flags = tcp_header[5]
                    flag_syn = (flags & 0x02) >> 1
                    flag_ack = (flags & 0x10) >> 4
                    flag_rst = (flags & 0x04) >> 2
            elif protocol_id == 17:  # UDP
                proto_udp = 1
            elif protocol_id == 1:   # ICMP
                proto_icmp = 1

            # Dispatch vector to background thread immediately
            packet_queue.put((arrival_time, total_length, proto_tcp, proto_udp, proto_icmp, flag_syn, flag_ack, flag_rst))

    except KeyboardInterrupt:
        print("\n[*] Gracefully halting execution engine...")
    finally:
        shutdown_event.set()
        writer_thread.join()
        print("[+] Storage buffer flushed cleanly. Data ready for Phase 3.")

if __name__ == "__main__":
    main()
