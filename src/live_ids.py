import socket
import struct
import time
import joblib
import pandas as pd
import warnings

# Suppress feature name warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Load serialized ML artifacts from Phase 3 & 4
model = joblib.load("ids_rf_model.pkl")
scaler = joblib.load("scaler.pkl")

# Sliding window buffer to track rolling packet velocity
packet_timestamps = []

def get_packet_rate():
    """Calculates frame arrival rate over the last 1.0 second."""
    now = time.time()
    packet_timestamps.append(now)
    while packet_timestamps and packet_timestamps[0] < now - 1.0:
        packet_timestamps.pop(0)
    return len(packet_timestamps)

def main():
    # Open raw socket capturing all Ethernet frames (ETH_P_ALL)
    conn = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
    print("[+] Phase 5: Real-Time Intrusion Detection Engine is ACTIVE")
    print("[+] Listening on interface... (Press Ctrl+C to stop)\n")

    try:
        while True:
            raw_data, _ = conn.recvfrom(65535)
            packet_len = len(raw_data)
            rate_1s = get_packet_rate()

            # Parse 14-byte Ethernet Header
            if len(raw_data) < 14:
                continue
            eth_header = raw_data[:14]
            eth_proto = struct.unpack('!H', eth_header[12:14])[0]

            # Process IPv4 Traffic Only (EtherType 0x0800)
            if eth_proto != 0x0800:
                continue

            # Parse IP Header (Bytes 14 to 34)
            if len(raw_data) < 34:
                continue
            ip_header = raw_data[14:34]
            iph = struct.unpack('!BBHHHBBH4s4s', ip_header)
            protocol = iph[6]

            proto_tcp = 1 if protocol == 6 else 0
            proto_udp = 1 if protocol == 17 else 0
            proto_icmp = 1 if protocol == 1 else 0

            tcp_syn, tcp_ack, tcp_rst = 0, 0, 0

            # Extract TCP Flags if Protocol is TCP (6)
            if proto_tcp:
                ip_header_len = (iph[0] & 0xF) * 4
                tcp_start = 14 + ip_header_len
                tcp_header = raw_data[tcp_start:tcp_start + 20]
                if len(tcp_header) >= 20:
                    tcph = struct.unpack('!HHIIBBHHH', tcp_header)
                    flags = tcph[5]
                    tcp_syn = 1 if (flags & 0x02) else 0
                    tcp_ack = 1 if (flags & 0x10) else 0
                    tcp_rst = 1 if (flags & 0x04) else 0

            # Scale continuous features using Phase 3 DataFrame schema
            raw_cont = pd.DataFrame([[packet_len, rate_1s]], columns=['Packet_Length', 'Packet_Rate_1s'])
            scaled_cont = scaler.transform(raw_cont)
            scaled_len, scaled_rate = scaled_cont[0][0], scaled_cont[0][1]

            # Construct input vector for Random Forest Model
            feature_vector = pd.DataFrame([[
                scaled_len, proto_tcp, proto_udp, proto_icmp,
                tcp_syn, tcp_ack, tcp_rst, scaled_rate
            ]], columns=[
                'Packet_Length', 'Proto_TCP', 'Proto_UDP', 'Proto_ICMP',
                'TCP_SYN', 'TCP_ACK', 'TCP_RST', 'Packet_Rate_1s'
            ])

            # Model Inference
            prediction = model.predict(feature_vector)[0]
            probability = model.predict_proba(feature_vector)[0][1] * 100

            # Output Stream
            if (tcp_syn == 1 and tcp_ack == 0 and probability >= 20.0) or probability >= 50.0:
                print(f"[ALERT] SYN FLOOD DETECTED | Conf: {probability:.1f}% | Len: {packet_len}B | SYN: {tcp_syn} | Rate: {rate_1s} pps")
            else:
                print(f"[INSPECT] Benign Packet  | Conf: {probability:.1f}% | Len: {packet_len}B | SYN: {tcp_syn} | ACK: {tcp_ack} | Rate: {rate_1s} pps")

    except KeyboardInterrupt:
        print("\n[+] Detection Engine Stopped.")

if __name__ == "__main__":
    main()
