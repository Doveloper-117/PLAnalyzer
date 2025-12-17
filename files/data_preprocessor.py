import os
print("### RUNNING FILE:", __file__)
print("### CWD:", os.getcwd())

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  # 현재 data_preprocessor.py가 있는 폴더 (files)
PROCESSED_DATA_DIR = BASE_DIR / "processed_data"

FILE_PATHS = {
    "championship_stats": BASE_DIR / "24 25 England Championship Full Data.csv",
    "pl_stats_full": BASE_DIR / "24 25 PL Full Data.csv",
    "pl_player_stats_24_25": BASE_DIR / "PL players stats 24 25.csv",
    "europe_big5_league_players_data": BASE_DIR / "Europe_Big_5_Ligue_players_data_full-2024 25.csv",
}


def load_data(file_paths):
    """
    지정된 경로에서 CSV 파일들을 불러와 DataFrame 딕셔너리로 반환합니다.
    """
    raw_data = {}
    print("데이터 로딩 시작...")

    # 디버그: 현재 기준 폴더와 파일 목록 출력
    print("BASE_DIR =", BASE_DIR)
    try:
        print("BASE_DIR 안 파일들 =", [p.name for p in BASE_DIR.iterdir()])
    except Exception as e:
        print("BASE_DIR 목록 출력 실패:", e)

    for key, path in file_paths.items():
        path = Path(path)

        # 디버그: 존재 여부 출력
        print(f"[CHECK] {key} => {path} | exists? {path.exists()}")

        if not path.exists():
            print(f"경고: '{path}' 파일을 찾을 수 없습니다. 이 파일은 건너뜁니다.")
            continue

        # 원본 CSV 파일 인코딩 문제 대비: utf-8-sig -> cp949 순서로 시도
        try:
            raw_data[key] = pd.read_csv(path, encoding="utf-8-sig")
        except UnicodeDecodeError:
            raw_data[key] = pd.read_csv(path, encoding="cp949")

        print(f"성공: '{path.name}' 로드 완료 (행: {len(raw_data[key])})")

    if not raw_data:
        print("오류: 로드할 수 있는 데이터 파일이 하나도 없습니다. 파일 경로를 확인해주세요.")
        return None

    return raw_data


def preprocess_data(raw_data):
    """
    원본 DataFrame들을 받아 전처리합니다.
    """
    print("데이터 전처리 시작...")
    processed_data = {}

    # 1. 팀 데이터 통합 (EPL + 챔피언십)
    pl_df = raw_data.get("pl_stats_full")
    champ_df = raw_data.get("championship_stats")

    if pl_df is not None and champ_df is not None:
        print(" - PL 및 챔피언십 데이터 통합 중...")
        pl_df = pl_df.copy()
        champ_df = champ_df.copy()

        pl_df["League"] = "PL"
        champ_df["League"] = "Championship"

        try:
            team_data_combined = pd.concat([pl_df, champ_df], ignore_index=True)
            print(" - (TODO) 팀 데이터 Feature 엔지니어링 (승점, 골득실 등)...")
            print(" - (TODO) 팀 데이터 결측치 및 타입 변환 처리...")

            processed_data["team_data_cleaned"] = team_data_combined
            print(" - 팀 데이터 통합 및 전처리 완료.")
        except Exception as e:
            print(f"오류: 팀 데이터 병합 실패: {e}")

    elif pl_df is not None:
        print(" - (경고) 챔피언십 데이터가 없어 EPL 데이터만 전처리합니다.")
        processed_data["team_data_cleaned"] = pl_df.copy()

    # 2. 선수 데이터 전처리 (안 터지는 버전 + 최종 표준 스키마 보장)
    if "pl_player_stats_24_25" in raw_data:
        print(" - 선수 데이터 전처리 중...")
        player_df = raw_data["pl_player_stats_24_25"].copy()

        # 컬럼 이름 공백 제거
        player_df.columns = player_df.columns.str.strip()

        # 컬럼 목록 출력(확인용)
        print("=== 선수 CSV 실제 컬럼 목록 ===")
        print(player_df.columns.tolist())
        print("=============================")

        # ---------- 컬럼 자동 매핑 ----------
        def pick_col(candidates):
            for c in candidates:
                if c in player_df.columns:
                    return c
            return None

        COL_PLAYER  = pick_col(["Player Name", "Player", "Name"])
        COL_CLUB    = pick_col(["Club", "Team", "Squad"])

        COL_MINUTES = pick_col(["Minutes", "Mins", "Min"])
        COL_GOALS   = pick_col(["Goals", "Gls", "Goal"])
        COL_ASSISTS = pick_col(["Assists", "Ast", "A"])

        COL_SHOTS   = pick_col(["Shots", "Sh", "Total Shots", "Shots Total", "Total Shoot"])
        COL_SOT     = pick_col(["Shots On Target", "SoT", "SOT", "Shots on Target", "Shoot on Target"])

        COL_YC      = pick_col(["Yellow Cards", "YC", "Yellows"])
        COL_RC      = pick_col(["Red Cards", "RC", "Reds"])

        COL_APPS    = pick_col(["Appearances", "Apps", "Matches", "MP"])
        COL_FOULS   = pick_col(["Fouls", "Fls", "Foul"])

        # ---------- 표준 컬럼 생성 ----------
        if COL_PLAYER:
            player_df["Player Name"] = player_df[COL_PLAYER].astype(str)
        else:
            player_df["Player Name"] = ""

        if COL_CLUB:
            player_df["Club"] = player_df[COL_CLUB].astype(str)
        else:
            player_df["Club"] = ""

        # 숫자 컬럼 변환 유틸
        def to_num(col, default=0):
            if col is None:
                return pd.Series([default] * len(player_df))
            return pd.to_numeric(player_df[col], errors="coerce").fillna(default)

        player_df["Minutes"] = to_num(COL_MINUTES, 0)
        player_df["Goals"] = to_num(COL_GOALS, 0)
        player_df["Assists"] = to_num(COL_ASSISTS, 0)

        player_df["Shots"] = to_num(COL_SHOTS, 0)
        player_df["Shots On Target"] = to_num(COL_SOT, 0)

        player_df["Yellow Cards"] = to_num(COL_YC, 0)
        player_df["Red Cards"] = to_num(COL_RC, 0)

        player_df["Appearances"] = to_num(COL_APPS, 0)
        player_df["Fouls"] = to_num(COL_FOULS, 0)

        # ---------- 파생 변수 ----------
        print(" - 선수 데이터 Feature 엔지니어링 중...")

        minutes_nonzero = player_df["Minutes"].replace(0, np.nan)
        apps_nonzero = player_df["Appearances"].replace(0, np.nan)

        player_df["Goals_per90"] = (player_df["Goals"] / minutes_nonzero) * 90
        player_df["Assists_per90"] = (player_df["Assists"] / minutes_nonzero) * 90

        player_df["Shots_Accuracy"] = np.where(
            player_df["Shots"] > 0,
            (player_df["Shots On Target"] / player_df["Shots"]) * 100,
            0
        )

        player_df["Conversion_Rate"] = np.where(
            player_df["Shots"] > 0,
            (player_df["Goals"] / player_df["Shots"]) * 100,
            0
        )

        player_df["Total_Cards"] = player_df["Yellow Cards"] + player_df["Red Cards"]

        player_df["Fouls_per_Game"] = np.where(
            player_df["Appearances"] > 0,
            player_df["Fouls"] / apps_nonzero,
            0
        )

        # 팀 내 기여도
        print(" - 선수 데이터 Feature 엔지니어링 중 (팀 내 기여도)...")
        if (player_df["Club"] != "").any():
            club_stats = player_df.groupby("Club")[["Goals", "Assists"]].sum().reset_index()
            club_stats["Team_Total_Contribution"] = club_stats["Goals"] + club_stats["Assists"]

            player_df = player_df.merge(
                club_stats[["Club", "Team_Total_Contribution"]],
                on="Club",
                how="left"
            )
            player_df["Player_Contribution"] = player_df["Goals"] + player_df["Assists"]

            player_df["Goal_Contribution_Pct"] = np.where(
                player_df["Team_Total_Contribution"] > 0,
                (player_df["Player_Contribution"] / player_df["Team_Total_Contribution"]) * 100,
                0
            )
        else:
            player_df["Team_Total_Contribution"] = 0
            player_df["Player_Contribution"] = 0
            player_df["Goal_Contribution_Pct"] = 0

        # NaN/inf 마무리(1차)
        player_df = player_df.replace([np.inf, -np.inf], np.nan).fillna(0)

        # =====================================================
        # ✅ SeasonAnalyzer/Streamlit용 "표준 컬럼" 최종 보장 (필수)
        #  - 너 CSV 실제 컬럼명: Player, Team, Total Shoot, Shoot on Target
        #  - 이미 표준컬럼이 있어도 "비어있으면" 채워줌
        # =====================================================

        # Player Name / Club 보장
        if "Player Name" not in player_df.columns:
            player_df["Player Name"] = ""
        if "Club" not in player_df.columns:
            player_df["Club"] = ""

        if "Player" in player_df.columns:
            player_df.loc[player_df["Player Name"].astype(str).str.len() == 0, "Player Name"] = player_df["Player"].astype(str)

        if "Team" in player_df.columns:
            player_df.loc[player_df["Club"].astype(str).str.len() == 0, "Club"] = player_df["Team"].astype(str)

        # Shots / Shots On Target 보장
        if "Shots" not in player_df.columns:
            player_df["Shots"] = 0
        if "Shots On Target" not in player_df.columns:
            player_df["Shots On Target"] = 0

        if "Total Shoot" in player_df.columns:
            player_df["Shots"] = pd.to_numeric(player_df["Shots"], errors="coerce").fillna(0)
            if (player_df["Shots"] == 0).all():
                player_df["Shots"] = pd.to_numeric(player_df["Total Shoot"], errors="coerce").fillna(0)

        if "Shoot on Target" in player_df.columns:
            player_df["Shots On Target"] = pd.to_numeric(player_df["Shots On Target"], errors="coerce").fillna(0)
            if (player_df["Shots On Target"] == 0).all():
                player_df["Shots On Target"] = pd.to_numeric(player_df["Shoot on Target"], errors="coerce").fillna(0)

        # Appearances 보장 (원본에 없으면 Date로 추정)
        if "Appearances" not in player_df.columns or player_df["Appearances"].isna().all():
            if "Date" in player_df.columns:
                player_df["Appearances"] = player_df.groupby("Player Name")["Date"].transform("nunique")
            else:
                player_df["Appearances"] = 0

        # 숫자형 변환 (최종)
        for c in ["Minutes", "Goals", "Assists", "Shots", "Shots On Target", "Appearances", "Yellow Cards", "Red Cards"]:
            if c in player_df.columns:
                player_df[c] = pd.to_numeric(player_df[c], errors="coerce").fillna(0)
            else:
                player_df[c] = 0

        # per90/효율 파생변수 최종 보장
        minutes_nz = player_df["Minutes"].replace(0, np.nan)
        player_df["Goals_per90"] = np.where(player_df["Minutes"] > 0, (player_df["Goals"] / minutes_nz) * 90, 0)
        player_df["Assists_per90"] = np.where(player_df["Minutes"] > 0, (player_df["Assists"] / minutes_nz) * 90, 0)
        player_df["Conversion_Rate"] = np.where(player_df["Shots"] > 0, (player_df["Goals"] / player_df["Shots"]) * 100, 0)
        player_df["Shots_Accuracy"] = np.where(player_df["Shots"] > 0, (player_df["Shots On Target"] / player_df["Shots"]) * 100, 0)
        player_df["Total_Cards"] = player_df["Yellow Cards"] + player_df["Red Cards"]

        # NaN/inf 정리(최종)
        player_df = player_df.replace([np.inf, -np.inf], np.nan).fillna(0)

        processed_data["player_data_cleaned"] = player_df
        print(" - 선수 데이터 전처리 및 Feature 엔지니어링 완료.")

    print("모든 데이터 전처리 완료.")
    return processed_data


def save_data(processed_data):
    """
    전처리된 DataFrame들을 processed_data 폴더에 저장합니다.
    """
    print("전처리된 데이터 저장 시작...")
    if not processed_data:
        print("경고: 저장할 전처리된 데이터가 없습니다.")
        return

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for key, df in processed_data.items():
        if key.endswith("_cleaned"):
            base_name = key.replace("_cleaned", "")
            save_path = PROCESSED_DATA_DIR / f"{base_name}.csv"
            df.to_csv(save_path, index=False, encoding="utf-8-sig")
            print(f"성공: '{save_path}' 저장 완료")


def main():
    raw_dataframes = load_data(FILE_PATHS)

    if raw_dataframes:
        processed_dataframes = preprocess_data(raw_dataframes)
        save_data(processed_dataframes)
        print("\n=== 데이터 전처리 작업 완료 ===")
    else:
        print("\n=== 데이터 전처리 작업 실패: 데이터를 로드할 수 없습니다. ===")


if __name__ == "__main__":
    main()
