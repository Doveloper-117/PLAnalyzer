import pandas as pd
import numpy as np
import os

# PDF 8페이지에 언급된 데이터 소스를 기반으로 파일 경로를 정의합니다.
# 이 스크립트와 같은 폴더에 CSV 파일들이 있다고 가정합니다.
BASE_DIR = "." 
FILE_PATHS = {
    "epl_stats": os.path.join(BASE_DIR, "24 25 PL Full Data.csv"),
    "championship_stats": os.path.join(BASE_DIR, "24 25 England Championship Full Data.csv"),
    "player_stats_24_25": os.path.join(BASE_DIR, "PL players stats 24 25.csv"),
    "Europe Big 5 League players stats": os.path.join(BASE_DIR, "Europe_Big_5_Ligue_players_data_full-2024 25.csv"),
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
            raw_data[key] = pd.read_csv(path)
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
    
    # 2. 선수 데이터 전처리
    if "player_stats_24_25" in raw_data:
        print(" - 선수 데이터 전처리 중...")
        player_df = raw_data["player_stats_24_25"].copy()
        
        # (TODO 4): (PDF 개발범위 1) 결측치 처리 (예: 'Min' 컬럼)
        print(" - (TODO) 선수 데이터 결측치 처리...")
        
        # (TODO 5): (PDF 개발범위 1) Feature 엔지니어링 (선수)
        print(" - (TODO) 선수 데이터 Feature 엔지니어링 (90분당 스탯)...")
        
        processed_data["player_data_cleaned"] = player_df
        print(" - 선수 데이터 전처리 완료.")

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