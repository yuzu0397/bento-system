import streamlit as st
import psutil
import time
import base64
import requests
from datetime import datetime

# ページ設定
st.set_page_config(page_title="BENTO System v2.0", layout="wide", page_icon="🍱")

# --- 画像をBase64に変換する関数 ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        return ""

win_img_base64 = get_base64_image("Win11.jpg")
android_img_base64 = get_base64_image("Android.jpg")
microsoft_img_base64 = get_base64_image("Microsoft.jpg")
google_img_base64 = get_base64_image("Google.jpg")
apple_img_base64 = get_base64_image("Apple.jpg")
sony_img_base64 = get_base64_image("Sony.jpg")
xperia_img_base64 = get_base64_image("Xperia.jpg")

# --- 天気取得関数（京都市西京極新明町付近の緯度経度） ---
def get_nishikyogoku_weather():
    try:
        # 西京極付近の座標 (緯度: 34.99, 経度: 135.71)
        url = "https://api.open-meteo.com/v1/forecast?latitude=34.99&longitude=135.71&current_weather=true&timezone=Asia%2FTokyo"
        res = requests.get(url, timeout=3).json()
        cw = res.get("current_weather", {})
        temp = cw.get("temperature", "--")
        wcode = cw.get("weathercode", 0)
        
        # WMO天気コードを簡易的に変換
        if wcode == 0: weather_str = "快晴 ☀️"
        elif wcode in [1, 2, 3]: weather_str = "晴れ/曇り ⛅"
        elif wcode in [45, 48]: weather_str = "霧 🌫️"
        elif wcode in [51, 53, 55, 56, 57]: weather_str = "霧雨 🌧️"
        elif wcode in [61, 63, 65, 66, 67]: weather_str = "雨 ☔"
        elif wcode in [71, 73, 75, 77, 85, 86]: weather_str = "雪 ❄️"
        elif wcode in [80, 81, 82]: weather_str = "にわか雨 🌦️"
        elif wcode >= 95: weather_str = "雷雨 ⛈️"
        else: weather_str = "不明"
        
        return f"{weather_str} / {temp}℃"
    except Exception:
        return "取得失敗 ⚠️ (Offline)"

# --- 15秒延長 ＋ Windows風ぐるぐるロード追加の最強演出CSS ---
st.markdown("""
<style>
.stApp {
    background-color: #0d1117;
    color: #ffffff;
}
[data-testid="stSidebar"] {
    background-color: #161b22;
}
h1, h2, h3, h4, h5, h6 {
    color: #79c0ff !important;
    font-weight: 700;
}
p, span, label, div {
    color: #f0f6fc !important;
}

/* --- セレクトボックスの完全ダーク化 --- */
.stSelectbox div[data-baseweb="select"] {
    background-color: #161b22 !important;
    color: #ffffff !important;
    border-color: #30363d !important;
}
.stSelectbox div[data-baseweb="select"] * {
    color: #ffffff !important;
    background-color: #161b22 !important;
}
div[data-baseweb="popover"], div[data-baseweb="menu"], ul[data-baseweb="menu"] {
    background-color: #161b22 !important;
    color: #ffffff !important;
    border: 1px solid #30363d !important;
}
li[data-baseweb="option"] {
    background-color: #161b22 !important;
    color: #ffffff !important;
}
li[data-baseweb="option"]:hover {
    background-color: #30363d !important;
    color: #58a6ff !important;
}
li[data-baseweb="option"][aria-selected="true"] {
    background-color: #1f242c !important;
    color: #58a6ff !important;
}

/* ヘッダー右側用：目立つスペックコンテナ */
.top-popup-container {
    width: 100%;
    background-color: #1f242c;
    border: 2px solid #58a6ff;
    border-top: 6px solid #58a6ff;
    padding: 12px 16px;
    border-radius: 8px;
    box-shadow: 0 6px 20px rgba(88, 166, 255, 0.3);
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.popup-title {
    font-size: 13px;
    font-weight: bold;
    color: #79c0ff;
    border-bottom: 1px solid #30363d;
    padding-bottom: 4px;
    letter-spacing: 0.5px;
}

.popup-grid {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.popup-item {
    font-size: 12px;
    color: #f0f6fc;
    font-weight: bold;
    background-color: #161b22;
    padding: 6px 10px;
    border-radius: 6px;
    border: 1px solid #30363d;
}

.spec-ok {
    color: #3fb950;
    font-weight: bold;
}

.spec-ng {
    color: #ff7b72;
    font-weight: bold;
}

.env-data {
    color: #a5d6ff;
    font-family: monospace;
    font-size: 13px;
}

/* --- 演出コンテナ --- */
.boot-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: linear-gradient(135deg, #050b14 0%, #0d1b2a 50%, #1b1035 100%);
    z-index: 999999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

.boot-container::before {
    content: "";
    position: absolute;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(0,210,255,0.15) 0%, rgba(114,9,183,0.1) 40%, transparent 70%);
    animation: sekaiPulse 3s infinite alternate;
}

@keyframes sekaiPulse {
    0% { transform: scale(0.9); opacity: 0.6; }
    100% { transform: scale(1.1); opacity: 1; }
}

.simultaneous-boot {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 25px;
    z-index: 100000;
}

.boot-row {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    gap: 40px;
}

.boot-item {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.boot-container img {
    width: 290px !important;
    max-width: 21vw !important;
    height: auto !important;
    object-fit: contain;
    opacity: 0;
}

/* ==========================================================
   15秒版：ソロリレー (0秒〜12.5秒) ＋ 最後に全員一斉集合 (12.5秒〜15秒)
   ========================================================== */

.logo-1 { animation: soloThenAll1 15.0s ease forwards; }
.logo-2 { animation: soloThenAll2 15.0s ease forwards; }
.logo-3 { animation: soloThenAll3 15.0s ease forwards; }
.logo-4 { animation: soloThenAll4 15.0s ease forwards; }
.logo-5 { animation: soloThenAll5 15.0s ease forwards; }
.logo-6 { animation: soloThenAll6 15.0s ease forwards; }
.logo-7 { animation: soloThenAll7 15.0s ease forwards; }

@keyframes soloThenAll1 {
    0% { opacity: 0; transform: scale(0.6); filter: drop-shadow(0 0 0px #00d2ff); }
    2% { opacity: 1; transform: scale(1.12); filter: drop-shadow(0 0 30px #00ffff) brightness(1.4); }
    10% { opacity: 1; transform: scale(1); filter: drop-shadow(0 0 15px rgba(0, 210, 255, 0.6)); }
    14% { opacity: 0; transform: scale(0.9); filter: drop-shadow(0 0 0px transparent); }
    83% { opacity: 0; transform: scale(0.5); }
    100% { opacity: 1; transform: scale(1); filter: drop-shadow(0 0 20px #00d2ff); }
}

@keyframes soloThenAll2 {
    0% { opacity: 0; transform: scale(0.6); filter: drop-shadow(0 0 0px #00d2ff); }
    13% { opacity: 0; transform: scale(0.6); }
    15% { opacity: 1; transform: scale(1.12); filter: drop-shadow(0 0 30px #00ffff) brightness(1.4); }
    23% { opacity: 1; transform: scale(1); filter: drop-shadow(0 0 15px rgba(0, 210, 255, 0.6)); }
    27% { opacity: 0; transform: scale(0.9); filter: drop-shadow(0 0 0px transparent); }
    83% { opacity: 0; transform: scale(0.5); }
    100% { opacity: 1; transform: scale(1); filter: drop-shadow(0 0 20px #00d2ff); }
}

@keyframes soloThenAll3 {
    0% { opacity: 0; transform: scale(0.6); filter: drop-shadow(0 0 0px #00d2ff); }
    26% { opacity: 0; transform: scale(0.6); }
    28% { opacity: 1; transform: scale(1.12); filter: drop-shadow(0 0 30px #00ffff) brightness(1.4); }
    36% { opacity: 1; transform: scale(1); filter: drop-shadow(0 0 15px rgba(0, 210, 255, 0.6)); }
    40% { opacity: 0; transform: scale(0.9); filter: drop-shadow(0 0 0px transparent); }
    83% { opacity: 0; transform: scale(0.5); }
    100% { opacity: 1; transform: scale(1); filter: drop-shadow(0 0 20px #00d2ff); }
}

@keyframes soloThenAll4 {
    0% { opacity: 0; transform: scale(0.6); filter: drop-shadow(0 0 0px #00d2ff); }
    39% { opacity: 0; transform: scale(0.6); }
    41% { opacity: 1; transform: scale(1.12); filter: drop-shadow(0 0 30px #00ffff) brightness(1.4); }
    49% { opacity: 1; transform: scale(1); filter: drop-shadow(0 0 15px rgba(0, 210, 255, 0.6)); }
    53% { opacity: 0; transform: scale(0.9); filter: drop-shadow(0 0 0px transparent); }
    83% { opacity: 0; transform: scale(0.5); }
    100% { opacity: 1; transform: scale(1); filter: drop-shadow(0 0 20px #00d2ff); }
}

@keyframes soloThenAll5 {
    0% { opacity: 0; transform: scale(0.6); filter: drop-shadow(0 0 0px #00d2ff); }
    52% { opacity: 0; transform: scale(0.6); }
    54% { opacity: 1; transform: scale(1.12); filter: drop-shadow(0 0 30px #00ffff) brightness(1.4); }
    62% { opacity: 1; transform: scale(1); filter: drop-shadow(0 0 15px rgba(0, 210, 255, 0.6)); }
    66% { opacity: 0; transform: scale(0.9); filter: drop-shadow(0 0 0px transparent); }
    83% { opacity: 0; transform: scale(0.5); }
    100% { opacity: 1; transform: scale(1); filter: drop-shadow(0 0 20px #00d2ff); }
}

@keyframes soloThenAll6 {
    0% { opacity: 0; transform: scale(0.6); filter: drop-shadow(0 0 0px #00d2ff); }
    65% { opacity: 0; transform: scale(0.6); }
    67% { opacity: 1; transform: scale(1.12); filter: drop-shadow(0 0 30px #00ffff) brightness(1.4); }
    75% { opacity: 1; transform: scale(1); filter: drop-shadow(0 0 15px rgba(0, 210, 255, 0.6)); }
    79% { opacity: 0; transform: scale(0.9); filter: drop-shadow(0 0 0px transparent); }
    83% { opacity: 0; transform: scale(0.5); }
    100% { opacity: 1; transform: scale(1); filter: drop-shadow(0 0 20px #00d2ff); }
}

@keyframes soloThenAll7 {
    0% { opacity: 0; transform: scale(0.6); filter: drop-shadow(0 0 0px #00d2ff); }
    78% { opacity: 0; transform: scale(0.6); }
    80% { opacity: 1; transform: scale(1.12); filter: drop-shadow(0 0 30px #00ffff) brightness(1.4); }
    82% { opacity: 1; transform: scale(1); filter: drop-shadow(0 0 15px rgba(0, 210, 255, 0.6)); }
    83% { opacity: 0; transform: scale(0.9); filter: drop-shadow(0 0 0px transparent); }
    83% { opacity: 0; transform: scale(0.5); }
    100% { opacity: 1; transform: scale(1); filter: drop-shadow(0 0 20px #00d2ff); }
}

/* ========================================================== */

/* --- Windows風ぐるぐる回るロードサークル --- */
.win-spinner {
    width: 36px;
    height: 36px;
    border: 3px solid rgba(0, 210, 255, 0.2);
    border-top: 3px solid #00d2ff;
    border-radius: 50%;
    margin-top: 15px;
    animation: winSpin 1s cubic-bezier(0.5, 0.1, 0.5, 0.9) infinite;
    z-index: 100000;
    box-shadow: 0 0 15px rgba(0, 210, 255, 0.4);
}

@keyframes winSpin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.boot-system-text {
    margin-top: 15px;
    font-family: monospace;
    font-size: 13px;
    color: #00d2ff;
    letter-spacing: 4px;
    text-transform: uppercase;
    z-index: 100000;
    text-shadow: 0 0 12px rgba(0, 210, 255, 0.8);
    animation: blinkText 0.8s infinite alternate;
}

@keyframes blinkText {
    0% { opacity: 0.4; }
    100% { opacity: 1; }
}

.boot-progress-bar-container {
    width: 45vw;
    height: 5px;
    background-color: #0d1b2a;
    border: 1px solid #00d2ff;
    border-radius: 3px;
    margin-top: 15px;
    overflow: hidden;
    position: relative;
    z-index: 100000;
    box-shadow: 0 0 20px rgba(0, 210, 255, 0.3);
}

.boot-progress-bar-fill {
    position: absolute;
    height: 100%;
    width: 35%;
    background: linear-gradient(90deg, #7209b7, #00d2ff, #ffffff);
    border-radius: 3px;
    box-shadow: 0 0 15px #00d2ff;
    animation: moveSoloBar 1.2s infinite linear;
}

@keyframes moveSoloBar {
    0% { left: -35%; }
    100% { left: 100%; }
}

.animated-box {
    background-color: #161b22;
    border: 1px solid #30363d;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0,255,204,0.1);
}

/* --- 超カッコいいエラー画面アニメーション --- */
.error-screen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: rgba(13, 17, 23, 0.95);
    backdrop-filter: blur(8px);
    z-index: 9999999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 20px;
    animation: fadeInBg 0.3s cubic-bezier(0, 0, 0.2, 1) forwards;
}

@keyframes fadeInBg {
    0% { opacity: 0; }
    100% { opacity: 1; }
}

.error-box {
    background-color: #161b22;
    border: 2px solid #ff7b72;
    border-top: 10px solid #ff7b72;
    padding: 35px 45px;
    border-radius: 12px;
    box-shadow: 0 0 50px rgba(255, 123, 114, 0.4), 0 10px 30px rgba(0, 0, 0, 0.8);
    max-width: 620px;
    width: 100%;
    text-align: center;
    animation: slamErrorBox 0.4s cubic-bezier(0.2, 1.5, 0.4, 1) forwards;
    transform: scale(0.5);
    opacity: 0;
}

@keyframes slamErrorBox {
    0% { transform: scale(0.5) translateY(-30px); opacity: 0; }
    70% { transform: scale(1.03) translateY(5px); opacity: 1; }
    100% { transform: scale(1) translateY(0); opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

# --- スペック・環境情報の取得と必須比較 ---
MIN_RAM_GB = 4.0
MIN_CPU_CORES = 4
MIN_CPU_FREQ_GHZ = 2.2

try:
    cpu_cores = psutil.cpu_count(logical=False) or psutil.cpu_count(logical=True)
    total_ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 1)
    used_ram_gb = round(psutil.virtual_memory().used / (1024 ** 3), 1)
    cpu_freq = psutil.cpu_freq()
    max_cpu_freq_ghz = round(cpu_freq.max / 1000, 2) if cpu_freq and cpu_freq.max > 0 else 2.5
    cpu_usage = psutil.cpu_percent(interval=None)
except Exception:
    cpu_cores, total_ram_gb, used_ram_gb, max_cpu_freq_ghz, cpu_usage = 4, 4.0, 2.0, 2.2, 15.0

# 差分（マージン/不足分）の計算
ram_diff = round(total_ram_gb - MIN_RAM_GB, 1)
cpu_core_diff = cpu_cores - MIN_CPU_CORES
cpu_freq_diff = round(max_cpu_freq_ghz - MIN_CPU_FREQ_GHZ, 2)

is_ram_ok = total_ram_gb >= MIN_RAM_GB
is_cpu_ok = (cpu_cores >= MIN_CPU_CORES and max_cpu_freq_ghz >= MIN_CPU_FREQ_GHZ)

ram_status_class = "spec-ok" if is_ram_ok else "spec-ng"
ram_diff_str = f"+{ram_diff} GB" if ram_diff >= 0 else f"{ram_diff} GB"

cpu_status_class = "spec-ok" if is_cpu_ok else "spec-ng"
cpu_core_diff_str = f"+{cpu_core_diff}" if cpu_core_diff >= 0 else str(cpu_core_diff)
cpu_freq_diff_str = f"+{cpu_freq_diff}GHz" if cpu_freq_diff >= 0 else f"{cpu_freq_diff}GHz"

# --- スペック不足の場合はここで完全に弾く ---
if not (is_ram_ok and is_cpu_ok):
    st.markdown(f"""
    <div class="error-screen">
        <div class="error-box">
            <h2 style="color: #ff7b72 !important; margin-top: 0; font-size: 22px; letter-spacing: 1px;">⚡ [ SYSTEM ERROR ] Insufficient System Specifications ⚡</h2>
            <p style="font-size: 14px; margin-bottom: 20px;">Your device does not meet the minimum requirements for Bento Management System v2.0.</p>
            <div style="text-align: left; background-color: #0d1117; padding: 15px; border-radius: 6px; border: 1px solid #30363d; margin-bottom: 20px;">
                <b>[Requirement Comparison & Margin]</b><br>
                • RAM: {total_ram_gb} GB (Required: {MIN_RAM_GB}GB) — Diff: <span class="{ram_status_class}">{ram_diff_str}</span><br>
                • CPU Cores: {cpu_cores}C (Required: {MIN_CPU_CORES}C) — Diff: <span class="{cpu_status_class}">{cpu_core_diff_str}</span><br>
                • CPU Clock: {max_cpu_freq_ghz} GHz (Required: {MIN_CPU_FREQ_GHZ}GHz) — Diff: <span class="{cpu_status_class}">{cpu_freq_diff_str}</span>
            </div>
            <p style="color: #8b949e; font-size: 13px;">System startup aborted to protect your environment.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- 状態管理の初期化 ---
if "booted" not in st.session_state:
    st.session_state.booted = False

# --- 起動画面（15秒・ソロリレー ＋ ぐるぐるローディング ＋ 一斉集合） ---
if not st.session_state.booted:
    boot_placeholder = st.empty()
    boot_html = (
        '<div class="boot-container">'
        '<div class="simultaneous-boot">'
        '<div class="boot-row">'
        f'<div class="boot-item"><img class="logo-1" src="data:image/jpeg;base64,{win_img_base64}" /></div>'
        f'<div class="boot-item"><img class="logo-2" src="data:image/jpeg;base64,{android_img_base64}" /></div>'
        f'<div class="boot-item"><img class="logo-3" src="data:image/jpeg;base64,{microsoft_img_base64}" /></div>'
        f'<div class="boot-item"><img class="logo-4" src="data:image/jpeg;base64,{google_img_base64}" /></div>'
        '</div>'
        '<div class="boot-row">'
        f'<div class="boot-item"><img class="logo-5" src="data:image/jpeg;base64,{apple_img_base64}" /></div>'
        f'<div class="boot-item"><img class="logo-6" src="data:image/jpeg;base64,{sony_img_base64}" /></div>'
        f'<div class="boot-item"><img class="logo-7" src="data:image/jpeg;base64,{xperia_img_base64}" /></div>'
        '</div>'
        '</div>'
        '<div class="win-spinner"></div>'
        '<div class="boot-system-text">LOADING SYSTEM COMPONENTS...</div>'
        '<div class="boot-progress-bar-container">'
        '<div class="boot-progress-bar-fill"></div>'
        '</div>'
        '</div>'
    )
    boot_placeholder.markdown(boot_html, unsafe_allow_html=True)
    time.sleep(15.0)
    st.session_state.booted = True
    boot_placeholder.empty()
    st.rerun()

# ==========================================
# 起動完了後のメインコンテンツ
# ==========================================

# リアルタイムの時刻と天気を取得
current_time_str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
weather_info_str = get_nishikyogoku_weather()

# --- ヘッダー部分（左：ロゴ、中央：タイトル、右：スペック＆環境表） ---
col1, col2, col3 = st.columns([1.2, 2.2, 2.5])

with col1:
    st.image("Kawase.jpg", width=200)

with col2:
    st.markdown("<h1 style='margin-top: 10px; font-size: 26px;'>Bento Management System</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size: 15px;'>[SECURE SYSTEM v2.0] — メニュー管理モード</h3>", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="top-popup-container">
        <div class="popup-title">SYSTEM SPEC & ENVIRONMENT DATA</div>
        <div class="popup-grid">
            <div class="popup-item">
                現在時刻: <span class="env-data">{current_time_str}</span>
            </div>
            <div class="popup-item">
                京都市西京極新明町: <span class="env-data" style="color: #ff7b72;">{weather_info_str}</span>
            </div>
            <div class="popup-item">
                RAM: {used_ram_gb} GB / {total_ram_gb} GB 
                <span class="{ram_status_class}">[基準差: {ram_diff_str}]</span>
            </div>
            <div class="popup-item">
                CPU: {cpu_cores}C ({max_cpu_freq_ghz}GHz / {cpu_usage}%) 
                <span class="{cpu_status_class}">[基準差: {cpu_core_diff_str}C / {cpu_freq_diff_str}]</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- メニューデータの定義 ---
bento_data = {
    "周山御膳": [
        "マリネ: 1", "サーモン: 1", "ホタテ: 1", "プチトマト: 1", "オムレツ: 1",
        "有頭エビフライ: 1", "白身フライ: 2", "パスタ: 7g", "ポテトフライ: 3",
        "牛しゃぶ: 60g", "グリル野菜: 1", "ブロッコリー: 2", "鮭フレーク: 1", "豆: 5", "ごはん: 190g"
    ],
    "会席膳 八坂": [
        "ステーキ: 4枚", "グリル野菜: 1", "キャベツ: 1", "ゴマ豆腐: 1", "だし巻き玉子: 2",
        "紅かまぼこ: 3", "海鮮春巻き: 1", "魚: 1", "里芋田楽: 1", "鳥梅ごぼう: 1",
        "なすはさみ揚げ: 1", "枝豆: 2", "天豆玉子: 1", "じゃばら: 2", "カニテリーヌ: 2",
        "華れんこん: 1", "錦糸巻き: 2", "がんも: 1", "彩り豆腐: 1", "たけのこ: 1",
        "南京かぼちゃ: 1", "ふき: 1", "紅葉麩: 1", "えびうま煮: 1", "茶碗蒸し: 1",
        "お吸い物: 1", "漬物: 1", "えび (26-30): 1", "なす: 1", "れんこん: 1",
        "オクラ: 1", "華イカ: 1", "大根けん: 1", "大葉: 1", "マグロ: 3",
        "鯛: 2", "イカ: 2", "ご飯: 180g", "ちりめん: 1"
    ],
    "国産牛すきやきと国産牛ステーキ御膳": [
        "がんも: 1", "彩り豆腐: 1", "南京: 1", "竹の子: 1", "ふき: 1",
        "もみじ麩: 1", "ステーキ: 4", "グリル野菜: 1", "だし巻き玉子: 1", "魚: 1",
        "枝豆: 2", "さつまいも: 1", "カニテリーヌ: 1", "酢の物: 1", "牛すき焼き: 50g",
        "豆: 5", "ごはん: 150g"
    ],
    "ボリューム唐揚げハンバーグ弁当": [
        "ハンバーグ: 1個", "ウインナー: 2本", "プチトマト: 1個", "きゅうり: 2枚", "ポテトサラダ: 1個",
        "唐揚げ: 3個", "だし巻き卵: 1個", "さつまいも: 1個", "ナポリタン: 9g", "ごはん: 190g"
    ]
}

st.markdown("### Select Bento Menu")
selected_bento = st.selectbox("お弁当を選んでください", list(bento_data.keys()))

st.markdown(f"""
<div class="animated-box">
    <h3 style="color: #58a6ff; margin-top: 0;">【 {selected_bento} 】構成材料一覧</h3>
    <hr style="border-color: #30363d;">
    <ul style="list-style-type: none; padding-left: 0;">
""", unsafe_allow_html=True)

for item in bento_data[selected_bento]:
    st.markdown(f"<li style='padding: 4px 0; border-bottom: 1px solid #21262d;'>• {item}</li>", unsafe_allow_html=True)

st.markdown("</ul></div>", unsafe_allow_html=True)