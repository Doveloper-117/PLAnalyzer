import pandas as pd
import joblib # Scikit-learn 모델을 불러오기 위해 joblib을 사용합니다.
import os

# 훈련된 모델이 저장될 경로
MODEL_DIR = "trained_models"
TEAM_MODEL_PATH = os.path.join(MODEL_DIR, "team_prediction_model.pkl")
PLAYER_MODEL_PATH = os.path.join(MODEL_DIR, "player_prediction_model.pkl")

class PredictionModel:
    """
    PDF 7페이지의 클래스 다이어그램에 정의된 PredictionModel 클래스입니다.
    미리 훈련된 Scikit-learn 모델을 로드하여, 25-26 시즌 성적을 예측합니다.
    """
    def __init__(self, team_model_path=TEAM_MODEL_PATH, player_model_path=PLAYER_MODEL_PATH):
        """
        예측 모델은 생성될 때 훈련된 .pkl 파일을 로드합니다.
        """
        print("PredictionModel 초기화 중...")
        self.team_model = self.load_model(team_model_path)
        self.player_model = self.load_model(player_model_path)
        
        if self.team_model is None or self.player_model is None:
            print("오류: 예측 모델을 로드하지 못했습니다.")
            print(f"'{MODEL_DIR}' 폴더에 훈련된 .pkl 파일이 있는지 확인하세요.")
        else:
            print("모델 로드 완료. 예측기 준비 완료.")

    def load_model(self, file_path):
        """
        지정된 경로의 .pkl 또는 .joblib 파일을 로드합니다.
        """
        try:
            if not os.path.exists(file_path):
                print(f"경고: '{file_path}' 모델 파일을 찾을 수 없습니다.")
                return None
            
            model = joblib.load(file_path)
            print(f"성공: '{file_path}' 모델 로드 완료")
            return model
        except Exception as e:
            print(f"'{file_path}' 모델 로드 중 오류 발생: {e}")
            return None

    def predict_team_performance(self, features):
        """
        (PDF 개발범위 3) 25-26 시즌 팀 성적(순위, 승점) 예측
        """
        if self.team_model is None:
            return {"error": "팀 예측 모델이 로드되지 않았습니다."}

        print("팀 성적 예측 중...")
        
        # TODO: (PDF 개발범위 3)
        # 1. 'features'는 모델 훈련에 사용된 것과 동일한 형태의 
        #    24-25 시즌 데이터여야 합니다. (예: DataFrame)
        # 2. self.team_model.predict()를 사용하여 예측 수행
        
        # prediction = self.team_model.predict(features)
        
        result = {
            "predicted_points": 75, # (TODO: 실제 예측 값)
            "predicted_rank": 4,     # (TODO: 실제 예측 값)
        }
        
        return result

    def predict_player_performance(self, features):
        """
        (PDF 개발범위 3) 25-26 시즌 선수 성적(골, 어시스트) 예측
        """
        if self.player_model is None:
            return {"error": "선수 예측 모델이 로드되지 않았습니다."}
            
        print("선수 성적 예측 중...")
        
        # TODO: (PDF 개발범위 3)
        # 1. 'features'는 모델 훈련에 사용된 것과 동일한 형태의 
        #    24-25 시즌 선수 데이터여야 합니다.
        # 2. self.player_model.predict()를 사용하여 예측 수행
        
        # prediction = self.player_model.predict(features)
        
        result = {
            "predicted_goals": 14,    # (TODO: 실제 예측 값)
            "predicted_assists": 11,  # (TODO: 실제 예측 값)
        }
        
        return result