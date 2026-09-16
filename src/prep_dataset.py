from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ARTIFACTS = ROOT / "artifacts"


def main():
    print("[+] Phase 3 Data Engineering Engine Active...")

    # 1. Load Benign and Malicious Telemetry
    try:
        df_benign = pd.read_csv(DATA / "benign_telemetry.csv")
        df_malicious = pd.read_csv(DATA / "malicious_telemetry.csv")
        print(f"[+] Loaded benign dataset: {len(df_benign)} records")
        print(f"[+] Loaded malicious dataset: {len(df_malicious)} records")
    except FileNotFoundError as e:
        print(
            "[-] Error: Missing telemetry files. Ensure "
            "data/benign_telemetry.csv and data/malicious_telemetry.csv exist.\n"
            f"{e}"
        )
        return

    # 2. Assign Ground-Truth Labels (0 = Benign, 1 = Malicious)
    df_benign["Label"] = 0
    df_malicious["Label"] = 1

    # 3. Concatenate into Master Dataset
    df_master = pd.concat([df_benign, df_malicious], ignore_index=True)
    print(f"[+] Combined Master Dataset Total Rows: {len(df_master)}")

    # 4. Data Cleaning & Drop Non-Predictive Features
    # Timestamps are dropped to prevent time-based overfitting in static models
    df_master.dropna(inplace=True)

    X = df_master.drop(columns=["Timestamp", "Label"])
    y = df_master["Label"]

    feature_names = X.columns.tolist()
    print(f"[+] Extracted Feature Vector Set ({len(feature_names)} features): {feature_names}")

    # 5. Stratified 80/20 Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"[+] Train Set: {len(X_train)} samples | Test Set: {len(X_test)} samples")

    # 6. Feature Normalization / Standard Scaling
    continuous_features = ["Packet_Length", "Packet_Rate_1s"]

    scaler = StandardScaler()

    # Fit scaler ONLY on Training data to avoid Data Leakage
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()

    X_train_scaled[continuous_features] = scaler.fit_transform(X_train[continuous_features])
    X_test_scaled[continuous_features] = scaler.transform(X_test[continuous_features])

    # 7. Save Processed Artifacts
    DATA.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    X_train_scaled.to_csv(DATA / "X_train.csv", index=False)
    X_test_scaled.to_csv(DATA / "X_test.csv", index=False)
    y_train.to_csv(DATA / "y_train.csv", index=False)
    y_test.to_csv(DATA / "y_test.csv", index=False)

    # Save the fitted scaler so the live inference engine can reuse it
    joblib.dump(scaler, ARTIFACTS / "scaler.pkl")
    print(
        "[+] Dataset compilation complete! Exported processed datasets to data/ "
        "and scaler.pkl to artifacts/."
    )


if __name__ == "__main__":
    main()
