from flask import Flask, jsonify
from flask_cors import CORS # 브라우저에서 오는 요청을 허용하기 위해 필요

# 2, 3단계에서 만들었던 .py 파일에서 클래스를 가져옵니다.
from season_analyzer import SeasonAnalyzer
from prediction_model import PredictionModel

# Flask 앱 생성
app = Flask(__name__)
CORS(app) # 모든 도메인에서의 API 요청을 허용합니다 (개발용)

# --- PDF 7페이지 '클래스 다이어그램' ---
# 1. 전역 변수로 분석기 및 예측기 인스턴스 생성
print("Flask 앱 시작 중... 분석기(v2) 및 예측 모델을 로드합니다.")
analyzer = SeasonAnalyzer()
predictor = PredictionModel()
print("분석기 및 예측 모델 로드 완료. API 서버 준비 완료.")
# -------------------------------------

@app.route('/')
def home():
    """
    서버가 살아있는지 확인하는 기본 페이지
    """
    return "EPL 데이터 분석 API 서버(v2)가 실행 중입니다."

# --- API 엔드포인트 (v2: 노트북 로직 반영) ---

@app.route('/api/stats/team/<team_name>', methods=['GET'])
def get_team_stats(team_name):
    """
    (API 엔드포인트 1)
    특정 팀의 24-25 시즌 성과(스탯, 트렌드)를 반환합니다.
    """
    print(f"[API 요청] 팀 스탯: {team_name}")
    stats = analyzer.get_team_stats(team_name)
    trend = analyzer.get_team_trend(team_name)
    response = {"stats": stats, "trend": trend}
    return jsonify(response)

@app.route('/api/stats/player/<player_name>', methods=['GET'])
def get_player_stats(player_name):
    """
    (API 엔드포인트 2 - 수정됨)
    특정 선수의 24-25 시즌 모든 상세 스탯을 반환합니다.
    (1단계에서 계산한 Goals_per90, Goal_Contribution_Pct 등 포함)
    """
    print(f"[API 요청] 선수 상세 스탯: {player_name}")
    stats = analyzer.get_player_stats(player_name)
    return jsonify(stats)

@app.route('/api/stats/top-scorers', methods=['GET'])
def get_top_scorers():
    """
    (API 엔드포인트 3 - 신규)
    24-25 시즌 Top 10 득점자 목록을 반환합니다.
    """
    print(f"[API 요청] Top 10 득점자")
    top_scorers = analyzer.get_top_scorers(top_n=10)
    return jsonify(top_scorers)

@app.route('/api/stats/efficient-finishers', methods=['GET'])
def get_efficient_finishers():
    """
    (API 엔드포인트 4 - 신규)
    슈팅 효율 Top 10 선수 목록 (최소 20회 슈팅)을 반환합니다.
    """
    print(f"[API 요청] 슈팅 효율 Top 10")
    efficient_finishers = analyzer.get_efficient_finishers(min_shots=20, top_n=10)
    return jsonify(efficient_finishers)


# --- 예측 API 엔드포인트 (기존 TODO 유지) ---

@app.route('/api/predict/team/<team_name>', methods=['GET'])
def get_team_prediction(team_name):
    """
    (API 엔드포인트 5)
    특정 팀의 25-26 시즌 성적을 예측합니다.
    """
    print(f"[API 요청] 팀 예측: {team_name}")
    
    # (TODO: 'team_name'을 기반으로 24-25시즌 데이터(Feature)를 가져와야 함)
    import pandas as pd
    features_df = pd.DataFrame([{"past_points": 80, "past_goals": 90}]) # (TODO: 실제 피처로 수정)

    prediction = predictor.predict_team_performance(features_df)
    return jsonify(prediction)


@app.route('/api/predict/player/<player_name>', methods=['GET'])
def get_player_prediction(player_name):
    """
    (API 엔드포인트 6)
    특정 선수의 25-26 시즌 성적을 예측합니다.
    """
    print(f"[API 요청] 선수 예측: {player_name}")
    
    # (TODO: 'player_name'을 기반으로 24-25시즌 데이터(Feature)를 가져와야 함)
    import pandas as pd
    features_df = pd.DataFrame([{"past_goals": 15, "past_assists": 8}]) # (TODO: 실제 피처로 수정)
    
    prediction = predictor.predict_player_performance(features_df)
    return jsonify(prediction)

# --- 서버 실행 ---
if __name__ == '__main__':
    # Flask 서버를 5000번 포트로 실행합니다.
    # (use_reloader=False 추가: 주피터 노트북에서 ZMQError 충돌을 방지합니다)
    app.run(debug=True, port=5000, use_reloader=False)