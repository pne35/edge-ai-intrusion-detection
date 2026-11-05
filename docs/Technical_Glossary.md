# Technical Glossary — Edge AI Intrusion Detection System

This is a plain-English guide to the terms used in my project logbook. It explains what each term means **and how it relates to my prototype**. It is a learning/reference document, not a record of extra experiments.

## Networking

### AF_PACKET raw socket
A Linux feature that lets my Python program read Ethernet frames directly. I used it to capture traffic without a packet-capture library such as Scapy.

### Ethernet frame
A block of data sent over a local network. It contains information my program can read, including the type of data inside it.

### IP address
A number identifying a device on a network. My test machines used `192.168.99.1` and `192.168.99.2`.

### TCP
A network protocol used to establish connections and transfer data reliably. My simulated attack targeted TCP connections.

### SYN flag
A bit in a TCP header that is normally set when a device starts a connection. My attack traffic had SYN set.

### ACK flag
A bit in a TCP header that acknowledges communication. The simulated attack packets had ACK unset.

### SYN flood
An attack that sends lots of TCP connection-start requests, potentially overwhelming a target. I generated simulated SYN-flood traffic in an isolated test setup.

### Packet rate
How many packets arrive in a given time. My project calculated a rate using a rolling one-second window.

### Header
Information at the start of a network packet, such as addresses and flags. I used headers rather than inspecting message contents.

### Deep Packet Inspection (DPI)
Examining the contents of network traffic, not just basic headers. My prototype did **not** perform DPI.

## Python and system design

### Binary parsing
Reading raw bytes and working out what each part means. My code extracted network information from packet headers.

### `struct`
A Python module that helps turn raw bytes into numbers and other values. I used it when reading packet headers.

### Thread
A sequence of work running within a program. My program used separate threads for receiving packets and writing data.

### Thread-safe queue
A waiting line for data that different threads can use safely. The capture thread put records in the queue; a background thread took them out to write them.

### Producer–consumer design
One part of a program creates data and another part processes it. This helped separate packet capture from CSV writing.

### Sliding window
A calculation that only looks at recent data. My one-second window tracked recent packet arrivals to estimate packet rate.

### CSV
A simple text file format for storing data in rows and columns. I used it to save packet features.

## Machine learning

### Feature
A piece of information the model uses to make a decision, such as packet length, TCP flags or packet rate.

### Label
The answer attached to a training example. My dataset labelled packets as benign (0) or malicious (1).

### Random Forest
A machine-learning model that combines many decision trees. Each tree helps decide which class a packet belongs to.

### Training data
Examples the model learns from. I used about 80% of my dataset for training.

### Test data
Examples used to check the model after training. I held back about 20% of my dataset for testing.

### Stratified train-test split
Dividing data into training and testing groups while keeping roughly the same percentage of benign and malicious packets in both. **I used one stratified 80/20 split, not K-fold cross-validation.**

### K-fold cross-validation
A different testing method that trains and tests a model several times using different sections of the data. **I did not use this method in the reported experiment.**

### StandardScaler / Z-score
A way to rescale numbers by comparing them with the training data's average and spread. I used it for numerical features such as packet length and packet rate.

### Classification threshold
The score above which the program calls a packet malicious. A common threshold is 0.50 (50%). My live program also used a lower 0.20 threshold **when SYN was set and ACK was unset**.

### Inference
Using an already-trained model to make a prediction on new data. Training is learning; inference is using what was learned.

## Model evaluation

### Accuracy
The percentage of all predictions that were correct. My model scored 100% **on its particular held-out test data**, not on every possible network.

### Precision
Of the packets the model flagged as malicious, how many really were malicious? Low precision means more false alarms.

### Recall
Of the packets that really were malicious, how many did the model catch? Low recall means more missed attacks.

### F1-score
A single score combining precision and recall. It helps assess both false alarms and missed attacks.

### False positive
A normal packet incorrectly flagged as malicious. A legitimate TCP connection could potentially trigger my SYN-based rule.

### False negative
A malicious packet incorrectly treated as normal. My lower-rate live probes initially fell below the model's usual 50% threshold.

### ROC-AUC
A score showing how well a model generally ranks malicious examples above benign examples across different thresholds. My score of 1.0 was perfect **for the controlled test dataset**; it does not prove the system works perfectly on unfamiliar traffic.

### Overfitting / poor generalisation
When a model performs well on familiar-looking data but struggles with different real-world examples. My benign and malicious datasets were unusually easy to tell apart, so the perfect offline results did not prove reliable detection elsewhere.

### Hold-out test
Checking a trained model on rows kept out of training. My hold-out rows came from the same overall collection conditions, not a completely separate capture session.

### Inference latency
How long it takes to prepare an input and run the trained model to get a prediction. My benchmark averaged **24.60 ms** for the measured feature-preparation, scaling and inference path, **not** the complete capture-to-alert process.

### p99 latency
A time that 99% of measured runs were at or below. My measured p99 was about **47.69 ms**.

### Throughput
How much work a system handles in a given time. Dividing one second by my 24.60 ms average gives about **41 sequential predictions per second for the measured path**; this is not a proven whole-system packet-processing limit.

## Security outcomes and limitations

### Intrusion detection
Noticing traffic that may be malicious and raising an alert. **This is what my prototype attempted to do.**

### Mitigation
Actually reducing or stopping an attack, for example by blocking traffic or limiting its rate. **My prototype did not mitigate attacks.** It captured, classified and alerted.

### Heuristic / rule-based detection
Making decisions using a simple rule instead of relying only on a trained model. My live decision was strongly influenced by whether SYN was set and ACK was unset, together with a model score.

### False-alarm risk
The possibility of flagging harmless activity as an attack. Since normal TCP connections begin with a SYN packet, my rule may flag legitimate traffic.

### Generalisation
How well a model works on new traffic unlike its training examples. I did not demonstrate strong generalisation to different networks or attack types.

---

## The key lesson from this project

**100% accuracy on a limited dataset does not mean a perfect security system.** My offline model separated the examples I collected, but low-rate live tests exposed weaknesses. I added a SYN/ACK-dependent rule to detect those probes, and the prototype **did not block or stop attacks**. The project taught me the difference between a promising laboratory result and a reliable, deployed detector.
