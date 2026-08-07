# Edge AI Intrusion Detection System

A high-performance edge Network Intrusion Detection System (NIDS) combining Linux AF_PACKET raw sockets, asynchronous packet ingestion, stateful feature engineering, and machine-learning-based threat detection.

## Overview

This project implements a lightweight Network Intrusion Detection System designed for bare-metal Linux environments.

The system captures network traffic directly from the Linux kernel using AF_PACKET raw sockets, extracts Layer 2–4 packet metadata, calculates stateful packet-rate features, and uses a Random Forest classifier to identify malicious TCP SYN flood traffic.

## Architecture

Physical Ethernet Interface
        ↓
AF_PACKET Raw Socket
        ↓
Asynchronous Packet Ingestion
        ↓
Feature Extraction
        ↓
Z-Score Normalisation
        ↓
Random Forest
        ↓
Compound Detection Logic
        ↓
Real-Time Alert

## Key Technologies

- Python
- Linux
- AF_PACKET raw sockets
- NumPy
- Scikit-learn
- TCP/IP
- Multithreading
- Statistical feature engineering
- Random Forest
- Performance benchmarking

## Performance

- Test dataset: 5,915 unseen samples
- Accuracy: 100%
- Precision: 100%
- Recall: 100%
- F1: 100%
- ROC-AUC: 1.0000
- Mean inference latency: 24.60 ms
- p99 latency: 47.69 ms
- Theoretical single-thread throughput: 41 packets/sec

## Running the Project

### Install dependencies

```bash
pip3 install -r requirements.txt