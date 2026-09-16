# Edge AI Intrusion Detection System

A lightweight Network Intrusion Detection System exploring how low-level Linux packet capture, stateful feature engineering and machine learning can be combined for real-time network monitoring.

## Overview

The system captures Ethernet frames directly from Linux using `AF_PACKET` raw sockets, parses IPv4/TCP metadata, maintains short-term traffic statistics and uses a Random Forest classifier to identify suspicious TCP SYN flood traffic.

The project is deliberately built close to the networking layer rather than relying on a high-level packet-capture library. The aim is to understand the full path from raw bytes to a real-time security decision.

## Architecture

```text
Linux network interface
        │
        ▼
AF_PACKET raw socket
        │
        ▼
Packet parsing
        │
        ▼
Stateful feature extraction
        │
        ▼
Feature scaling
        │
        ▼
Random Forest inference
        │
        ▼
Detection policy
        │
        ▼
Real-time alert
```

## Key technical features

### Raw packet capture

- Linux `AF_PACKET` raw sockets
- Ethernet and IPv4 header parsing using Python's `struct`
- TCP flag extraction
- No Scapy dependency for the core capture/parsing path

### Stateful features

The system derives features including:

- packet length;
- packet rate over a rolling one-second window;
- TCP/UDP/ICMP protocol indicators;
- TCP SYN, ACK and RST flags.

### Machine-learning pipeline

The training pipeline currently uses a Random Forest classifier with standardised continuous features. The fitted scaler and model are stored in `artifacts/` for reuse during live inference.

## Performance benchmark

`benchmark_ids.py` runs 1,000 inference iterations after a warm-up period and reports mean, median, p95 and p99 inference time.

The benchmark measures the scaling, feature-vector construction and Random Forest inference path; it does **not** represent total end-to-end packet-capture latency.

Run the benchmark locally to obtain measurements for your own machine:

```bash
python src/benchmark_ids.py
```

The benchmark script reports latency in microseconds and also gives a theoretical throughput derived from the mean inference time.

## Evaluation

The current dataset is a controlled initial evaluation of benign and malicious telemetry. The existing held-out split is useful for checking that the pipeline works, but the perfect initial metrics should **not** be interpreted as evidence of production-level detection performance.

The next evaluation stage is to expand the dataset across multiple traffic types and capture sessions and compare the Random Forest against a simpler packet-rate baseline. This will make false positives, false negatives and generalisation much more meaningful.

This distinction is important to the project: a high score on a homogeneous dataset is not the same thing as demonstrating robust intrusion detection.

## Project structure

```text
edge-ai-intrusion-detection/
├── artifacts/
│   ├── ids_rf_model.pkl
│   └── scaler.pkl
├── data/
│   ├── X_train.csv
│   ├── X_test.csv
│   ├── y_train.csv
│   ├── y_test.csv
│   ├── benign_telemetry.csv
│   └── malicious_telemetry.csv
├── docs/
│   └── Technical_Log_Book.pdf
├── src/
│   ├── capture_pipeline.py
│   ├── prep_dataset.py
│   ├── train_models.py
│   ├── live_ids.py
│   └── benchmark_ids.py
├── requirements.txt
└── README.md
```

## Installation

Linux is required for the live `AF_PACKET` capture component.

```bash
git clone https://github.com/pne35/edge-ai-intrusion-detection.git
cd edge-ai-intrusion-detection
pip install -r requirements.txt
```

## Usage

Prepare the dataset:

```bash
python src/prep_dataset.py
```

Train the model:

```bash
python src/train_models.py
```

Run the inference benchmark:

```bash
python src/benchmark_ids.py
```

Run live detection with the required network permissions:

```bash
sudo python src/live_ids.py
```

## Technologies

`Python` · `Linux` · `AF_PACKET` · `struct` · `NumPy` · `Pandas` · `Scikit-learn` · `TCP/IP` · `Machine Learning`

## Current limitations and next steps

- Current evaluation focuses on a controlled SYN-flood scenario.
- The dataset needs more varied traffic and independent capture sessions.
- A simple packet-rate baseline should be evaluated alongside the ML model.
- The capture path currently focuses on IPv4 traffic.
- More automated tests are needed around packet parsing and feature extraction.

## Author

Harry Smalley — Mathematics, Further Mathematics and Computing student interested in systems engineering, cybersecurity, machine learning and mathematical computing.
