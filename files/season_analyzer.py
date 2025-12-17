import pandas as pd
import numpy as np
from pathlib import Path

# ==================================================
# 이 파일(season_analyzer.py)이 있는 폴더 = files
# ==================================================
BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DATA_DIR = BASE_DIR / "processed_data"

TEAM_DATA_PATH = PROCESSED_DATA_DIR / "team_data.csv"
PLAYER_DATA_PATH = PROCESSED_DATA_DIR / "player_data.csv"


class SeasonAnalyzer:
    """
    전처리된 데이터를 로드하여 팀/선수 성과를 분석하는 클래스 (실데이터 기반)
    - 로드시 컬럼 표준화(Player Name, Club, Shots, xG, xA, Date 등) 수행
    """

    def __init__(self, team_data_path=TEAM_DATA_PATH, player_data_path=PLAYER_DATA_PATH):
        print("SeasonAnalyzer 초기화 중...")

        self.team_data = self._load_csv(team_data_path)
        self.player_data_raw = self._load_csv(player_data_path)
        self.player_data = None

        if self.player_data_raw is None:
            print(f"오류: '{player_data_path}'에서 선수 데이터를 로드하지 못했습니다.")
            return

        self.player_data = self._standardize_player_data(self.player_data_raw)

        if self.player_data is not None and len(self.player_data) > 0:
            print("선수 데이터 로드/표준화 완료. 분석기 준비 완료.")
        else:
            print("오류: 선수 데이터 표준화 후 데이터가 비어있습니다. player_data.csv를 확인하세요.")

    # --------------------------------------------------
    # 내부 유틸: CSV 안전 로드
    # --------------------------------------------------
    def _load_csv(self, path):
        path = Path(path)
        if not path.exists():
            print(f"경고: '{path}' 파일을 찾을 수 없습니다.")
            return None
        try:
            return pd.read_csv(path)
        except Exception as e:
            print(f"'{path}' 로드 중 오류 발생: {e}")
            return None

    # --------------------------------------------------
    # 내부 유틸: 숫자 변환
    # --------------------------------------------------
    def _to_num(self, s, default=0):
        return pd.to_numeric(s, errors="coerce").fillna(default)

    # --------------------------------------------------
    # 핵심: player_data 컬럼 표준화
    # --------------------------------------------------
    def _standardize_player_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df.columns = df.columns.astype(str).str.strip()

        def pick_col(candidates):
            for c in candidates:
                if c in df.columns:
                    return c
            return None

        col_player = pick_col(["Player Name", "Player", "Name"])
        col_club = pick_col(["Club", "Team", "Squad"])
        col_pos = pick_col(["Position", "Pos"])
        col_goals = pick_col(["Goals", "Gls", "Goal"])
        col_assists = pick_col(["Assists", "Ast", "A"])

        col_shots = pick_col(["Shots", "Sh", "Total Shoot", "Total Shots", "Shots Total"])
        col_sot = pick_col(["Shots On Target", "SoT", "SOT", "Shoot on Target", "Shots on Target"])

        col_xg = pick_col(["xG", "Expected Goals (xG)", "Expected Goals"])
        col_xa = pick_col(["xA", "Expected Assists (xA)", "Expected Assists (xAG)", "xAG", "Expected Assists"])

        col_minutes = pick_col(["Minutes", "Mins", "Min"])
        col_date = pick_col(["Date", "Match Date"])

        col_tackles = pick_col(["Tackles"])
        col_blocks = pick_col(["Blocks"])

        df["Player Name"] = df[col_player].astype(str) if col_player else ""
        df["Club"] = df[col_club].astype(str) if col_club else ""
        df["Position"] = df[col_pos].astype(str) if col_pos else ""

        df["Goals"] = self._to_num(df[col_goals]) if col_goals else 0
        df["Assists"] = self._to_num(df[col_assists]) if col_assists else 0

        df["Shots"] = self._to_num(df[col_shots]) if col_shots else 0
        df["Shots On Target"] = self._to_num(df[col_sot]) if col_sot else 0

        df["xG"] = self._to_num(df[col_xg]) if col_xg else 0
        df["xA"] = self._to_num(df[col_xa]) if col_xa else 0

        df["Minutes"] = self._to_num(df[col_minutes]) if col_minutes else 0
        df["Tackles"] = self._to_num(df[col_tackles]) if col_tackles else 0
        df["Blocks"] = self._to_num(df[col_blocks]) if col_blocks else 0

        if col_date:
            df["Date"] = pd.to_datetime(df[col_date], errors="coerce")
        else:
            df["Date"] = pd.NaT

        df["Conversion_Rate"] = np.where(df["Shots"] > 0, (df["Goals"] / df["Shots"]) * 100, 0)
        df["Shots_Accuracy"] = np.where(df["Shots"] > 0, (df["Shots On Target"] / df["Shots"]) * 100, 0)

        minutes_nz = df["Minutes"].replace(0, np.nan)
        df["Goals_per90"] = np.where(df["Minutes"] > 0, (df["Goals"] / minutes_nz) * 90, 0)
        df["Assists_per90"] = np.where(df["Minutes"] > 0, (df["Assists"] / minutes_nz) * 90, 0)

        if df["Date"].notna().any():
            df["Appearances"] = df.groupby(["Player Name", "Club"])["Date"].transform("nunique")
        else:
            df["Appearances"] = df.groupby(["Player Name", "Club"])["Goals"].transform("count")

        df = df.replace([np.inf, -np.inf], np.nan).fillna(0)
        return df

    # ==================================================
    # 공통: 시즌 누적(중복 제거) 집계 테이블 만들기
    # ==================================================
    def _aggregate_season_by_player_club(self) -> pd.DataFrame:
        if self.player_data is None:
            return None

        df = self.player_data.copy()

        agg = (
            df.groupby(["Player Name", "Club"], as_index=False)
              .agg(
                  Position=("Position", lambda x: x.iloc[0] if len(x) else ""),
                  Goals=("Goals", "sum"),
                  Assists=("Assists", "sum"),
                  Shots=("Shots", "sum"),
                  xG=("xG", "sum"),
                  xA=("xA", "sum"),
                  Tackles=("Tackles", "sum"),
                  Blocks=("Blocks", "sum"),
                  Appearances=("Appearances", "max"),
              )
        )

        agg["Conversion_Rate"] = np.where(agg["Shots"] > 0, (agg["Goals"] / agg["Shots"]) * 100, 0)
        agg["OverUnder_xG"] = agg["Goals"] - agg["xG"]

        return agg

    # ==================================================
    # 1) Top Scorers
    # ==================================================
    def get_top_scorers(self, top_n=20):
        if self.player_data is None:
            return {"error": "선수 데이터가 로드되지 않았습니다."}

        try:
            agg = self._aggregate_season_by_player_club()
            if agg is None or agg.empty:
                return {"error": "집계 데이터가 비어있습니다."}

            agg = agg.sort_values("Goals", ascending=False)
            if top_n is not None:
                agg = agg.head(int(top_n))

            cols = ["Player Name", "Club", "Goals", "Appearances"]
            return agg[cols].to_dict("records")

        except Exception as e:
            print(f"Top 득점자 분석 중 오류 발생: {e}")
            return {"error": "Top 득점자 분석 중 오류가 발생했습니다."}

    # ==================================================
    # 2) 슈팅 대비 득점 효율
    # ==================================================
    def get_efficient_finishers(self, min_shots=0, top_n=None):
        if self.player_data is None:
            return {"error": "선수 데이터가 로드되지 않았습니다."}

        try:
            agg = self._aggregate_season_by_player_club()
            if agg is None or agg.empty:
                return {"error": "집계 데이터가 비어있습니다."}

            min_shots = int(min_shots) if min_shots is not None else 0
            agg = agg[agg["Shots"] >= min_shots]

            agg = agg.sort_values("Conversion_Rate", ascending=False)

            if top_n is not None:
                agg = agg.head(int(top_n))

            cols = ["Player Name", "Club", "Shots", "Goals", "Conversion_Rate"]
            return agg[cols].to_dict("records")

        except Exception as e:
            print(f"슈팅 효율 분석 중 오류 발생: {e}")
            return {"error": "슈팅 효율 분석 중 오류가 발생했습니다."}

    # ==================================================
    # 3) 최근 폼 랭킹 (최근 N경기)
    # ==================================================
    def get_recent_form_ranking(self, last_n=5, metric="Goals", top_n=20):
        if self.player_data is None:
            return {"error": "선수 데이터가 로드되지 않았습니다."}

        df = self.player_data.copy()
        has_date = df["Date"].notna().any()

        try:
            rows = []
            for (p, c), g in df.groupby(["Player Name", "Club"]):
                g = g.copy()
                if has_date:
                    g = g.sort_values("Date")
                g_last = g.tail(int(last_n))

                goals = g_last["Goals"].sum()
                assists = g_last["Assists"].sum()
                shots = g_last["Shots"].sum()
                xg = g_last["xG"].sum()
                conv = (goals / shots) * 100 if shots > 0 else 0

                rows.append({
                    "Player Name": p,
                    "Club": c,
                    "Goals": goals,
                    "Assists": assists,
                    "Shots": shots,
                    "xG": xg,
                    "Conversion_Rate": conv,
                    "Matches(Recent)": len(g_last),
                })

            out = pd.DataFrame(rows)
            if out.empty:
                return {"error": "최근 폼 집계 결과가 비어있습니다."}

            if metric not in out.columns:
                metric = "Goals"
            out = out.sort_values(metric, ascending=False)

            if top_n is not None:
                out = out.head(int(top_n))

            return out.to_dict("records")

        except Exception as e:
            print(f"최근 폼 분석 중 오류 발생: {e}")
            return {"error": "최근 폼 분석 중 오류가 발생했습니다."}

    # ==================================================
    # 4) 포지션별 랭킹
    # ==================================================
    def get_position_ranking(self, position_keyword="FW", metric="Goals", top_n=20):
        if self.player_data is None:
            return {"error": "선수 데이터가 로드되지 않았습니다."}

        try:
            agg = self._aggregate_season_by_player_club()
            if agg is None or agg.empty:
                return {"error": "집계 데이터가 비어있습니다."}

            if position_keyword:
                mask = agg["Position"].astype(str).str.upper().str.contains(str(position_keyword).upper(), na=False)
                agg = agg[mask]

            if agg.empty:
                return {"error": f"해당 포지션({position_keyword}) 데이터가 없습니다."}

            if metric not in agg.columns:
                metric = "Goals"

            agg = agg.sort_values(metric, ascending=False)
            if top_n is not None:
                agg = agg.head(int(top_n))

            cols = ["Player Name", "Club", "Position", metric, "Goals", "Assists", "Shots", "xG", "Conversion_Rate"]
            cols = [c for c in cols if c in agg.columns]
            return agg[cols].to_dict("records")

        except Exception as e:
            print(f"포지션 랭킹 분석 중 오류 발생: {e}")
            return {"error": "포지션 랭킹 분석 중 오류가 발생했습니다."}

    # ==================================================
    # 5) xG 오버/언더 퍼포머
    # ==================================================
    def get_xg_over_under(self, top_n=20, mode="over"):
        if self.player_data is None:
            return {"error": "선수 데이터가 로드되지 않았습니다."}

        try:
            agg = self._aggregate_season_by_player_club()
            if agg is None or agg.empty:
                return {"error": "집계 데이터가 비어있습니다."}

            if mode == "under":
                agg = agg.sort_values("OverUnder_xG", ascending=True)
            else:
                agg = agg.sort_values("OverUnder_xG", ascending=False)

            if top_n is not None:
                agg = agg.head(int(top_n))

            cols = ["Player Name", "Club", "Goals", "xG", "OverUnder_xG", "Shots", "Conversion_Rate"]
            return agg[cols].to_dict("records")

        except Exception as e:
            print(f"xG 오버/언더 분석 중 오류 발생: {e}")
            return {"error": "xG 오버/언더 분석 중 오류가 발생했습니다."}

    # ==================================================
    # 6) 팀 의존도 (Top1/Top3 득점 비중)
    # ==================================================
    def get_team_dependency(self, top_n_teams=20, top_n=None):
        if self.player_data is None:
            top_n_teams = top_n
            return {"error": "선수 데이터가 로드되지 않았습니다."}

        try:
            agg = self._aggregate_season_by_player_club()
            if agg is None or agg.empty:
                return {"error": "집계 데이터가 비어있습니다."}

            teams = []
            for club, g in agg.groupby("Club"):
                team_goals = g["Goals"].sum()
                if team_goals <= 0:
                    continue

                g_sorted = g.sort_values("Goals", ascending=False)
                top1 = g_sorted.iloc[0]
                top3 = g_sorted.head(3)

                top1_share = (top1["Goals"] / team_goals) * 100
                top3_share = (top3["Goals"].sum() / team_goals) * 100

                teams.append({
                    "Club": club,
                    "Team_Goals": team_goals,
                    "Top1_Player": top1["Player Name"],
                    "Top1_Goals": top1["Goals"],
                    "Top1_Share(%)": top1_share,
                    "Top3_Share(%)": top3_share,
                })

            out = pd.DataFrame(teams)
            if out.empty:
                return {"error": "팀 의존도 결과가 비어있습니다."}

            out = out.sort_values("Top1_Share(%)", ascending=False)
            if top_n_teams is not None:
                out = out.head(int(top_n_teams))

            return out.to_dict("records")

        except Exception as e:
            print(f"팀 의존도 분석 중 오류 발생: {e}")
            return {"error": "팀 의존도 분석 중 오류가 발생했습니다."}

    # ==================================================
    # 7) 선수 시즌 집계 1행 가져오기 (검색용)
    # ==================================================
    def get_player_season_summary(self, player_name_keyword: str):
        if self.player_data is None:
            return {"error": "선수 데이터가 로드되지 않았습니다."}

        try:
            agg = self._aggregate_season_by_player_club()
            if agg is None or agg.empty:
                return {"error": "집계 데이터가 비어있습니다."}

            mask = agg["Player Name"].astype(str).str.lower().str.contains(str(player_name_keyword).lower(), na=False)
            results = agg[mask].copy()

            if results.empty:
                return {"error": f"'{player_name_keyword}' 선수를 찾을 수 없습니다."}

            results = results.sort_values("Goals", ascending=False)
            return results.iloc[0].to_dict()

        except Exception as e:
            print(f"선수 시즌 요약 검색 중 오류 발생: {e}")
            return {"error": "선수 시즌 요약 검색 중 오류가 발생했습니다."}

    # ==================================================
    # 8) (원본 row 기반) 선수 검색 - 필요 시 유지
    # ==================================================
    def get_player_stats(self, player_name):
        if self.player_data is None:
            return {"error": "선수 데이터가 로드되지 않았습니다."}

        if "Player Name" not in self.player_data.columns:
            return {"error": "player_data.csv에 'Player Name' 컬럼이 없습니다. data_preprocessor.py 결과를 확인하세요."}

        try:
            mask = self.player_data["Player Name"].astype(str).str.lower().str.contains(str(player_name).lower(), na=False)
            results = self.player_data[mask]

            if results.empty:
                return {"error": f"'{player_name}' 선수를 찾을 수 없습니다."}

            return results.iloc[0].to_dict()

        except Exception as e:
            print(f"선수 스탯 검색 중 오류 발생: {e}")
            return {"error": "선수 스탯 검색 중 오류가 발생했습니다."}

    # --------------------------------------------------
    # 팀 분석 (더미)
    # --------------------------------------------------
    def get_team_stats(self, team_name, season="2024-2025"):
        if self.team_data is None:
            return {"error": "팀 데이터가 로드되지 않았습니다."}

        return {"team": team_name, "season": season, "points": 89, "goals_for": 92, "goals_against": 38}

    def get_team_trend(self, team_name, season="2024-2025"):
        if self.team_data is None:
            return {"error": "팀 데이터가 로드되지 않았습니다."}

        return {
            "labels": ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May"],
            "goals_per_month": [5, 7, 3, 6, 8, 5, 7, 4, 6, 3],
            "points_per_month": [9, 7, 6, 7, 9, 6, 7, 6, 9, 3],
        }


if __name__ == "__main__":
    analyzer = SeasonAnalyzer()

    if analyzer.player_data is not None:
        print(pd.DataFrame(analyzer.get_top_scorers(10)).head())
        print(pd.DataFrame(analyzer.get_efficient_finishers(min_shots=0, top_n=10)).head())
        print(pd.DataFrame(analyzer.get_recent_form_ranking(last_n=5, metric="Goals", top_n=10)).head())
        print(pd.DataFrame(analyzer.get_xg_over_under(top_n=10, mode="over")).head())
        print(pd.DataFrame(analyzer.get_team_dependency(top_n_teams=10)).head())
