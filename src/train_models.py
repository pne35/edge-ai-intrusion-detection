from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ARTIFACTS = ROOT / "artifacts"


def main():
    print("[+] Phase 4: Training Intrusion Detection ML Models...")

    # 1. Load processed Phase 3 datasets
    X_train = pd.read_csv(DATA / "X_train.csv")
    X_test = pd.read_csv(DATA / "X_test.csv")
    y_train = pd.read_csv(DATA / "y_train.csv").values.ravel()
    y_test = pd.read_csv(DATA / "y_test.csv").values.ravel()

    # 2. Train Random Forest classifier
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    print("[+] Random Forest model training complete.")

    # 3. Model evaluation on the held-out test split
    y_pred = rf_model.predict(X_test)
    y_pred_proba = rf_model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba)

    print("\n" + "=" * 45)
    print("      PHASE 4 EVALUATION METRICS SUMMARY     ")
    print("=" * 45)
    print(f"Accuracy:  {acc * 100:.4f}%")
    print(f"Precision: {prec * 100:.4f}%")
    print(f"Recall:    {rec * 100:.4f}%")
    print(f"F1-Score:  {f1 * 100:.4f}%")
    print(f"ROC-AUC:   {roc_auc:.4f}")
    print("=" * 45)

    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Benign (0)", "Malicious (1)"]))

    # 4. Save model artifact for live inference
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    joblib.dump(rf_model, ARTIFACTS / "ids_rf_model.pkl")
    print("[+] Saved trained model artifact to artifacts/ids_rf_model.pkl.")

    # 5. Feature importance extraction
    importances = rf_model.feature_importances_
    features = X_train.columns

    print("\nFeature Importances:")
    for feat, imp in sorted(zip(features, importances), key=lambda x: x[1], reverse=True):
        print(f" - {feat:15s}: {imp * 100:.2f}%")


if __name__ == "__main__":
    main()
