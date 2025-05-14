import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ぎゅっと家族の記録", layout="centered")

st.title("🍼 話すだけで育児を記録するアプリ")

# JavaScript + Web Speech API
st.markdown("""
<button onclick="startRecognition()">🎙 話す</button>
<p id="result"></p>

<script>
  var recognition;
  function startRecognition() {
    if (!('webkitSpeechRecognition' in window)) {
      document.getElementById('result').innerHTML = "ブラウザが音声認識に対応していません。";
      return;
    }
    recognition = new webkitSpeechRecognition();
    recognition.lang = "ja-JP";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onresult = function(event) {
      var text = event.results[0][0].transcript;
      document.getElementById("result").innerHTML = "認識結果：" + text;
      window.parent.postMessage({type: 'speech', message: text}, "*");
    };
    recognition.start();
  }

  window.addEventListener("message", (event) => {
    if (event.data.type === "speech") {
      const input = window.parent.document.querySelector("input[type='text']");
      if (input) {
        input.value = event.data.message;
        input.dispatchEvent(new Event("input", { bubbles: true }));
      }
    }
  });
</script>
""", unsafe_allow_html=True)

# 入力欄（音声が自動入力される）
input_text = st.text_input("📝 話した内容：")

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
