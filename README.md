# Edge AI Intrusion Detection System

A lightweight, high-performance Network Intrusion Detection System (NIDS) combining Linux kernel packet capture, asynchronous packet ingestion, stateful feature engineering, and machine-learning-based threat detection.

## Overview

This project implements an edge-based Network Intrusion Detection System designed for bare-metal Linux environments.

The system captures network traffic directly from the Linux kernel using AF_PACKET raw sockets, extracts Layer 2-4 packet metadata, generates stateful traffic features, and uses a Random Forest classifier to detect malicious TCP SYN flood traffic.

The aim of this project is to explore how machine learning can be deployed close to the network edge while maintaining low latency and minimal resource requirements.

---

## Architecture

```
Physical Ethernet Interface
            |
            v
AF_PACKET Raw Socket Capture
            |
            v
Asynchronous Packet Ingestion
            |
            v
Feature Extraction
            |
            v
Z-Score Normalisation
            |
            v
Random Forest Classifier
            |
            v
Detection Logic
            |
            v
Real-Time Alert
```

---

## Key Features

### High-Speed Packet Capture

- Linux AF_PACKET raw socket integration
- Direct kernel-level packet access
- Layer 2-4 traffic analysis
- Designed for lightweight edge deployment

### Stateful Feature Engineering

The system extracts network behaviour features including:

- Packet rates
- TCP flag information
- Protocol metadata
- Traffic statistics over time windows
- Source and destination information

### Machine Learning Detection

A Random Forest classifier is used to classify network behaviour and identify malicious TCP SYN flood activity.

The pipeline includes:

- Dataset preparation
- Feature extraction
- Feature normalisation
- Model training
- Evaluation
- Real-time inference

---

## Performance Results

Evaluation was performed using unseen test data.

| Metric | Result |
|---|---:|
| Accuracy | 100% |
| Precision | 100% |
| Recall | 100% |
| F1 Score | 100% |
| ROC-AUC | 1.0000 |
| Mean Inference Latency | 24.60 ms |
| p99 Latency | 47.69 ms |

---

## Project Structure

```
edge-ai-intrusion-detection/

├── artifacts/
│   ├── ids_rf_model.pkl
│   └── scaler.pkl
│
├── data/
│   ├── X_train.csv
│   ├── X_test.csv
│   ├── y_train.csv
│   ├── y_test.csv
│   ├── benign_telemetry.csv
│   └── malicious_telemetry.csv
│
├── docs/
│   └── Technical_Log_Book.pdf
│
├── src/
│   ├── capture_pipeline.py
│   ├── prep_dataset.py
│   ├── train_models.py
│   ├── live_ids.py
│   └── benchmark_ids.py
│
├── requirements.txt
└── README.md
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/pne35/edge-ai-intrusion-detection.git
```

Navigate into the project:

```bash
cd edge-ai-intrusion-detection
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

### Prepare Dataset

```bash
python src/prep_dataset.py
```

### Train Model

```bash
python src/train_models.py
```

### Run Benchmarking

```bash
python src/benchmark_ids.py
```

### Run Live Detection

```bash
python src/live_ids.py
```

---

## Technologies Used

- Python
- Linux
- AF_PACKET raw sockets
- NumPy
- Pandas
- Scikit-learn
- TCP/IP networking
- Machine learning
- Statistical feature engineering
- Multithreading
- Performance benchmarking

---

## Future Improvements

Potential future developments:

- Real-time monitoring dashboard
- Additional attack classifications
- Deep learning anomaly detection
- Containerised deployment
- Edge hardware deployment
- Automated model retraining pipeline

---

## Author

Harry Smalley

A-level Computer Science, Mathematics and Further Mathematics student developing projects across machine learning, cybersecurity, and systems programming.
