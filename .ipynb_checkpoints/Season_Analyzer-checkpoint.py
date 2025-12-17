import pandas as pd
import os

# data_preprocessor.py가 데이터를 저장하기로 한 경로
PROCESSED_DATA_DIR = "processed_data"
TEAM_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "team_data.csv")
PLAYER_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "player_data.csv")

class SeasonAnalyzer:
    """
    PDF 7페이지의 클래스 다이어그램에 정의된 SeasonAnalyzer 클래스입니다.
    전처리된 데이터를 로드하여, 팀/선수의 성과를 분석하는 메서드를 제공합니다.
    """
    def __init__(self, team_data_path=TEAM_DATA_PATH, player_data_path=PLAYER_DATA_PATH):
        """
        분석기는 생성될 때 전처리된 데이터를 로드합니다.
        """
        print("SeasonAnalyzer 초기화 중...")
        self.team_data = self.load_data(team_data_path)
        self.player_data = self.load_data(player_data_path)
        
        if self.team_data is None or self.player_data is None:
            print("오류: 분석에 필요한 데이터를 로드하지 못했습니다.")
            print(f"'{PROCESSED_DATA_DIR}' 폴더에 전처리된 CSV 파일이 있는지 확인하세요.")
        else:
            print("데이터 로드 완료. 분석기 준비 완료.")

    def load_data(self, file_path):
        """
        지정된 경로의 CSV 파일을 로드합니다.
        """
        try:
            if not os.path.exists(file_path):
                print(f"경고: '{file_path}' 파일을 찾을 수 없습니다.")
                return None
            return pd.read_csv(file_path)
        except Exception as e:
            print(f"'{file_path}' 로드 중 오류 발생: {e}")
            return None

    def get_team_stats(self, team_name, season="2024-2025"):
        """
        (PDF 개발범위 2) 특정 팀의 24-25 시즌 주요 스탯 계산 로직
        """
        if self.team_data is None:
            return {"error": "팀 데이터가 로드되지 않았습니다."}

        print(f"'{team_name}' (2024-2025 시즌) 스탯 계산 중...")
        
        # TODO: (PDF 개발범위 2)
        # 1. self.team_data에서 'team_name'과 'season'으로 데이터 필터링
        # 2. 주요 스탯 계산 (승점, 득점, 실점, 승/무/패 등)
        
        stats = {
            "team": team_name,
            "season": season,
            "points": 89, # (TODO: 실제 계산 값)
            "goals_for": 92, # (TODO: 실제 계산 값)
            "goals_against": 38 # (TODO: 실제 계산 값)
        }
        
        return stats

    def get_player_stats(self, player_name, season="2024-2025"):
        """
        (PDF 개발범위 2) 특정 선수의 24-25 시즌 주요 스탯 계산 로직
        """
        if self.player_data is None:
            return {"error": "선수 데이터가 로드되지 않았습니다."}
            
        print(f"'{player_name}' (2024-2025 시즌) 스탯 계산 중...")

        # TODO: (PDF 개발범위 2)
        # 1. self.player_data에서 'player_name'과 'season'으로 데이터 필터링
        # 2. 주요 스탯 집계 (골, 어시스트, 출전 시간, 90분당 스탯 등)
        
        stats = {
            "player": player_name,
            "season": season,
            "goals": 16, # (TODO: 실제 계산 값)
            "assists": 9, # (TODO: 실제 계산 값)
            "minutes_played": 2980, # (TODO: 실제 계산 값)
            "goals_per_90": 0.48, # (TODO: 실제 계산 값)
        }
        
        return stats

    def get_team_trend(self, team_name, season="2024-2025"):
        """
        (PDF 개발범위 2) 팀의 시즌 성과 추이 (월별 득점 등) 분석 로직
        """
        if self.team_data is None:
            return {"error": "팀 데이터가 로드되지 않았습니다."}
            
        print(f"'{team_name}' (2024-2025 시즌) 성과 추이 분석 중...")
        
        # TODO: (PDF 개발범위 2)
        # 1. self.team_data에서 'team_name'과 'season'으로 데이터 필터링
        # 2. 날짜(Date)별로 그룹화(groupby)하여 월별 득점, 승점 등 계산
        
        trend_data = {
            "labels": ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May"],
            "goals_per_month": [5, 7, 3, 6, 8, 5, 7, 4, 6, 3], # (TODO: 실제 계산 값)
            "points_per_month": [9, 7, 6, 7, 9, 6, 7, 6, 9, 3] # (TODO: 실제 계산 값)
        }
        
        return trend_data