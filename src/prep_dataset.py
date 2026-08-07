import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

def main():
    print("[+] Phase 3 Data Engineering Engine Active...")

    # 1. Load Benign and Malicious Telemetry
    try:
        df_benign = pd.read_csv("benign_telemetry.csv")
        df_malicious = pd.read_csv("malicious_telemetry.csv")
        print(f"[+] Loaded benign dataset: {len(df_benign)} records")
        print(f"[+] Loaded malicious dataset: {len(df_malicious)} records")
    except FileNotFoundError as e:
        print(f"[-] Error: Missing telemetry files. Ensure benign_telemetry.csv and malicious_telemetry.csv exist.\n{e}")
        return

    # 2. Assign Ground-Truth Labels (0 = Benign, 1 = Malicious)
    df_benign['Label'] = 0
    df_malicious['Label'] = 1

    # 3. Concatenate into Master Dataset
    df_master = pd.concat([df_benign, df_malicious], ignore_index=True)
    print(f"[+] Combined Master Dataset Total Rows: {len(df_master)}")

    # 4. Data Cleaning & Drop Non-Predictive Features
    # Timestamps are dropped to prevent time-based overfitting in static models
    df_master.dropna(inplace=True)
    
    X = df_master.drop(columns=['Timestamp', 'Label'])
    y = df_master['Label']

    feature_names = X.columns.tolist()
    print(f"[+] Extracted Feature Vector Set ({len(feature_names)} features): {feature_names}")

    # 5. Stratified 80/20 Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"[+] Train Set: {len(X_train)} samples | Test Set: {len(X_test)} samples")

    # 6. Feature Normalization / Standard Scaling
    # Scale continuous features (Packet_Length, Packet_Rate_1s) while leaving binary flags intact
    continuous_features = ['Packet_Length', 'Packet_Rate_1s']
    
    scaler = StandardScaler()
    
    # Fit scaler ONLY on Training data to avoid Data Leakage
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()

    X_train_scaled[continuous_features] = scaler.fit_transform(X_train[continuous_features])
    X_test_scaled[continuous_features] = scaler.transform(X_test[continuous_features])

    # 7. Save Processed Artifacts for Phase 4 Model Training
    X_train_scaled.to_csv("X_train.csv", index=False)
    X_test_scaled.to_csv("X_test.csv", index=False)
    y_train.to_csv("y_train.csv", index=False)
    y_test.to_csv("y_test.csv", index=False)
    
    # Save the fitted scaler so the live inference engine in Phase 5 can use it
    joblib.dump(scaler, "scaler.pkl")
    print("[+] Dataset compilation complete! Exported X_train.csv, X_test.csv, y_train.csv, y_test.csv, and scaler.pkl.")

if __name__ == "__main__":
    main()
