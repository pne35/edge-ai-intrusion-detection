# Technical Log Book — Required Corrections and Final Critical Evaluation

This amendment accompanies `docs/Technical_Log_Book.pdf`. It records corrections to the original logbook and provides the missing final evaluation. The original experimental results are retained; claims are qualified where the evidence does not support broader conclusions.

## Corrections to the existing logbook

### Phase 0 — topology and hypothesis

Change “a three-node physical network topology” to “a two-node physical network topology”, consistent with the attacker/defender setup described in Phase 1.

Replace the original hypothesis with:

> **Hypothesis:** A machine-learning-driven network defender can identify simulated volumetric attack traffic using low-level packet metadata while maintaining sufficiently low processing overhead on a dedicated edge device.

The project did not demonstrate attack mitigation. It demonstrated packet capture, classification and alerting only. The original mitigation objective was therefore not achieved.

### Phase 2 — socket behaviour

The implementation calls ordinary blocking `recvfrom(65535)`; it does not configure the socket as non-blocking. Replace “via non-blocking recvfrom execution” with:

> The ingestion thread receives frames using the socket's blocking `recvfrom()` operation. Packet parsing and queue dispatch are kept separate from CSV writing, which is performed by a background consumer thread. This producer-consumer design reduces the amount of work performed before the next receive operation.

### Phase 4 — evaluation method

Replace “using Stratified K-Fold logic” with:

> Model performance was evaluated using the stratified 20% hold-out test subset created during preprocessing (N = 5,915). The remaining 80% was used for training. Stratification preserved the class proportions in both subsets. This was a single train-test split, not Stratified K-Fold cross-validation.

### Phase 4 — interpretation of 100% metrics

Keep the measured 100% accuracy, precision, recall, F1-score and ROC-AUC, but add:

> **Critical evaluation of offline results:** The Random Forest achieved 100% on the held-out test subset from this dataset. However, this result reflects separation within a controlled and relatively narrow dataset, not proven generalisation to different networks or attack behaviours. The benign and malicious samples had highly distinctive characteristics: the simulated SYN flood consisted of fixed-length TCP packets with SYN asserted and ACK unset, whereas the benign capture had a very different flag distribution and packet-length profile. The random stratified split also allowed samples from the same capture conditions to appear in both training and testing subsets. Consequently, the test set was unseen at row level but was not an independent capture-session evaluation. The perfect scores therefore exposed a limitation in the experimental dataset: it was too easy for the model to separate the two collected classes. Further training and testing on varied, independently captured benign traffic and multiple attack types would be necessary before claiming robust detection.

### Phase 5 — live detection and rule dependence

Add the following after the compound decision rule and its reported results:

> **Critical evaluation of the live detection approach:** The live tests showed that the raw Random Forest probability was not a reliable standalone decision threshold for the lower-rate probes used during deployment. The compound rule improved the number of simulated SYN probes that triggered alerts, but it also made the decision heavily dependent on a simple TCP flag condition: SYN = 1 and ACK = 0, combined with a probability threshold. This is close to a rule-based SYN/ACK check rather than a sufficiently discriminating machine-learning intrusion detector. An initial SYN packet can also occur during a legitimate TCP connection attempt, so treating this flag combination as sufficient evidence of an attack risks false positives in normal traffic. The limited benign test sample did not establish that this rule would maintain a low false-positive rate in a wider network environment. The rule therefore demonstrated a way to detect the specific probes used in testing, but it did not establish robust attack detection.

Where the logbook currently says “0% False Positives on Benign Traffic”, use:

> No false positives were observed in the benign traffic sample used for this live test. This result is limited to that sample and should not be interpreted as a general false-positive rate.

### Phase 6 — benchmark interpretation

Replace “Monte Carlo inference passes” with “1,000 benchmark iterations” unless the inputs were randomly sampled.

Replace the claim that the engine “processed every incoming attack frame in real time without dropping socket memory buffers” with:

> During the low-rate live tests (approximately 9–20 packets/sec), the engine processed the observed attack traffic without reported packet loss. The benchmark measured a mean single-frame processing time of approximately 24.60 ms, equivalent to a theoretical rate of around 41 frames/sec for that measured processing path. This is substantially below the packet rate required for high-throughput or line-rate capture. The result therefore identifies per-frame Python inference and feature preparation as a major performance limitation. The low-rate experiment demonstrates operation under the tested conditions only; it does not demonstrate the ability to sustain volumetric flood traffic.

Also change “full line-rate capacity” in Phase 1.5 to “approximately 900 Mbps on the 1 Gbps Ethernet link”.

## Phase 7 — Project conclusion and critical reflection

The original objective was to develop a machine-learning-driven network defender capable of identifying and mitigating volumetric attacks while maintaining low processing overhead. The project achieved some of its technical objectives, but it did **not** achieve the mitigation objective and did not produce a robust, general-purpose intrusion detection system.

A working prototype was developed to capture Ethernet frames using Linux AF_PACKET raw sockets, parse selected IPv4 and TCP header fields, extract packet-level features, record telemetry and apply a Random Forest classifier. The project also established a repeatable two-node test environment and measured the processing cost of the inference pipeline.

The offline model achieved 100% accuracy, precision, recall and F1-score, with an ROC-AUC of 1.0000, on the stratified hold-out subset. Initially, these results appeared to indicate excellent classification. However, analysis of the dataset showed that the two classes were unusually easy to distinguish: the simulated malicious traffic consisted of highly consistent SYN-only packets, while the benign traffic had a markedly different distribution. The random split did not test generalisation to a separate capture session or a different network. The 100% result was therefore a property of the limited experimental dataset, not evidence that the model could reliably identify attacks in realistic, varied traffic.

Live testing exposed a further weakness. Low-rate SYN probes produced Random Forest probabilities of approximately 27–28%, below the original 50% decision threshold. A compound rule was introduced to trigger alerts for packets with SYN asserted and ACK unset when the model probability exceeded 20%. This improved detection of the particular probes tested, but it made the final decision logic heavily dependent on a simple TCP flag check. In practical terms, the final system was close to a glorified SYN-without-ACK detector rather than a robust machine-learning NIDS. Legitimate TCP connection attempts can also begin with SYN set and ACK unset, so this rule could generate false positives in a wider network environment. The small benign test sample was not sufficient to rule this out.

The project also failed to meet its original mitigation aim. The system generated alerts and classified packets; it did not block, rate-limit or otherwise stop malicious traffic. It should therefore be described as a prototype detection and monitoring system, not an attack mitigation system. This is an important shortcoming against the original hypothesis, and the hypothesis was not fully supported.

Performance testing identified another limitation. The measured mean processing time was approximately 24.60 ms per frame, corresponding to a theoretical single-threaded processing rate of about 41 frames per second for the measured path. This may be adequate for the low-rate probes used in testing, but it is not sufficient to claim high-throughput or line-rate protection. The project did not demonstrate an ultra-low CPU footprint or sustained processing under a high-volume attack.

The main learning outcome was that successful model training and high offline scores do not guarantee a useful deployed security system. The live tests revealed weaknesses that were not apparent from the offline metrics, and the attempt to compensate with a heuristic rule exposed the danger of overfitting the detection logic to one attack signature. The project improved my understanding of raw packet capture, binary protocol parsing, concurrency, feature engineering, model evaluation and the difference between a laboratory result and a deployable system.

Further work would require collecting a much broader dataset across independent capture sessions, including varied legitimate TCP connection attempts and multiple attack types. The model should be compared against a simple rule-based baseline using a separate test environment, with false positives and false negatives reported explicitly. The detection policy should use traffic context and rates over time rather than relying on a single SYN/ACK pattern. Finally, mitigation would need to be designed and tested as a separate component, with safeguards to avoid blocking legitimate traffic. Inference would also need substantial optimisation before the system could be considered for high-throughput deployment.

**Overall conclusion:** The project successfully produced and evaluated a low-level packet-capture and alerting prototype, but it failed to achieve its original goal of mitigating attacks and did not establish robust general-purpose detection. Recognising and explaining these limitations is a central outcome of the project.
