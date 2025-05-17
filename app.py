import streamlit as st
import pandas as pd
from datetime import datetime
from urllib.parse import quote_plus
import os

st.set_page_config(page_title="ぎゅっと家族の記録", layout="centered")
st.title("🍼 手入力で育児を記録するアプリ")

# 初回ユーザー登録情報をCSVとセッションに保存
USER_FILE = "user_info.csv"

def load_user_info():
    if os.path.exists(USER_FILE):
        df = pd.read_csv(USER_FILE)
        if not df.empty:
            return df.iloc[0].to_dict()
    return None

def save_user_info(info):
    df = pd.DataFrame([info])
    df.to_csv(USER_FILE, index=False)

if "user_info" not in st.session_state:
    user_info = load_user_info()
    if user_info:
        st.session_state.user_info = user_info

# 未登録時：ユーザー登録フォーム
if "user_info" not in st.session_state:
    with st.form("user_form"):
        st.subheader("👪 最初にユーザー情報を登録してください")

        region = st.text_input("🏠 居住地（例: 東京都杉並区）")
        age = st.number_input("🎂 あなたの年齢", min_value=15, max_value=100)
        baby_age = st.text_input("🍼 赤ちゃんの年齢（月齢など）", help="例: 6ヶ月、1歳3ヶ月")
        baby_gender = st.radio("👶 赤ちゃんの性別", ["女の子", "男の子", "選ばない"])

        submitted = st.form_submit_button("登録する")
        if submitted and region:
            info = {
                "region": region,
                "age": age,
                "baby_age": baby_age,
                "baby_gender": baby_gender
            }
            st.session_state.user_info = info
            save_user_info(info)
            st.success("登録が完了しました！")
            st.rerun()
    st.stop()

# 登録済み：記録画面表示
region = st.session_state.user_info["region"]
baby_age = st.session_state.user_info["baby_age"]
baby_gender = st.session_state.user_info["baby_gender"]

selected_date = st.date_input("📅 記録する日付を選んでください", value=datetime.today())
input_text = st.text_input("📝 今日の気持ちや出来事を入力してください")

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

def support_message(text, region, baby_age, baby_gender):
    suggestions = []

    if any(word in text for word in ["疲れた", "しんどい", "つらい"]):
        query = f"{region} 産後ケア"
        url = f"https://www.google.com/search?q={quote_plus(query)}"
        suggestions.append(f"💡 お住まいの地域にも産後ケアがあります。 [こちらで検索する]({url})")

    if any(word in text for word in ["ねむれない", "寝不足"]):
        query = f"{region} 一時預かり"
        url = f"https://www.google.com/search?q={quote_plus(query)}"
        suggestions.append(f"🌙 一時預かりや夜間サポートについて [こちらで検索する]({url})")

    if any(word in text for word in ["嬉しい", "楽しい", "幸せ"]):
        suggestions.append("😊 その気持ち、大切に！家族で共有して素敵な思い出にしましょう。")

    # 年齢や性別に応じた提案
    if "夜泣き" in text and "6ヶ月" in baby_age:
        suggestions.append("👶 夜泣きは成長の一部です。お昼に15分でも横になれますように。")

    if baby_gender == "女の子" and "疲れた" in text:
        suggestions.append("🧸 未来の小さなレディも、あなたのやさしさで育っています。")

    return suggestions

if input_text:
    st.success(f"記録しました：{selected_date.strftime('%Y-%m-%d')}：{input_text}")
    save_to_csv(selected_date, input_text, region)

    messages = support_message(input_text, region, baby_age, baby_gender)
    if messages:
        st.info("🧸 やさしいサポート提案")
        for msg in messages:
            st.markdown(f"- {msg}", unsafe_allow_html=True)
    else:
        st.info("💡 特別なサポート提案はありませんが、記録を続けること自体が素晴らしいことです。")

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
