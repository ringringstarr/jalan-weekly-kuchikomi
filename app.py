import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ページ設定
st.set_page_config(page_title="じゃらんクチコミ平均点計算", layout="wide")

st.title("じゃらんクチコミ平均点計算")
st.write("CSVをドロップすると、現在と1週間後の平均点（予測）を算出します。")

# CSVアップロード
uploaded_file = st.file_uploader("じゃらんのクチコミCSV（1年分）をドラッグ＆ドロップしてください", type=['csv'])

if uploaded_file is not None:
    try:
        # encoding='cp932' を指定して日本語CSVの文字化け・エラーを防止
        df = pd.read_csv(uploaded_file, skiprows=1, encoding='cp932')
        
        # 投稿日を日付型に変換
        df['投稿日'] = pd.to_datetime(df['投稿日'])
        
        # 実行日と1週間後の日付を取得
        today = datetime.now()
        next_week = today + timedelta(days=7)
        
        # 表の行名となる文字列を生成（例: "3/14時点", "3/21時点"）
        today_str = f"{today.month}/{today.day}時点"
        next_week_str = f"{next_week.month}/{next_week.day}時点"
        
        # 1週間後に「集計対象外」となる境界日（1年前の1週間後）
        cutoff_date = next_week - pd.DateOffset(years=1)
        
        # 1週間後の予測用データ（古い1週間分のクチコミを除外）
        df_next_week = df[df['投稿日'] >= cutoff_date]
        
        # 抽出するカラムと表示名の対応表
        columns_map = {
            '総合評価': '総合',
            '部屋': '部屋',
            '風呂': '風呂',
            '料理朝食': '朝食',
            '料理夕食': '夕食',
            '接客・サービス': '接客ｻｰﾋﾞｽ',
            '清潔感': '清潔感'
        }
        
        current_means = {}
        next_week_means = {}
        
        for orig_col, disp_col in columns_map.items():
            if orig_col in df.columns:
                # ハイフンなどを除外し、数値として扱えるものだけを抽出
                curr_scores = pd.to_numeric(df[orig_col], errors='coerce').dropna()
                next_scores = pd.to_numeric(df_next_week[orig_col], errors='coerce').dropna()
                
                # 平均点を算出し、小数点第2位まで丸める
                current_means[disp_col] = f"{curr_scores.mean():.2f}" if not curr_scores.empty else "0.00"
                next_week_means[disp_col] = f"{next_scores.mean():.2f}" if not next_scores.empty else "0.00"

        # ご要望のレイアウトに合わせてデータフレームを作成（行に日付、列に各項目）
        result_df = pd.DataFrame([current_means, next_week_means], index=[today_str, next_week_str])
        
        st.subheader("算出結果")
        st.info("💡 下の表をマウスで全選択してコピーし、そのままExcelに貼り付けることができます。")
        
        # Excelにコピペしやすい形式（静的HTMLテーブル）で表示
        st.table(result_df)
        
    except Exception as e:
        st.error(f"エラーが発生しました。CSVの形式を確認してください。詳細: {e}")
