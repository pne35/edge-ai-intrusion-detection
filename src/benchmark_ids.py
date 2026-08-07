import time
import joblib
import numpy as np
import warnings

# Suppress feature name validation warnings during array bench
warnings.filterwarnings("ignore")

# Load pipeline components
model = joblib.load("ids_rf_model.pkl")
scaler = joblib.load("scaler.pkl")

print("[+] Phase 6: Running Real-Time Inference Latency Benchmark...")

# Pre-allocate continuous input [Packet_Length=60, Packet_Rate_1s=20] as raw NumPy array
raw_continuous = np.array([[60.0, 20.0]])

NUM_ITERATIONS = 1000
latencies = []

# Warm up CPU cache
for _ in range(50):
    s = scaler.transform(raw_continuous)
    sample_vec = np.array([[s[0][0], 1, 0, 0, 1, 0, 0, s[0][1]]])
    _ = model.predict(sample_vec)

# High-precision benchmark loop
for _ in range(NUM_ITERATIONS):
    t0 = time.perf_counter()
    
    # 1. Continuous Feature Scaling
    s = scaler.transform(raw_continuous)
    
    # 2. Vector Construction: [scaled_len, proto_tcp, proto_udp, proto_icmp, tcp_syn, tcp_ack, tcp_rst, scaled_rate]
    feat = np.array([[s[0][0], 1, 0, 0, 1, 0, 0, s[0][1]]])
    
    # 3. Model Inference Execution
    _ = model.predict(feat)[0]
    
    t1 = time.perf_counter()
    latencies.append((t1 - t0) * 1e6)  # Convert to microseconds (µs)

mean_lat = np.mean(latencies)
p99_lat = np.percentile(latencies, 99)
max_throughput = 1e6 / mean_lat

print("\n==================================================")
print("     PHASE 6: REAL-TIME INFERENCE LATENCY BENCHMARK")
print("==================================================")
print(f"Total Test Iterations            : {NUM_ITERATIONS:,}")
print(f"Mean Processing Time per Packet  : {mean_lat:.2f} µs")
print(f"99th Percentile Latency (p99)    : {p99_lat:.2f} µs")
print(f"Theoretical Max Engine Throughput : {max_throughput:,.0f} packets/sec")
print("==================================================")
