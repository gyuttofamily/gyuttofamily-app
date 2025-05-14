import streamlit as st
import speech_recognition as sr
from datetime import datetime
import pandas as pd
import re
import os
import requests

# LINE Notify トークン（必要ならここに貼り付け）
LINE_TOKEN = ""  # ← トークンがあればここに入力

# CSVファイルの保存先
CSV_PATH = "mam_record.csv"

# ユーザーが話した内容から情報を抽出する関数
def extract_info(text):
    milk = re.search(r"(\d+)\s*ml", text)
    sleep = re.search(r"(\d+)(\.|\,)?(\d+)?\s*(時間|じかん|h|hours|hrs)", text)
    mood_keywords = ["疲れ", "つらい", "しんどい", "イライラ", "限界", "やばい"]
    
    milk_ml = int(milk.group(1)) if milk else None
    sleep_hr = float(sleep.group(1) + "." + (sleep.group(3) or "0")) if sleep else None
    needs_support = any(word in text for word in mood_keywords)

    return milk_ml, sleep_hr, text, needs_support

# サポートメッセージ表示
def show_support():
    st.warning("\n杉並区にはこんなサポートがあります。遠慮なく、ぜひ活用しましょう！")
    st.markdown("[杉並区 子育て応援サイト](https://www.city.suginami.tokyo.jp/kosodate/index.html)")

# LINE通知送信
def send_line_notify(message):
    if not LINE_TOKEN:
        return
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"message": message}
    try:
        requests.post(url, headers=headers, data=data)
    except:
        pass

# --- Streamlit UI ---
st.set_page_config(page_title="ママの記録アプリ", layout="centered")

st.title("🍼 話すだけで育児記録 ＆ やさしいサポート")
st.write("ミルク・睡眠・ママの気持ちを、声だけで記録します。疲れが見られたら支援情報も表示されます。")

if st.button("🎙 話す"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("マイクをONにしました。ゆっくり話してください...")
        audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio, language="ja-JP")
            st.success(f"📝 認識結果: {text}")

            milk, sleep, mood, support = extract_info(text)

            # 結果表示
            st.write(f"🍼 ミルク量: {milk if milk else '記録なし'} ml")
            st.write(f"😴 睡眠時間: {sleep if sleep else '記録なし'} 時間")
            st.write(f"💬 ママの気分: {mood}")

            if support:
                show_support()
                send_line_notify("今日はママが少しお疲れかも。そっと声をかけてみてくださいね。")

            # CSVに記録
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = {"日時": timestamp, "発言内容": mood, "ミルク(ml)": milk, "睡眠(h)": sleep, "サポート表示": "あり" if support else "なし"}

            if os.path.exists(CSV_PATH):
                df_existing = pd.read_csv(CSV_PATH)
                df = pd.concat([df_existing, pd.DataFrame([entry])], ignore_index=True)
            else:
                df = pd.DataFrame([entry])

            df.to_csv(CSV_PATH, index=False)
            st.success("📁 記録しました！")

        except sr.UnknownValueError:
            st.error("音声を認識できませんでした。")
        except sr.RequestError:
            st.error("音声認識サービスに接続できませんでした。")

if st.button("📋 記録履歴を見る"):
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        st.subheader("🗂 育児記録一覧")
        st.dataframe(df)
    else:
        st.warning("まだ記録がありません。")
