# files/model_trainer.py
from pathlib import Path
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "processed_data" / "player_data.csv"
MODEL_DIR = BASE_DIR / "trained_models"
MODEL_PATH = MODEL_DIR / "player_goal_model.pkl"

# ✅ 예측에 사용할 피처(입력 폼과 맞춰야 함)
FEATURES = [
    "Minutes",
    "Shots",
    "Shots On Target",
    "Assists",
    "Passes Attempted",
    "Passes Completed",
    "Expected Goals (xG)",
    "Expected Assists (xAG)",
]
TARGET = "Goals"


def main():
    print("=== Model Trainer 시작 ===")
    print("데이터 경로:", DATA_PATH)

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"player_data.csv가 없습니다: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    # 필요한 컬럼 체크
    missing = [c for c in FEATURES + [TARGET] if c not in df.columns]
    if missing:
        raise ValueError(
            f"player_data.csv에 필요한 컬럼이 없습니다: {missing}\n"
            f"현재 컬럼: {list(df.columns)}"
        )

    # 숫자형 변환
    for c in FEATURES + [TARGET]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # NaN 너무 많은 행 제거(최소 안전장치)
    df = df.dropna(subset=[TARGET])
    if len(df) < 200:
        print("경고: 학습 데이터가 너무 적을 수 있어요. (행 수:", len(df), ")")

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 파이프라인: 결측치 채우기 → 스케일링 → 랜덤포레스트 회귀
    model = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("rf", RandomForestRegressor(
                n_estimators=300,
                random_state=42,
                n_jobs=-1
            )),
        ]
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    print(f"✅ 평가 결과: MAE={mae:.3f}, R2={r2:.3f}")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "features": FEATURES,
            "target": TARGET,
        },
        MODEL_PATH,
    )

    print("✅ 모델 저장 완료:", MODEL_PATH)
    print("=== Model Trainer 종료 ===")


if __name__ == "__main__":
    main()
