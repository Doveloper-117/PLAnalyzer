import pandas as pd
import os

# 1단계(data_preprocessor.py)가 데이터를 저장한 경로
PROCESSED_DATA_DIR = "processed_data"
TEAM_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "team_data.csv")
PLAYER_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "player_data.csv")

class SeasonAnalyzer:
    """
    (v2: 노트북 분석 로직 추가)
    전처리된 데이터를 로드하여, 팀/선수의 성과를 분석하는 메서드를 제공합니다.
    """
    def __init__(self, team_data_path=TEAM_DATA_PATH, player_data_path=PLAYER_DATA_PATH):
        """
        분석기는 생성될 때 1단계에서 전처리된 데이터를 로드합니다.
        """
        print("SeasonAnalyzer (v2) 초기화 중...")
        self.team_data = self.load_data(team_data_path)
        self.player_data = self.load_data(player_data_path)
        
        if self.player_data is not None:
            # 1단계에서 생성된 컬럼이 있는지 확인
            if 'Goals_per90' not in self.player_data.columns:
                print("경고: 'Goals_per90' 컬럼이 없습니다. data_preprocessor.py (v2)를 먼저 실행해야 합니다.")
            else:
                print("데이터 로드 완료. 분석기 준비 완료.")
        else:
            print(f"오류: '{PLAYER_DATA_PATH}'에서 선수 데이터를 로드하지 못했습니다.")

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

    # --- 선수 분석 메서드 (노트북 로직 적용) ---

    def get_player_stats(self, player_name, season="2024-2025"):
        """
        (PDF 개발범위 2 - 수정됨)
        특정 선수의 24-25 시즌 모든 상세 스탯을 반환합니다.
        (1단계에서 계산한 Goals_per90, Goal_Contribution_Pct 등 포함)
        """
        if self.player_data is None:
            return {"error": "선수 데이터가 로드되지 않았습니다."}
            
        print(f"'{player_name}' (2024-2025 시즌) 스탯 검색 중...")

        try:
            # 'Player Name' 컬럼에서 정확히 일치하는 선수 검색
            player_stats = self.player_data[self.player_data['Player Name'].str.strip() == player_name.strip()]
            
            if player_stats.empty:
                return {"error": f"'{player_name}' 선수를 찾을 수 없습니다."}

            # DataFrame의 첫 번째 행을 dict(JSON) 형태로 변환하여 반환
            return player_stats.iloc[0].to_dict()
            
        except Exception as e:
            print(f"선수 스탯 검색 중 오류 발생: {e}")
            return {"error": "스탯 검색 중 오류가 발생했습니다."}

    def get_top_scorers(self, top_n=10):
        """
        (신규 - 노트북 6번 셀 로직)
        24-25 시즌 Top N 득점자 목록을 반환합니다.
        """
        if self.player_data is None:
            return {"error": "선수 데이터가 로드되지 않았습니다."}
        
        try:
            # 'Goals' 기준으로 내림차순 정렬
            top_scorers_df = self.player_data.sort_values(by="Goals", ascending=False).head(top_n)
            # API로 보내기 위해 JSON(dict) 리스트 형태로 변환
            return top_scorers_df[['Player Name', 'Club', 'Goals', 'Appearances']].to_dict('records')
        except Exception as e:
            print(f"Top 득점자 분석 중 오류 발생: {e}")
            return {"error": "Top 득점자 분석 중 오류가 발생했습니다."}

    def get_efficient_finishers(self, min_shots=20, top_n=10):
        """
        (신규 - 노트북 15번 셀 로직)
        최소 20회 슈팅 기준, 슈팅 전환율(Conversion_Rate) Top N 선수 목록을 반환합니다.
        """
        if self.player_data is None:
            return {"error": "선수 데이터가 로드되지 않았습니다."}
        
        try:
            # 최소 슈팅 횟수 필터링
            efficient_df = self.player_data[self.player_data['Shots'] >= min_shots]
            # 1단계에서 계산한 'Conversion_Rate' 기준으로 정렬
            efficient_df = efficient_df.sort_values(by='Conversion_Rate', ascending=False).head(top_n)
            
            return efficient_df[['Player Name', 'Club', 'Shots', 'Goals', 'Conversion_Rate']].to_dict('records')
        except Exception as e:
            print(f"슈팅 효율 분석 중 오류 발생: {e}")
            return {"error": "슈팅 효율 분석 중 오류가 발생했습니다."}

    # --- 팀 분석 메서드 (기존 TODO 유지) ---

    def get_team_stats(self, team_name, season="2024-2025"):
        """
        (PDF 개발범위 2 - TODO)
        특정 팀의 24-25 시즌 주요 스탯 계산 로직
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

    def get_team_trend(self, team_name, season="2024-2025"):
        """
        (PDF 개발범위 2 - TODO)
        팀의 시즌 성과 추이 (월별 득점 등) 분석 로직
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

# --- 테스트용 main ---
if __name__ == "__main__":
    # 이 파일을 직접 실행할 경우 (테스트 목적)
    analyzer = SeasonAnalyzer()
    
    if analyzer.player_data is not None:
        print("\n--- get_player_stats 테스트 (Bukayo Saka) ---")
        saka_stats = analyzer.get_player_stats("Bukayo Saka")
        print(saka_stats)
        
        print("\n--- get_top_scorers 테스트 ---")
        top_10_scorers = analyzer.get_top_scorers(top_n=10)
        print(pd.DataFrame(top_10_scorers))
        
        print("\n--- get_efficient_finishers 테스트 (최소 20회 슈팅) ---")
        efficient_10 = analyzer.get_efficient_finishers(min_shots=20, top_n=10)
        print(pd.DataFrame(efficient_10))