import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ぎゅっと家族の記録", layout="centered")

st.title("🍼 手入力で育児を記録するアプリ")

# 入力欄（手入力）
input_text = st.text_input("📝 今日の気持ちや出来事を入力してください")

# CSV記録用の関数
def save_to_csv(text):
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame({"timestamp": [dt], "text": [text]})
    try:
        existing = pd.read_csv("log.csv")
        df = pd.concat([existing, new_data], ignore_index=True)
    except FileNotFoundError:
        df = new_data
    df.to_csv("log.csv", index=False)

if input_text:
    st.success(f"記録しました：{input_text}")
    save_to_csv(input_text)

# 記録履歴表示
if st.button("📖 記録履歴を表示する"):
    try:
        df = pd.read_csv("log.csv")
        st.dataframe(df)
    except FileNotFoundError:
        st.info("まだ記録がありません。")


# 著作権表記
st.markdown("---")
st.markdown("© 2025 gyuttofamily - このアプリのアイデア・構成は著作権で保護されています。無断転載・商用利用を禁じます。")
