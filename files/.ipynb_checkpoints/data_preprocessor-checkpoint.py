import pandas as pd
import numpy as np
import os

# PDF 8페이지에 언급된 데이터 소스를 기반으로 파일 경로를 정의합니다.
# 이 스크립트와 같은 폴더에 CSV 파일들이 있다고 가정합니다.
BASE_DIR = "." 
FILE_PATHS = {
    "epl_stats": os.path.join(BASE_DIR, "England Premier League.csv"),
    "championship_stats": os.path.join(BASE_DIR, "England Championship.csv"),
    "player_stats_24_25": os.path.join(BASE_DIR, "epl_player_stats_24_25.csv"),
    # (TODO: PDF 8페이지의 다른 CSV 파일들도 여기에 추가)
}

# 전처리된 데이터를 저장할 폴더 이름
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "processed_data")

def load_data(file_paths):
    """
    지정된 경로에서 CSV 파일들을 불러와 DataFrame 딕셔너리로 반환합니다.
    """
    raw_data = {}
    print("데이터 로딩 시작...")
    try:
        for key, path in file_paths.items():
            if not os.path.exists(path):
                print(f"경고: '{path}' 파일을 찾을 수 없습니다. 이 파일은 건너뜁니다.")
                continue
            # 원본 CSV 파일의 인코딩 문제(예: 엑셀 저장)를 대비해 'utf-8-sig' 또는 'cp949' 시도
            try:
                raw_data[key] = pd.read_csv(path)
            except UnicodeDecodeError:
                raw_data[key] = pd.read_csv(path, encoding='cp949')
                
            print(f"성공: '{path}' 로드 완료 (행: {len(raw_data[key])})")
            
        if not raw_data:
            print("오류: 로드할 수 있는 데이터 파일이 하나도 없습니다. 파일 경로를 확인해주세요.")
            return None
            
        return raw_data
        
    except FileNotFoundError as e:
        print(f"오류: 파일을 찾을 수 없습니다. {e}")
        print("FILE_PATHS 변수의 경로가 올바른지 확인해주세요.")
        return None
    except Exception as e:
        print(f"데이터 로딩 중 예기치 않은 오류 발생: {e}")
        return None

def preprocess_data(raw_data):
    """
    원본 DataFrame들을 받아 PDF 4페이지의 '개발범위'에 맞게 전처리합니다.
    """
    print("데이터 전처리 시작...")
    processed_data = {} # 전처리된 데이터를 저장할 새 딕셔너리

    # 1. 팀 데이터 통합 (EPL + 챔피언십)
    epl_df = raw_data.get("epl_stats")
    champ_df = raw_data.get("championship_stats")

    if epl_df is not None and champ_df is not None:
        print(" - EPL 및 챔피언십 데이터 통합 중...")
        epl_df['League'] = 'EPL'
        champ_df['League'] = 'Championship'
        
        # (TODO 1): 두 DataFrame의 컬럼이 다를 수 있습니다.
        # pd.concat 전에 동일한 컬럼만 선택하거나, 컬럼 이름을 통일해야 합니다.
        try:
            team_data_combined = pd.concat([epl_df, champ_df], ignore_index=True)
            
            # (TODO 2): (PDF 개발범위 1) Feature 엔지니어링 (팀)
            print(" - (TODO) 팀 데이터 Feature 엔지니어링 (승점, 골득실 등)...")

            # (TODO 3): (PDF 개발범위 1) 결측치 처리, 타입 변환
            print(" - (TODO) 팀 데이터 결측치 및 타입 변환 처리...")
            
            processed_data["team_data_cleaned"] = team_data_combined
            print(" - 팀 데이터 통합 및 전처리 완료.")
            
        except pd.errors.InvalidIndexError as e:
            print(f"오류: EPL과 챔피언십 데이터의 컬럼이 일치하지 않아 병합에 실패했습니다. {e}")
            print(" (TODO 1)을 확인하여 컬럼을 통일해주세요.")

    elif epl_df is not None:
        print(" - (경고) 챔피언십 데이터가 없어 EPL 데이터만 전처리합니다.")
        processed_data["team_data_cleaned"] = epl_df.copy() # epl_df만 사용
    
    # 2. 선수 데이터 전처리 (*** 업로드한 노트북의 로직 적용 ***)
    if "player_stats_24_25" in raw_data:
        print(" - 선수 데이터 전처리 중...")
        player_df = raw_data["player_stats_24_25"].copy()
        
        # 컬럼 이름의 앞뒤 공백 제거 (노트북 17번 셀 참고)
        player_df.columns = player_df.columns.str.strip()
        
        # (노트북 5번 셀) 숫자형 컬럼의 결측치(NaN)를 0으로 채우기
        numeric_cols = player_df.select_dtypes(include=np.number).columns
        player_df[numeric_cols] = player_df[numeric_cols].fillna(0)
        
        # (노트북 7, 14, 19번 셀) 파생 변수(Feature) 생성
        print(" - 선수 데이터 Feature 엔지니어링 중 (90분당 스탯 등)...")
        
        # 'Minutes'가 0인 경우 0으로 나누기 오류가 발생하므로, 0인 경우를 np.nan으로 처리
        player_df['Minutes'] = pd.to_numeric(player_df['Minutes'], errors='coerce')
        player_df['Minutes'].replace(0, np.nan, inplace=True) # 0분을 NaN으로 변경
        
        player_df['Goals_per90'] = (player_df['Goals'] / player_df['Minutes']) * 90
        player_df['Assists_per90'] = (player_df['Assists'] / player_df['Minutes']) * 90
        
        # 'Shots'가 0인 경우 0으로 나누기 오류 방지
        player_df['Shot_Accuracy'] = np.where(player_df['Shots'] > 0, (player_df['Shots On Target'] / player_df['Shots']) * 100, 0)
        player_df['Conversion_Rate'] = np.where(player_df['Shots'] > 0, (player_df['Goals'] / player_df['Shots']) * 100, 0)
        
        player_df['Total_Cards'] = player_df['Yellow Cards'] + player_df['Red Cards']
        
        # 'Appearances'가 0인 경우 0으로 나누기 오류 방지
        player_df['Appearances'] = pd.to_numeric(player_df['Appearances'], errors='coerce')
        player_df['Appearances'].replace(0, np.nan, inplace=True) # 0경기를 NaN으로 변경
        
        player_df['Fouls_per_Game'] = player_df['Fouls'] / player_df['Appearances']

        # (노트북 23번 셀) 팀 내 기여도 계산
        print(" - 선수 데이터 Feature 엔지니어링 중 (팀 내 기여도)...")
        club_stats = player_df.groupby('Club')[['Goals', 'Assists']].sum().reset_index()
        club_stats.columns = ['Club', 'Team_Goals', 'Team_Assists']
        club_stats['Team_Total_Contribution'] = club_stats['Team_Goals'] + club_stats['Team_Assists']
        
        player_df = player_df.merge(club_stats[['Club', 'Team_Total_Contribution']], on='Club', how='left')
        player_df['Player_Contribution'] = player_df['Goals'] + player_df['Assists']
        
        # 팀 기여도가 0인 경우 0으로 나누기 오류 방지
        player_df['Goal_Contribution_Pct'] = np.where(player_df['Team_Total_Contribution'] > 0, 
                                                    (player_df['Player_Contribution'] / player_df['Team_Total_Contribution']) * 100, 
                                                    0)
        
        # 다시 NaN 값들을 0으로 채워서 저장 (예: Minutes가 0이었던 선수들)
        player_df.fillna(0, inplace=True)
        
        processed_data["player_data_cleaned"] = player_df
        print(" - 선수 데이터 전처리 및 Feature 엔지니어링 완료.")

    print("모든 데이터 전처리 완료.")
    return processed_data

def save_data(processed_data):
    """
    전처리된 DataFrame들을 'processed_data' 폴더에 저장합니다.
    """
    print("전처리된 데이터 저장 시작...")
    if not processed_data:
        print("경고: 저장할 전처리된 데이터가 없습니다.")
        return

    try:
        os.makedirs(PROCESSED_DATA_DIR, exist_ok=True) # 저장할 폴더 생성
        
        for key, df in processed_data.items():
            if key.endswith("_cleaned"):
                base_name = key.replace("_cleaned", "")
                save_path = os.path.join(PROCESSED_DATA_DIR, f"{base_name}.csv")
                df.to_csv(save_path, index=False, encoding='utf-8-sig')
                print(f"성공: '{save_path}' 저장 완료")
                
    except Exception as e:
        print(f"데이터 저장 중 오류 발생: {e}")

def main():
    """
    메인 실행 함수: 데이터 로드 -> 전처리 -> 저장
    """
    raw_dataframes = load_data(FILE_PATHS)
    
    if raw_dataframes:
        processed_dataframes = preprocess_data(raw_dataframes)
        save_data(processed_dataframes)
        print("\n=== 데이터 전처리 작업 완료 ===")
    else:
        print("\n=== 데이터 전처리 작업 실패: 데이터를 로드할 수 없습니다. ===")

if __name__ == "__main__":
    main()