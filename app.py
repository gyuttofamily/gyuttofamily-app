import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ぎゅっと家族の記録", layout="centered")

st.title("🍼 手入力で育児を記録するアプリ")

# 日付選択（カレンダーから選べる）
selected_date = st.date_input("📅 記録する日付を選んでください", value=datetime.today())

# 入力欄（手入力）
input_text = st.text_input("📝 今日の気持ちや出来事を入力してください")

# CSVに記録する関数
def save_to_csv(date, text):
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame({"timestamp": [dt], "date": [date.strftime("%Y-%m-%d")], "text": [text]})
    try:
        existing = pd.read_csv("log.csv")
        df = pd.concat([existing, new_data], ignore_index=True)
    except FileNotFoundError:
        df = new_data
    df.to_csv("log.csv", index=False)

# やさしいサポート提案（キーワードベース）
def support_message(text):
    suggestions = []
    if any(word in text for word in ["疲れた", "しんどい", "つらい"]):
        suggestions.append("💡 杉並区には『産後ケア事業』があります。利用登録すれば助産師さんの訪問も受けられます。ぜひ活用しましょう！")
    if any(word in text for word in ["ねむれない", "寝不足"]):
        suggestions.append("🌙 夜間サポートや一時預かりサービスもあります。睡眠時間をしっかり確保しましょう。")
    if any(word in text for word in ["嬉しい", "楽しい", "幸せ"]):
        suggestions.append("😊 その気持ち、大切に！家族で共有してお祝いしても素敵ですね。")
    return suggestions

if input_text:
    st.success(f"記録しました：{selected_date.strftime('%Y-%m-%d')}：{input_text}")
    save_to_csv(selected_date, input_text)

    # サポート提案を表示
    messages = support_message(input_text)
    if messages:
        st.info("🧸 やさしいサポート提案")
        for msg in messages:
            st.markdown(f"- {msg}")
    else:
        st.info("💡 特別なサポート提案はありませんが、記録を続けること自体が素晴らしいことです。")

# 記録履歴表示（カレンダー別に表示）
if st.button("📖 記録履歴を表示する"):
    try:
        df = pd.read_csv("log.csv")
        df = df.sort_values("date", ascending=False)
        st.subheader("📆 日付ごとの記録一覧")
        for d in df["date"].unique():
            st.markdown(f"### {d}")
            for entry in df[df["date"] == d]["text"]:
                st.markdown(f"- {entry}")
    except FileNotFoundError:
        st.info("まだ記録がありません。")
        
# 著作権表記
st.markdown("---")
st.markdown("© 2025 gyuttofamily - このアプリのアイデア・構成は著作権で保護されています。無断転載・商用利用を禁じます。")
