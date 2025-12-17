import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression # 예시 모델 (회귀)
from sklearn.metrics import mean_squared_error

# 1. 설정
PROCESSED_DATA_DIR = "processed_data"
TEAM_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "team_data.csv")
PLAYER_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "player_data.csv")

MODEL_DIR = "trained_models"
TEAM_MODEL_PATH = os.path.join(MODEL_DIR, "team_prediction_model.pkl")
PLAYER_MODEL_PATH = os.path.join(MODEL_DIR, "player_prediction_model.pkl")

# 훈련된 모델을 저장할 폴더 생성
os.makedirs(MODEL_DIR, exist_ok=True)

def train_team_model(data_path):
    """
    (PDF 개발범위 3) 팀 성적 예측 모델을 훈련하고 저장합니다.
    """
    print(f"\n--- 팀 모델 훈련 시작 ({data_path}) ---")
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"오류: '{data_path}' 파일을 찾을 수 없습니다.")
        print("data_preprocessor.py를 먼저 실행하여 전처리된 데이터를 생성해야 합니다.")
        return

    # (TODO: PDF 개발범위 3)
    # 1. Feature(X)와 Target(y)을 정의해야 합니다.
    
    # (임시 코드: 실행을 위해 가상의 X, y 생성)
    print(" (임시) 가상의 훈련 데이터 생성 중...")
    X = pd.DataFrame(np.random.rand(100, 3), columns=['past_points', 'past_goals', 'past_rank'])
    y = pd.Series(50 + X['past_points']*0.5 + np.random.randn(100))
    
    # 2. 데이터를 훈련용/테스트용으로 분리
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"훈련 데이터: {X_train.shape}, 테스트 데이터: {X_test.shape}")

    # 3. 모델 선택 및 훈련 (PDF 4페이지 - Scikit-learn)
    model = LinearRegression()
    model.fit(X_train, y_train)
    print("모델 훈련 완료.")

    # 4. 모델 성능 평가 (옵션)
    preds = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    print(f"모델 성능 (RMSE): {rmse:.2f}")

    # 5. 훈련된 모델을 파일로 저장 (PDF 5페이지)
    joblib.dump(model, TEAM_MODEL_PATH)
    print(f"성공: 팀 모델을 '{TEAM_MODEL_PATH}'에 저장했습니다.")

def train_player_model(data_path):
    """
    (PDF 개발범위 3) 선수 성적 예측 모델을 훈련하고 저장합니다.
    """
    print(f"\n--- 선수 모델 훈련 시작 ({data_path}) ---")
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"오류: '{data_path}' 파일을 찾을 수 없습니다.")
        return

    # (TODO: PDF 개발범위 3)
    # 1. Feature(X)와 Target(y)을 정의
    
    # (임시 코드: 실행을 위해 가상의 X, y 생성)
    print(" (임시) 가상의 훈련 데이터 생성 중...")
    X = pd.DataFrame(np.random.rand(500, 3), columns=['past_goals', 'past_assists', 'past_min'])
    y = pd.DataFrame({
        'goals': 5 + X['past_goals']*0.8 + np.random.randn(500),
        'assists': 3 + X['past_assists']*0.7 + np.random.randn(500)
    })
    
    # 2. 훈련/테스트 분리
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"훈련 데이터: {X_train.shape}, 테스트 데이터: {X_test.shape}")

    # 3. 모델 선택 및 훈련 
    model_goals = LinearRegression()
    model_goals.fit(X_train, y_train['goals'])
    print("모델 훈련 완료 (Goals).")

    # 4. 모델 저장
    joblib.dump(model_goals, PLAYER_MODEL_PATH)
    print(f"성공: 선수 모델(Goals)을 '{PLAYER_MODEL_PATH}'에 저장했습니다.")

def main():
    print("=== 모델 훈련기 시작 ===")
    
    # 1. 팀 모델 훈련
    train_team_model(TEAM_DATA_PATH)
    
    # 2. 선수 모델 훈련
    train_player_model(PLAYER_DATA_PATH)
    
    print("\n=== 모든 모델 훈련 작업 완료 ===")
    print(f"'{MODEL_DIR}' 폴더에 .pkl 파일이 생성되었는지 확인하세요.")

if __name__ == "__main__":
    main()