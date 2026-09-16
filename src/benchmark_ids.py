from pathlib import Path
import time
import warnings

import joblib
import numpy as np

# Suppress feature name validation warnings during array benchmark
warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"

# Load pipeline components
model = joblib.load(ARTIFACTS / "ids_rf_model.pkl")
scaler = joblib.load(ARTIFACTS / "scaler.pkl")

print("[+] Phase 6: Running Real-Time Inference Latency Benchmark...")

# Pre-allocate continuous input [Packet_Length=60, Packet_Rate_1s=20]
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

    # 1. Continuous feature scaling
    s = scaler.transform(raw_continuous)

    # 2. Vector construction
    feat = np.array([[s[0][0], 1, 0, 0, 1, 0, 0, s[0][1]]])

    # 3. Model inference
    _ = model.predict(feat)[0]

    t1 = time.perf_counter()
    latencies.append((t1 - t0) * 1e6)  # microseconds

mean_lat = np.mean(latencies)
median_lat = np.median(latencies)
p95_lat = np.percentile(latencies, 95)
p99_lat = np.percentile(latencies, 99)
max_throughput = 1e6 / mean_lat

print("\n" + "=" * 58)
print("       PHASE 6: REAL-TIME INFERENCE LATENCY BENCHMARK")
print("=" * 58)
print(f"Total Test Iterations             : {NUM_ITERATIONS:,}")
print(f"Mean Processing Time per Packet   : {mean_lat:.2f} µs")
print(f"Median Processing Time per Packet : {median_lat:.2f} µs")
print(f"95th Percentile Latency (p95)     : {p95_lat:.2f} µs")
print(f"99th Percentile Latency (p99)     : {p99_lat:.2f} µs")
print(f"Theoretical Max Engine Throughput : {max_throughput:,.0f} packets/sec")
print("=" * 58)
