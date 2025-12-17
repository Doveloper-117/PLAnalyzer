# app.py
from flask import Flask, jsonify
from flask_cors import CORS

from season_analyzer import SeasonAnalyzer
from prediction_model import PredictionModel  # ✅ 이제 실제로 존재함

app = Flask(__name__)
CORS(app)

print("Flask 앱 시작 중... 분석기 및 예측 모델을 로드합니다.")
analyzer = SeasonAnalyzer()
predictor = PredictionModel()
print("분석기 및 예측 모델 로드 완료. API 서버 준비 완료.")

@app.route('/')
def home():
    return "EPL 데이터 분석 API 서버(v2)가 실행 중입니다."

@app.route('/api/stats/team/<team_name>', methods=['GET'])
def get_team_stats(team_name):
    stats = analyzer.get_team_stats(team_name)
    trend = analyzer.get_team_trend(team_name)
    return jsonify({"stats": stats, "trend": trend})

@app.route('/api/stats/player/<player_name>', methods=['GET'])
def get_player_stats(player_name):
    stats = analyzer.get_player_stats(player_name)
    return jsonify(stats)

@app.route('/api/stats/top-scorers', methods=['GET'])
def get_top_scorers():
    top_scorers = analyzer.get_top_scorers(top_n=10)
    return jsonify(top_scorers)

@app.route('/api/stats/efficient-finishers', methods=['GET'])
def get_efficient_finishers():
    efficient_finishers = analyzer.get_efficient_finishers(min_shots=20, top_n=10)
    return jsonify(efficient_finishers)

@app.route('/api/predict/team/<team_name>', methods=['GET'])
def get_team_prediction(team_name):
    import pandas as pd
    features_df = pd.DataFrame([{"past_points": 80, "past_goals": 90}])  # TODO: 실제 피처로 수정
    prediction = predictor.predict_team_performance(features_df)
    return jsonify(prediction)

@app.route('/api/predict/player/<player_name>', methods=['GET'])
def get_player_prediction(player_name):
    import pandas as pd
    features_df = pd.DataFrame([{"past_goals": 15, "past_assists": 8}])  # TODO: 실제 피처로 수정
    prediction = predictor.predict_player_performance(features_df)
    return jsonify(prediction)

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
