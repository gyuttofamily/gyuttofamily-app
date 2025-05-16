import streamlit as st
import pandas as pd
from datetime import datetime
from urllib.parse import quote_plus  # ← URLエンコード用

st.set_page_config(page_title="ぎゅっと家族の記録", layout="centered")
st.title("🍼 手入力で育児を記録するアプリ")

# 居住地の入力（セッションステートで保持）
if "region" not in st.session_state:
    st.session_state.region = ""

region = st.text_input("🏠 お住まいの地域（例: 東京都杉並区）を入力してください", value=st.session_state.region)
if region:
    st.session_state.region = region

# 日付選択（カレンダーから選べる）
selected_date = st.date_input("📅 記録する日付を選んでください", value=datetime.today())

# 入力欄（手入力）
input_text = st.text_input("📝 今日の気持ちや出来事を入力してください")

# CSVに記録する関数
def save_to_csv(date, text, region):
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame({
        "timestamp": [dt],
        "date": [date.strftime("%Y-%m-%d")],
        "region": [region],
        "text": [text]
    })
    try:
        existing = pd.read_csv("log.csv")
        df = pd.concat([existing, new_data], ignore_index=True)
    except FileNotFoundError:
        df = new_data
    df.to_csv("log.csv", index=False)

# やさしいサポート提案（地域＋Google検索リンク付き）
def support_message(text, region):
    suggestions = []

    if any(word in text for word in ["疲れた", "しんどい", "つらい"]):
        query = f"{region} 産後ケア"
        encoded_query = quote_plus(query)
        url = f"https://www.google.com/search?q={encoded_query}"
        suggestions.append(f"💡 お住まいの地域にも、産後ケアの支援があります。 [こちらで検索する]({url})")

    if any(word in text for word in ["ねむれない", "寝不足"]):
        query = f"{region} 一時預かり"
        encoded_query = quote_plus(query)
        url = f"https://www.google.com/search?q={encoded_query}"
        suggestions.append(f"🌙 一時預かりや夜間サポートについて、 [こちらで検索してみましょう]({url})")

    if any(word in text for word in ["嬉しい", "楽しい", "幸せ"]):
        suggestions.append("😊 その気持ち、大切に！家族と共有して素敵な思い出にしましょう。")

    return suggestions

# 入力があれば保存＋メッセージ表示
if input_text:
    st.success(f"記録しました：{selected_date.strftime('%Y-%m-%d')}：{input_text}")
    save_to_csv(selected_date, input_text, region)

    # サポート提案を表示
    messages = support_message(input_text, region)
    if messages:
        st.info("🧸 やさしいサポート提案")
        for msg in messages:
            st.markdown(f"- {msg}", unsafe_allow_html=True)
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
            for entry in df[df["date"] == d][["region", "text"]].values:
                st.markdown(f"- ({entry[0]}) {entry[1]}")
    except FileNotFoundError:
        st.info("まだ記録がありません。")
        
# 著作権表記
st.markdown("---")
st.markdown("© 2025 gyuttofamily - このアプリのアイデア・構成は著作権で保護されています。無断転載・商用利用を禁じます。")
