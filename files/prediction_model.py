# prediction_model.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

try:
    import joblib  # pip install joblib
except ImportError:
    joblib = None


@dataclass
class PlayerGoalPredictor:
    """
    Streamlit 앱에서 쓰는 '선수 득점 예측기'
    - model_trainer.py가 학습 후 저장한 pkl을 로드해서 예측
    """
    model_path: str = "models/player_goal_model.pkl"

    def __post_init__(self):
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        p = Path(self.model_path)
        if joblib is None:
            self.model = None
            return
        if p.exists():
            try:
                self.model = joblib.load(p)
            except Exception:
                self.model = None

    def predict_goals(self, input_data: Dict[str, Any]) -> int:
        """
        input_data 예:
        {
          'Minutes': 2000, 'Shots': 50, 'Shots On Target': 20, 'Assists': 5,
          'Passes_Attempted': 1000, 'Passes_Completed': 800, 'xG': 7.5, 'xA': 5.0
        }
        """
        if self.model is None:
            return -1

        try:
            df = pd.DataFrame([input_data])
            pred = float(self.model.predict(df)[0])
            return int(round(pred))
        except Exception:
            return -1


class PredictionModel:
    """
    Flask API(app.py)에서 쓰는 예측용 클래스
    - 지금 app.py가 기대하는 메서드 이름을 그대로 제공
    - (TODO) 팀/선수 예측 모델을 실제로 연결하고 싶으면 이 클래스에서 구현
    """
    def __init__(
        self,
        team_model_path: Optional[str] = None,
        player_model_path: Optional[str] = None,
    ):
        self.team_model = None
        self.player_model = None

        if joblib is not None:
            if team_model_path and Path(team_model_path).exists():
                try:
                    self.team_model = joblib.load(team_model_path)
                except Exception:
                    self.team_model = None

            if player_model_path and Path(player_model_path).exists():
                try:
                    self.player_model = joblib.load(player_model_path)
                except Exception:
                    self.player_model = None

    def predict_team_performance(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        # TODO: 실제 팀 예측 모델을 붙이면 여기서 self.team_model.predict(...)
        return {
            "ok": True,
            "kind": "team",
            "note": "TODO: connect real model",
            "input": features_df.to_dict(orient="records"),
        }

    def predict_player_performance(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        # TODO: 실제 선수 예측 모델을 붙이면 여기서 self.player_model.predict(...)
        return {
            "ok": True,
            "kind": "player",
            "note": "TODO: connect real model",
            "input": features_df.to_dict(orient="records"),
        }
