# streamlit_app.py
import streamlit as st
import pandas as pd
import numpy as np

from season_analyzer import SeasonAnalyzer
from prediction_model import PlayerGoalPredictor

# plotly는 있으면 쓰고, 없으면 앱이 죽지 않게 폴백
try:
    import plotly.graph_objects as go
    PLOTLY_OK = True
except Exception:
    go = None
    PLOTLY_OK = False

st.set_page_config(
    page_title="PL 24/25 Season Analyzer",
    page_icon="⚽",
    layout="wide"
)

# --------------------------------------------------
# 공통: Rank + Top3 메달 + 표 출력
# --------------------------------------------------
def show_rank_table(df: pd.DataFrame, rank_col_name: str = "Rank"):
    df = df.copy().reset_index(drop=True)

    if rank_col_name in df.columns:
        df = df.drop(columns=[rank_col_name])

    df.insert(0, rank_col_name, range(1, len(df) + 1))

    medals = []
    for r in df[rank_col_name].tolist():
        if r == 1:
            medals.append("🥇")
        elif r == 2:
            medals.append("🥈")
        elif r == 3:
            medals.append("🥉")
        else:
            medals.append("")
    df.insert(1, "Medal", medals)

    try:
        st.data_editor(df, use_container_width=True, hide_index=True, disabled=True)
    except TypeError:
        st.dataframe(df, use_container_width=True)

    return df


def safe_df(records):
    if isinstance(records, dict) and "error" in records:
        st.error(records["error"])
        return None
    df = pd.DataFrame(records)
    return df


def pct_fmt(x):
    try:
        if pd.isna(x):
            return "0.00%"
        return f"{float(x):.2f}%"
    except Exception:
        return "0.00%"


def main():
    st.title("⚽ PLAnalyzer — 24/25 Season Analyzer")
    st.caption("데이터 전처리 → 분석 → 예측 파이프라인")

    menu = st.sidebar.selectbox("메뉴 선택", ["📊 시즌 데이터 분석", "🔮 선수 득점 예측(준비중)"])

    # ==================================================
    # 1) 분석
    # ==================================================
    if menu == "📊 시즌 데이터 분석":
        analyzer = SeasonAnalyzer()

        if analyzer.player_data is None:
            st.error("선수 데이터를 로드하지 못했습니다. 먼저 data_preprocessor.py 실행 후 processed_data/player_data.csv를 확인하세요.")
            return

        tabs = st.tabs([
            "🏆 Top 20 득점",
            "🎯 슈팅 대비 득점 효율",
            "🔥 최근 폼(최근 경기)",
            "🧩 포지션별 랭킹",
            "📈 xG 오버/언더",
            "🧱 팀 의존도",
            "⚔️ 선수 비교",
            "🔍 선수 검색",
        ])

        # ------------------------------
        # 1) Top 20 득점 (고정)
        # ------------------------------
        with tabs[0]:
            st.subheader("Top 20 Scorers")

            top_scorers = analyzer.get_top_scorers(top_n=20)
            df = safe_df(top_scorers)
            if df is None or df.empty:
                return

            df_ranked = show_rank_table(df)

            if "Player Name" in df_ranked.columns and "Goals" in df_ranked.columns:
                st.bar_chart(df_ranked.set_index("Player Name")["Goals"])

        # ------------------------------
        # 2) 슈팅 대비 득점 효율 (전체)
        # ------------------------------
        with tabs[1]:
            st.subheader("All Players — Conversion Rate Ranking (전체 표시)")

            eff = analyzer.get_efficient_finishers(min_shots=0, top_n=None)
            df = safe_df(eff)
            if df is None or df.empty:
                return

            if "Conversion_Rate" in df.columns:
                df["Conversion_Rate"] = df["Conversion_Rate"].map(pct_fmt)

            show_rank_table(df)

        # ------------------------------
        # 3) 최근 폼 (최근 5/10경기)
        # ------------------------------
        with tabs[2]:
            st.subheader("Recent Form Ranking (최근 경기)")

            colA, colB = st.columns([1, 2])
            with colA:
                last_n = st.radio("기간 선택", [5, 10], horizontal=True)
            with colB:
                metric = st.selectbox("정렬 기준", ["Goals", "Assists", "xG", "Conversion_Rate"])

            form = analyzer.get_recent_form_ranking(last_n=last_n, metric=metric, top_n=20)
            df = safe_df(form)
            if df is None or df.empty:
                return

            if "Conversion_Rate" in df.columns:
                df["Conversion_Rate"] = df["Conversion_Rate"].map(pct_fmt)

            show_rank_table(df)

        # ------------------------------
        # 4) 포지션별 랭킹 (✅ 기능 복구)
        # ------------------------------
        with tabs[3]:
            st.subheader("Position Ranking (포지션별 랭킹)")

            # 포지션 후보 컬럼 자동 탐색
            df0 = analyzer.player_data.copy()
            pos_col = None
            for c in ["Position", "Pos", "position"]:
                if c in df0.columns:
                    pos_col = c
                    break

            if pos_col is None:
                st.warning("player_data.csv에 Position(포지션) 컬럼이 없어 포지션 랭킹을 만들 수 없습니다.")
                st.info("data_preprocessor에서 Position 컬럼을 유지/표준화했는지 확인해줘.")
            else:
                pos_list = sorted([p for p in df0[pos_col].dropna().astype(str).unique().tolist() if p.strip() != ""])
                if not pos_list:
                    st.warning("포지션 값이 비어있습니다.")
                else:
                    sel_pos = st.selectbox("포지션 선택", pos_list)
                    metric = st.selectbox("정렬 기준", ["Goals", "Assists", "Goals_per90", "xG", "Conversion_Rate"])
                    top_n = st.slider("표시할 선수 수", 5, 50, 20)

                    # 가능한 컬럼만 사용 (없으면 0 처리)
                    use_cols = ["Player Name", "Club", pos_col, "Minutes", "Goals", "Assists", "Goals_per90", "xG", "Shots", "Conversion_Rate"]
                    for c in use_cols:
                        if c not in df0.columns:
                            df0[c] = 0

                    filtered = df0[df0[pos_col].astype(str) == str(sel_pos)].copy()

                    # 같은 선수가 여러 행이면 (날짜/경기 단위) 합산/요약
                    # - Goals/Assists/Shots/xG: sum
                    # - Minutes: sum
                    # - Conversion_Rate: (Goals/Shots)*100 재계산
                    grouped = (
                        filtered.groupby(["Player Name", "Club"], as_index=False)
                        .agg(
                            Minutes=("Minutes", "sum"),
                            Goals=("Goals", "sum"),
                            Assists=("Assists", "sum"),
                            Shots=("Shots", "sum"),
                            xG=("xG", "sum") if "xG" in filtered.columns else ("Goals", "sum"),
                        )
                    )
                    grouped["Goals_per90"] = np.where(grouped["Minutes"] > 0, (grouped["Goals"] / grouped["Minutes"]) * 90, 0)
                    grouped["Conversion_Rate"] = np.where(grouped["Shots"] > 0, (grouped["Goals"] / grouped["Shots"]) * 100, 0)

                    if metric not in grouped.columns:
                        st.warning(f"'{metric}' 컬럼이 없어 Goals로 정렬합니다.")
                        metric = "Goals"

                    grouped = grouped.sort_values(metric, ascending=False).head(top_n)

                    # 보기 좋게 %
                    grouped["Conversion_Rate"] = grouped["Conversion_Rate"].map(pct_fmt)

                    show_rank_table(grouped)

        # ------------------------------
        # 5) xG 오버/언더
        # ------------------------------
        with tabs[4]:
            st.subheader("xG Over/Under (Goals - xG)")

            df = analyzer.get_xg_over_under(top_n=20)
            df = safe_df(df)
            if df is None or df.empty:
                return

            show_rank_table(df)

        # ------------------------------
        # 6) 팀 의존도
        # ------------------------------
        with tabs[5]:
            st.subheader("Team Dependency (팀 의존도)")

            dep = analyzer.get_team_dependency(top_n_teams=20)
            df = safe_df(dep)
            if df is None or df.empty:
                return

            show_rank_table(df)

        # ------------------------------
        # 7) 선수 비교
        # ------------------------------
        with tabs[6]:
            st.subheader("Player Comparison (선수 비교)")

            df0 = analyzer.player_data.copy()

            # 이름 컬럼 후보
            name_col = "Player Name" if "Player Name" in df0.columns else ("Player" if "Player" in df0.columns else None)
            if name_col is None:
                st.error("player_data.csv에 선수 이름 컬럼이 없습니다. ('Player Name' 또는 'Player')")
                return

            all_players = sorted(df0[name_col].dropna().astype(str).unique().tolist())
            colA, colB = st.columns(2)
            with colA:
                a = st.selectbox("선수 A", all_players, index=0)
            with colB:
                b = st.selectbox("선수 B", all_players, index=min(1, len(all_players)-1))

            # 선수별 집계
            def agg_one(player_name: str):
                sub = df0[df0[name_col].astype(str) == str(player_name)].copy()
                for c in ["Minutes", "Goals", "Assists", "Shots", "Shots On Target", "xG", "xA", "Passes Attempted", "Passes Completed"]:
                    if c not in sub.columns:
                        sub[c] = 0

                out = {
                    "Minutes": float(pd.to_numeric(sub["Minutes"], errors="coerce").fillna(0).sum()),
                    "Goals": float(pd.to_numeric(sub["Goals"], errors="coerce").fillna(0).sum()),
                    "Assists": float(pd.to_numeric(sub["Assists"], errors="coerce").fillna(0).sum()),
                    "Shots": float(pd.to_numeric(sub["Shots"], errors="coerce").fillna(0).sum()),
                    "Shots On Target": float(pd.to_numeric(sub["Shots On Target"], errors="coerce").fillna(0).sum()),
                    "xG": float(pd.to_numeric(sub["xG"], errors="coerce").fillna(0).sum()) if "xG" in sub.columns else 0.0,
                    "xA": float(pd.to_numeric(sub["xA"], errors="coerce").fillna(0).sum()) if "xA" in sub.columns else 0.0,
                }
                out["Goals_per90"] = (out["Goals"] / out["Minutes"] * 90) if out["Minutes"] > 0 else 0
                out["Assists_per90"] = (out["Assists"] / out["Minutes"] * 90) if out["Minutes"] > 0 else 0
                out["Conversion_Rate"] = (out["Goals"] / out["Shots"] * 100) if out["Shots"] > 0 else 0
                out["Shots_Accuracy"] = (out["Shots On Target"] / out["Shots"] * 100) if out["Shots"] > 0 else 0
                return out

            a_vals = agg_one(a)
            b_vals = agg_one(b)

            metrics = ["Goals", "Assists", "Goals_per90", "Assists_per90", "Conversion_Rate", "Shots_Accuracy", "xG", "xA"]
            compare_df = pd.DataFrame([
                {"Metric": m, "A": a_vals.get(m, 0), "B": b_vals.get(m, 0)} for m in metrics
            ])

            try:
                st.dataframe(compare_df, use_container_width=True, hide_index=True)
            except TypeError:
                st.dataframe(compare_df, use_container_width=True)

            # 레이더 차트(Plotly 있으면)
            if PLOTLY_OK:
                st.caption("레이더 차트 (Plotly)")
                # 레이더는 스케일이 필요해서 0~1 정규화
                def norm(v, m):
                    mx = max(a_vals.get(m, 0), b_vals.get(m, 0), 1e-9)
                    return v / mx

                a_r = [norm(a_vals.get(m, 0), m) for m in metrics]
                b_r = [norm(b_vals.get(m, 0), m) for m in metrics]

                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=a_r, theta=metrics, fill="toself", name=a))
                fig.add_trace(go.Scatterpolar(r=b_r, theta=metrics, fill="toself", name=b))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=True, height=450)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Plotly가 설치되어 있지 않아 레이더 차트는 표시하지 않습니다. (앱은 정상 동작)")

        # ------------------------------
        # 8) 선수 검색 (✅ 개선 UI 적용)
        # ------------------------------
        with tabs[7]:
            st.subheader("Player Search (선수 검색)")

            q = st.text_input("선수 이름 입력 (부분 검색 가능)")
            if not q:
                st.info("예: Son, Salah, Haaland, Saka ...")
                return

            stats = analyzer.get_player_stats(q)
            if isinstance(stats, dict) and "error" in stats:
                st.warning(stats["error"])
                return

            # 상단 요약
            player_display = stats.get("Player Name", stats.get("Player", ""))
            club_display = stats.get("Club", stats.get("Team", ""))
            st.success(f"검색 결과: {player_display} ({club_display})")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Goals", stats.get("Goals", 0))
            col2.metric("Assists", stats.get("Assists", 0))
            col3.metric("Shots", stats.get("Shots", stats.get("Total Shoot", 0)))
            col4.metric("Matches", stats.get("Appearances", 0))

            # 표로 보기 좋게(섹션)
            def as_table(d: dict):
                items = [{"Stat": k, "Value": d.get(k, "")} for k in d.keys()]
                return pd.DataFrame(items)

            basic = {
                "Player Name": player_display,
                "Club": club_display,
                "Nation": stats.get("Nation", ""),
                "Position": stats.get("Position", ""),
                "Age": stats.get("Age", ""),
                "Minutes": stats.get("Minutes", 0),
                "Appearances": stats.get("Appearances", 0),
            }
            attack = {
                "Goals": stats.get("Goals", 0),
                "Assists": stats.get("Assists", 0),
                "xG": stats.get("xG", stats.get("Expected Goals (xG)", 0)),
                "xA": stats.get("xA", stats.get("Expected Assists (xAG)", 0)),
                "Shots": stats.get("Shots", stats.get("Total Shoot", 0)),
                "Shots On Target": stats.get("Shots On Target", stats.get("Shoot on Target", 0)),
                "Conversion_Rate": pct_fmt(stats.get("Conversion_Rate", 0)),
                "Shots_Accuracy": pct_fmt(stats.get("Shots_Accuracy", 0)),
            }
            passing = {
                "Passes Attempted": stats.get("Passes Attempted", 0),
                "Passes Completed": stats.get("Passes Completed", 0),
                "Pass Completion %": stats.get("Pass Completion %", 0),
                "Progressive Passes": stats.get("Progressive Passes", 0),
            }
            discipline = {
                "Yellow Cards": stats.get("Yellow Cards", 0),
                "Red Cards": stats.get("Red Cards", 0),
                "Fouls": stats.get("Fouls", 0),
            }

            left, right = st.columns(2)
            with left:
                st.markdown("### 📌 기본 정보")
                st.dataframe(as_table(basic), use_container_width=True, hide_index=True)
                st.markdown("### 🧨 공격")
                st.dataframe(as_table(attack), use_container_width=True, hide_index=True)
            with right:
                st.markdown("### 🧠 패스/전개")
                st.dataframe(as_table(passing), use_container_width=True, hide_index=True)
                st.markdown("### 🟥 징계/파울")
                st.dataframe(as_table(discipline), use_container_width=True, hide_index=True)

    # ==================================================
    # 2) 예측
    # ==================================================
    else:
        st.header("🔮 머신러닝 기반 득점 예측")
        st.write("선수의 스탯을 입력하면 **예상 득점 수**를 예측합니다.")

        predictor = PlayerGoalPredictor(model_path="trained_models/player_goal_model.pkl")

        if predictor.model is None:
            st.error("모델이 없습니다. 'model_trainer.py'로 모델을 학습/저장하세요. (files/trained_models/player_goal_model.pkl)")
            return

        with st.form("prediction_form"):
            col1, col2 = st.columns(2)

            with col1:
                minutes = st.number_input("출전 시간 (Minutes)", min_value=0, value=2000)
                shots = st.number_input("총 슈팅 (Shots)", min_value=0, value=50)
                shots_on_target = st.number_input("유효 슈팅 (Shots On Target)", min_value=0, value=20)
                assists = st.number_input("어시스트 (Assists)", min_value=0, value=5)

            with col2:
                passes_att = st.number_input("시도한 패스 (Passes Attempted)", min_value=0, value=1000)
                passes_comp = st.number_input("성공한 패스 (Passes Completed)", min_value=0, value=800)
                xg = st.number_input("기대 득점 (xG)", min_value=0.0, value=7.5, step=0.1)
                xa = st.number_input("기대 어시스트 (xA)", min_value=0.0, value=5.0, step=0.1)

            submitted = st.form_submit_button("예측하기")

            if submitted:
                input_data = {
                    "Minutes": minutes,
                    "Shots": shots,
                    "Shots On Target": shots_on_target,
                    "Assists": assists,
                    "Passes Attempted": passes_att,
                    "Passes Completed": passes_comp,
                    "xG": xg,
                    "xA": xa,
                }

                pred = predictor.predict_goals(input_data)
                if pred != -1:
                    st.balloons()
                    st.success(f"🤖 AI가 예측한 이 선수의 예상 득점은 **{pred} 골** 입니다!")
                else:
                    st.error("예측 중 오류가 발생했습니다. (입력 피처/모델 컬럼 매칭 확인 필요)")


if __name__ == "__main__":
    main()