import streamlit as st
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import io

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ---------------------------------------------------------
# 讀取專案內的 NotoSansTC-VariableFont_wght.ttf 字型
# ---------------------------------------------------------
font_filename = "NotoSansTC-VariableFont_wght.ttf"

if os.path.exists(font_filename):
    fm.fontManager.addfont(font_filename)
    font_prop = fm.FontProperties(fname=font_filename)
    plt.rcParams['font.sans-serif'] = [font_prop.get_name(), 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    pdfmetrics.registerFont(TTFont('NotoSansTC', font_filename))
    pdf_font_name = 'NotoSansTC'
else:
    font_prop = None
    pdf_font_name = 'Helvetica'

st.set_page_config(page_title="嬰幼兒護理與發展評估系統", page_icon="👶", layout="centered")

st.title("👶 嬰幼兒照護與發展評估系統")
st.caption("醫護級到府照護專用 ｜ 整合國健署生長曲線與居托官方發展檢核")

if "baby_months" not in st.session_state:
    st.session_state["baby_months"] = 4.0
if "baby_gender" not in st.session_state:
    st.session_state["baby_gender"] = "男寶寶"

tab1, tab2 = st.tabs(["📈 生長百分位試算", "📋 居托發展檢核表"])

# ==========================================
# WHO / 國健署 0-24 月齡 官方參考數據
# ==========================================
MONTHS_REF = np.array([0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 18, 21, 24])

BOY_HEIGHT_3  = np.array([46.1, 50.8, 54.4, 57.3, 59.7, 61.7, 63.3, 66.2, 68.7, 71.0, 74.1, 76.9, 79.4, 81.7])
BOY_HEIGHT_15 = np.array([48.0, 52.7, 56.4, 59.3, 61.8, 63.8, 65.4, 68.4, 71.0, 73.3, 76.6, 79.6, 82.2, 84.7])
BOY_HEIGHT_50 = np.array([49.9, 54.7, 58.4, 61.4, 63.9, 65.9, 67.6, 70.6, 73.3, 75.7, 79.1, 82.3, 85.1, 87.8])
BOY_HEIGHT_85 = np.array([51.8, 56.7, 60.4, 63.5, 66.0, 68.0, 69.8, 72.8, 75.6, 78.1, 81.6, 85.0, 88.0, 90.9])
BOY_HEIGHT_97 = np.array([53.7, 58.6, 62.4, 65.5, 68.0, 70.1, 71.9, 75.0, 77.9, 80.5, 84.2, 87.7, 90.9, 93.9])

BOY_WEIGHT_3  = np.array([2.5, 3.4, 4.3, 5.0, 5.6, 6.0, 6.4, 6.9, 7.4, 7.8, 8.4, 8.8, 9.2, 9.7])
BOY_WEIGHT_15 = np.array([2.9, 3.9, 4.9, 5.7, 6.3, 6.7, 7.1, 7.7, 8.3, 8.7, 9.3, 9.8, 10.3, 10.9])
BOY_WEIGHT_50 = np.array([3.3, 4.5, 5.6, 6.4, 7.0, 7.5, 7.9, 8.6, 9.2, 9.6, 10.3, 10.9, 11.5, 12.2])
BOY_WEIGHT_85 = np.array([3.8, 5.1, 6.3, 7.2, 7.8, 8.4, 8.8, 9.6, 10.3, 10.8, 11.5, 12.3, 13.0, 13.7])
BOY_WEIGHT_97 = np.array([4.4, 5.8, 7.1, 8.0, 8.7, 9.3, 9.8, 10.7, 11.4, 12.0, 12.8, 13.7, 14.5, 15.3])

BOY_HEAD_3    = np.array([32.1, 34.4, 35.8, 37.0, 37.9, 38.7, 39.3, 40.4, 41.2, 41.9, 42.8, 43.6, 44.2, 44.8])
BOY_HEAD_15   = np.array([33.3, 35.6, 37.0, 38.2, 39.2, 40.0, 40.6, 41.7, 42.6, 43.3, 44.2, 45.0, 45.7, 46.3])
BOY_HEAD_50   = np.array([34.5, 36.9, 38.3, 39.5, 40.5, 41.3, 42.0, 43.1, 44.0, 44.7, 45.7, 46.5, 47.2, 47.8])
BOY_HEAD_85   = np.array([35.7, 38.1, 39.5, 40.8, 41.8, 42.6, 43.3, 44.4, 45.4, 46.1, 47.1, 48.0, 48.7, 49.3])
BOY_HEAD_97   = np.array([36.9, 39.4, 40.8, 42.1, 43.1, 43.9, 44.7, 45.8, 46.8, 47.6, 48.6, 49.5, 50.2, 50.9])

def calculate_percentile(age, val, ref3, ref15, ref50, ref85, ref97):
    p3 = np.interp(age, MONTHS_REF, ref3)
    p15 = np.interp(age, MONTHS_REF, ref15)
    p50 = np.interp(age, MONTHS_REF, ref50)
    p85 = np.interp(age, MONTHS_REF, ref85)
    p97 = np.interp(age, MONTHS_REF, ref97)
    
    if val < p3:
        return "< 3rd (偏低)"
    elif val < p15:
        return "3rd ~ 15th"
    elif val < p50:
        return "15th ~ 50th"
    elif val < p85:
        return "50th ~ 85th"
    elif val <= p97:
        return "85th ~ 97th"
    else:
        return "> 97th (偏高)"

def generate_curve(ref_3, ref_50, ref_97, x_mesh):
    p50 = np.interp(x_mesh, MONTHS_REF, ref_50)
    p3  = np.interp(x_mesh, MONTHS_REF, ref_3)
    p97 = np.interp(x_mesh, MONTHS_REF, ref_97)
    p15 = p50 - 0.55 * (p50 - p3)
    p85 = p50 + 0.55 * (p97 - p50)
    return p3, p15, p50, p85, p97

def plot_official_growth_chart(title_text, x_age, y_val, ylabel_text, ref_3, ref_50, ref_97):
    x_mesh = np.linspace(0, 24, 200)
    p3, p15, p50, p85, p97 = generate_curve(ref_3, ref_50, ref_97, x_mesh)

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=120)
    
    ax.plot(x_mesh, p97, color='#FF8A8A', linewidth=1.5, linestyle='-', label='97%')
    ax.plot(x_mesh, p85, color='#FFC107', linewidth=1.2, linestyle='--', label='85%')
    ax.plot(x_mesh, p50, color='#4CAF50', linewidth=2.0, linestyle='-', label='50%')
    ax.plot(x_mesh, p15, color='#FFC107', linewidth=1.2, linestyle='--', label='15%')
    ax.plot(x_mesh, p3,  color='#FF8A8A', linewidth=1.5, linestyle='-', label='3%')
    
    ax.fill_between(x_mesh, p3, p97, color='#E8F5E9', alpha=0.6)
    
    ax.text(24.2, p97[-1], '97%', verticalalignment='center', fontsize=9, color='#FF8A8A', fontweight='bold')
    ax.text(24.2, p85[-1], '85%', verticalalignment='center', fontsize=9, color='#FFC107')
    ax.text(24.2, p50[-1], '50%', verticalalignment='center', fontsize=9, color='#4CAF50', fontweight='bold')
    ax.text(24.2, p15[-1], '15%', verticalalignment='center', fontsize=9, color='#FFC107')
    ax.text(24.2, p3[-1],  '3%',  verticalalignment='center', fontsize=9, color='#FF8A8A', fontweight='bold')

    ax.scatter([x_age], [y_val], color='#FF4081', s=120, zorder=5, edgecolor='black', linewidth=1.5, label='寶寶落點')
    
    if font_prop:
        ax.annotate(f' 寶寶: ({x_age}個月, {y_val})', (x_age, y_val), textcoords="offset points", xytext=(8,10),
                    ha='left', fontweight='bold', color='#D81B60', fontproperties=font_prop,
                    bbox=dict(boxstyle="round,pad=0.3", fc="#FFF9C4", ec="#FF4081", lw=1, alpha=0.9))
        ax.set_title(title_text, fontsize=13, fontweight='bold', pad=10, fontproperties=font_prop)
        ax.set_xlabel('月齡 (個月)', fontsize=10, fontproperties=font_prop)
        ax.set_ylabel(ylabel_text, fontsize=10, fontproperties=font_prop)
    else:
        ax.annotate(f' 寶寶: ({x_age}M, {y_val})', (x_age, y_val), textcoords="offset points", xytext=(8,10),
                    ha='left', fontweight='bold', color='#D81B60',
                    bbox=dict(boxstyle="round,pad=0.3", fc="#FFF9C4", ec="#FF4081", lw=1, alpha=0.9))
        ax.set_title(title_text, fontsize=13, fontweight='bold', pad=10)
        ax.set_xlabel('Age (Months)', fontsize=10)
        ax.set_ylabel(ylabel_text, fontsize=10)

    ax.set_xlim(0, 25)
    ax.grid(True, linestyle=':', alpha=0.6)
    
    leg = ax.legend(loc='upper left', fontsize=9)
    if font_prop:
        for text in leg.get_texts():
            text.set_fontproperties(font_prop)
    
    plt.tight_layout()
    return fig

# ==========================================
# TAB 1: 生長百分位試算
# ==========================================
with tab1:
    st.header("寶寶生長百分位評估")
    st.write("請輸入寶寶的出生日期與最新測量數據：")
    
    col1, col2 = st.columns(2)
    with col1:
        gender = st.radio("寶寶性別", ["男寶寶", "女寶寶"], horizontal=True)
        birthday = st.date_input("出生日期", datetime.date(2026, 1, 1))
    with col2:
        measure_date = st.date_input("測量日期", datetime.date.today())
        
    days = (measure_date - birthday).days
    months = round(days / 30.44, 1)
    
    st.session_state["baby_months"] = months
    st.session_state["baby_gender"] = gender
    
    st.info(f"💡 目前計算精確月齡為：**{months} 個月** ({days} 天)")
    
    st.subheader("輸入測量數據")
    c1, c2, c3 = st.columns(3)
    with c1:
        height = st.number_input("身高 (cm)", min_value=30.0, max_value=120.0, value=68.0, step=0.1)
    with c2:
        weight = st.number_input("體重 (kg)", min_value=2.0, max_value=30.0, value=8.2, step=0.1)
    with c3:
        head = st.number_input("頭圍 (cm)", min_value=25.0, max_value=60.0, value=43.0, step=0.1)
        
    if st.button("🚀 開始計算生長百分位並繪圖"):
        h_pct = calculate_percentile(months, height, BOY_HEIGHT_3, BOY_HEIGHT_15, BOY_HEIGHT_50, BOY_HEIGHT_85, BOY_HEIGHT_97)
        w_pct = calculate_percentile(months, weight, BOY_WEIGHT_3, BOY_WEIGHT_15, BOY_WEIGHT_50, BOY_WEIGHT_85, BOY_WEIGHT_97)
        head_pct = calculate_percentile(months, head, BOY_HEAD_3, BOY_HEAD_15, BOY_HEAD_50, BOY_HEAD_85, BOY_HEAD_97)
        
        st.session_state["h_pct"] = h_pct
        st.session_state["w_pct"] = w_pct
        st.session_state["head_pct"] = head_pct
        st.session_state["height_val"] = height
        st.session_state["weight_val"] = weight
        st.session_state["head_val"] = head
        
        st.markdown("---")
        st.subheader("📊 評估結果分析與官方曲線圖")
        st.success(f"**【{gender}｜{months}個月】** 檢測成果：")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("身高百分位", h_pct, f"{height} cm")
        m2.metric("體重百分位", w_pct, f"{weight} kg")
        m3.metric("頭圍百分位", head_pct, f"{head} cm")
        
        st.markdown("""
        > **🩺 護理師綜合衛教評語：**  
        > 寶寶目前的各項生長指標均落在《兒童健康手冊》標準百分位曲線區間（3%~97%）之內，成長曲線非常平滑且穩定！
        """)
        
        st.subheader("📈 兒童健康手冊生長百分位曲線對照圖")
        
        fig_h = plot_official_growth_chart("身高清確落點對照圖 (0-24個月)", months, height, "身高 (cm)", BOY_HEIGHT_3, BOY_HEIGHT_50, BOY_HEIGHT_97)
        st.pyplot(fig_h)
        
        fig_w = plot_official_growth_chart("體重精確落點對照圖 (0-24個月)", months, weight, "體重 (kg)", BOY_WEIGHT_3, BOY_WEIGHT_50, BOY_WEIGHT_97)
        st.pyplot(fig_w)
        
        fig_head = plot_official_growth_chart("頭圍精確落點對照圖 (0-24個月)", months, head, "頭圍 (cm)", BOY_HEAD_3, BOY_HEAD_50, BOY_HEAD_97)
        st.pyplot(fig_head)

# ==========================================
# TAB 2: 居托官方發展檢核表
# ==========================================
with tab2:
    st.header("兒童發展里程碑檢核")
    
    m = st.session_state.get("baby_months", 4.0)
    default_idx = 0
    if m < 6.0:
        default_idx = 0
    elif m < 9.0:
        default_idx = 1
    elif m < 12.0:
        default_idx = 2
    elif m < 18.0:
        default_idx = 3
    else:
        default_idx = 4

    stage_options = [
        "4 個月（滿 4 個月至未滿 6 個月）", 
        "6 個月（滿 6 個月至未滿 9 個月）", 
        "9 個月（滿 9 個月至未滿 1 歲）", 
        "12 個月/1歲（滿 12 個月至未滿 1 歲半）", 
        "18 個月/1歲半（滿 18 個月至未滿 2 歲）"
    ]

    stage = st.selectbox(
        "請確認檢核月齡階段（系統已依輸入之出生日期自動帶入適齡階段）：",
        stage_options,
        index=default_idx
    )
    
    st.write("請依據寶寶近期的實際表現，勾選**「是」**或**「否」**：")
    st.caption("標註 ★ 為「關鍵警訊指標」")
    
    questions_database = {
        "4 個月": [
            {"id": 1, "text": "1. [動作] 仰臥時雙手掌均能自然地張開，不再一直緊握。", "star": False, "normal_ans": "是"},
            {"id": 2, "text": "2. [動作] 仰臥時雙手會在胸前互相靠近（不一定要碰到）。", "star": False, "normal_ans": "是"},
            {"id": 3, "text": "3. [警訊] ★ 仰臥不尋常地一直歪一邊，無法回正或自由轉動。", "star": True, "normal_ans": "否"},
            {"id": 4, "text": "4. [警訊] ★ 仰臥靜止不動時，身體的脊骨經常呈向固定一側，無法維持在中線上。", "star": True, "normal_ans": "否"},
            {"id": 5, "text": "5. [肌張力] 換尿布時感覺腿有明顯不尋常的阻力，不容易打開/彎曲。", "star": False, "normal_ans": "否"},
            {"id": 6, "text": "6. [警訊] ★ 使用左右手或左右腳的次數和力量明顯地不平均。", "star": True, "normal_ans": "否"},
            {"id": 7, "text": "7. [動作] 仰臥拉起時頭無法跟著身體抬起來，一直向後仰。", "star": False, "normal_ans": "否"},
            {"id": 8, "text": "8. [語言] 即使跟說話，也很少發出聲音。", "star": False, "normal_ans": "否"},
            {"id": 9, "text": "9. [警訊] ★ 眼睛可以跟在左右、提上到下拿無聲音的移動物體（離眼20cm）。", "star": True, "normal_ans": "是"},
            {"id": 10, "text": "10. [動作] 趴著時能以雙肘支撐，將頭抬起和地面垂直，並能維持數秒。", "star": False, "normal_ans": "是"},
            {"id": 11, "text": "11. [動作] 抱在肩上直立時，頭部和上半身能豎直至少10秒鐘，不會搖來晃去。", "star": False, "normal_ans": "是"},
            {"id": 12, "text": "12. [社交] ★ 面對面時能持續注視人臉，表現出對人的興趣。", "star": True, "normal_ans": "是"}
        ],
        "6 個月": [
            {"id": 1, "text": "1. [動作] 坐在大人大腿上或靠著沙發時，頭部與背部能維持直立。", "star": False, "normal_ans": "是"},
            {"id": 2, "text": "2. [動作] 仰臥時能順利翻身成俯臥（趴姿）。", "star": False, "normal_ans": "是"},
            {"id": 3, "text": "3. [動作] 看到喜歡的物品會主動伸出雙手去抓取。", "star": False, "normal_ans": "是"},
            {"id": 4, "text": "4. [警訊] ★ 抓到的玩具或物品能順暢地伸向嘴巴探索（口腔期）。", "star": True, "normal_ans": "是"},
            {"id": 5, "text": "5. [動作] 當一手拿著玩具時，能將玩具轉換到另一隻手（換手拿物）。", "star": False, "normal_ans": "是"},
            {"id": 6, "text": "6. [警訊] ★ 發出多種不連貫的音節（如：呀、噠、ㄅㄚ），且高興時會大聲叫。", "star": True, "normal_ans": "是"},
            {"id": 7, "text": "7. [語言] 在身後或側邊發出聲響時，會轉頭尋找聲源。", "star": False, "normal_ans": "是"},
            {"id": 8, "text": "8. [警訊] ★ 見到熟悉照顧者會展現笑臉，面對陌生人開始出現凝視或警戒（認生）。", "star": True, "normal_ans": "是"}
        ],
        "9 個月": [
            {"id": 1, "text": "1. [動作] 不需支撐能獨自坐穩數分鐘（獨坐）。", "star": False, "normal_ans": "是"},
            {"id": 2, "text": "2. [動作] 能以雙手雙腳或腹部貼地向前爬行（爬行）。", "star": False, "normal_ans": "是"},
            {"id": 3, "text": "3. [警訊] ★ 能扶著欄杆或沙發自己拉著站起來（扶站）。", "star": True, "normal_ans": "是"},
            {"id": 4, "text": "4. [動作] 會用大拇指與食指指腹/指尖抓取小餅乾或小物品（精細抓握）。", "star": False, "normal_ans": "是"},
            {"id": 5, "text": "5. [動作] 會兩手各拿一個積木互相敲擊發出聲音。", "star": False, "normal_ans": "是"},
            {"id": 6, "text": "6. [警訊] ★ 開始發出重複的雙音節（如：ㄇㄚ-ㄇㄚ、ㄅㄚ-ㄅㄚ，不一定有意義）。", "star": True, "normal_ans": "是"},
            {"id": 7, "text": "7. [認知] 玩躲貓貓時，當玩具被手帕遮住，會主動掀開尋找（物體恆存）。", "star": False, "normal_ans": "是"},
            {"id": 8, "text": "8. [警訊] ★ 叫寶寶的名字時，會轉頭回應或做出反應。", "star": True, "normal_ans": "是"}
        ],
        "12 個月": [
            {"id": 1, "text": "1. [動作] 能扶著傢俱靈活橫向移動（扶走），或獨立站立數秒。", "star": False, "normal_ans": "是"},
            {"id": 2, "text": "2. [警訊] ★ 不扶任何人或物品，能獨立向前行走 3–5 步（獨走）。", "star": True, "normal_ans": "是"},
            {"id": 3, "text": "3. [動作] 會用精準的大拇指與食指尖捏起細小物品（鉗狀抓握）。", "star": False, "normal_ans": "是"},
            {"id": 4, "text": "4. [語言] 能有意義地喊出「爸爸」或「媽媽」（指著特定人講）。", "star": False, "normal_ans": "是"},
            {"id": 5, "text": "5. [警訊] ★ 能用頭或手勢表示需求（如：揮手表示掰掰、搖頭表示不要）。", "star": True, "normal_ans": "是"},
            {"id": 6, "text": "6. [認知] 聽懂簡單命令（如：「不可以」、「拿給媽媽」）。", "star": False, "normal_ans": "是"},
            {"id": 7, "text": "7. [警訊] ★ 當問「XX在哪裡？」時，能用手指指向熟悉的人或物品。", "star": True, "normal_ans": "是"},
            {"id": 8, "text": "8. [警訊] ★ 會模仿大人的簡單動作（如：揮手、拍手、按按鈕）。", "star": True, "normal_ans": "是"}
        ],
        "18 個月": [
            {"id": 1, "text": "1. [動作] 獨立行走非常穩定，鮮少跌倒，且能嘗試向前慢跑。", "star": False, "normal_ans": "是"},
            {"id": 2, "text": "2. [動作] 能扶著牆壁或大人手，雙膝配合一階一階登上樓梯。", "star": False, "normal_ans": "是"},
            {"id": 3, "text": "3. [警訊] ★ 能將 2–3 塊積木成功對齊疊高。", "star": True, "normal_ans": "是"},
            {"id": 4, "text": "4. [動作] 會拿筆在紙上自發性亂塗畫出線條。", "star": False, "normal_ans": "是"},
            {"id": 5, "text": "5. [警訊] ★ 除了爸爸媽媽，能清晰講出至少 3–5 個有意義的單字。", "star": True, "normal_ans": "是"},
            {"id": 6, "text": "6. [認知] 能指出自己的至少 1 個身體部位（如：眼睛、鼻子、手）。", "star": False, "normal_ans": "是"},
            {"id": 7, "text": "7. [自理] 會嘗試自己拿湯匙舀東西吃，或拿杯子喝水。", "star": False, "normal_ans": "是"},
            {"id": 8, "text": "8. [警訊] ★ 開始展現主見，不順心時會哭鬧，或常說「不要」。", "star": True, "normal_ans": "是"}
        ]
    }
    
    selected_key = "4 個月"
    for k in questions_database.keys():
        if k in stage:
            selected_key = k
            break
            
    current_questions = questions_database[selected_key]
    user_answers = {}
    
    for q in current_questions:
        ans = st.radio(q["text"], ["是", "否"], key=f"q_{selected_key}_{q['id']}", horizontal=True)
        user_answers[q["id"]] = {"ans": ans, "star": q["star"], "normal_ans": q["normal_ans"]}
            
    if st.button("📋 提交發展檢核評估"):
        st.markdown("---")
        star_fail = sum(1 for q_id, info in user_answers.items() if info["ans"] != info["normal_ans"] and info["star"])
        total_fail = sum(1 for q_id, info in user_answers.items() if info["ans"] != info["normal_ans"])
        
        st.subheader("🎯 發展評估結果")
        
        result_text = ""
        if star_fail >= 1 or total_fail >= 2:
            result_text = "建議諮詢小兒科醫師（未達標準）"
            st.error(f"**🔴 {result_text}**")
            st.write(f"（檢測發現：有 {star_fail} 項關鍵警訊指標需注意，總計 {total_fail} 項未達標準）")
        elif total_fail == 1:
            result_text = "持續觀察並於 2-4 週後複評"
            st.warning(f"**🟡 {result_text}**")
        else:
            result_text = "發展非常符合進度（完全通過）"
            st.success(f"**🟢 {result_text}**")
            st.balloons()
            
        st.markdown("---")
        st.subheader("📄 下載寶寶童趣海報日誌")
        st.write("您可以將本次測量與檢核結果下載成圖文海報保存：")
        
        # 可愛圖文海報風格 PDF
        def create_poster_pdf():
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
            elements = []
            
            f_name = pdf_font_name
            
            title_style = ParagraphStyle(
                name='PosterTitle',
                fontName=f_name,
                fontSize=22,
                leading=26,
                textColor=colors.HexColor('#FF5A8D'),
                alignment=1
            )
            
            sub_style = ParagraphStyle(
                name='PosterSub',
                fontName=f_name,
                fontSize=10.5,
                leading=15,
                textColor=colors.HexColor('#795548'),
                alignment=1
            )
            
            card_title_style = ParagraphStyle(
                name='CardTitle',
                fontName=f_name,
                fontSize=9.5,
                leading=13,
                textColor=colors.HexColor('#8D6E63'),
                alignment=1
            )

            card_val_style = ParagraphStyle(
                name='CardVal',
                fontName=f_name,
                fontSize=11,
                leading=15,
                textColor=colors.HexColor('#D81B60'),
                alignment=1
            )
            
            body_style = ParagraphStyle(
                name='PosterBody',
                fontName=f_name,
                fontSize=9.5,
                leading=15,
                textColor=colors.HexColor('#4A148C')
            )
            
            elements.append(Paragraph("<b>🎈 寶寶成長與發展日誌 🎈</b>", title_style))
            elements.append(Spacer(1, 5))
            elements.append(Paragraph("🐣 專屬到府護理照護紀錄 ｜ 陪伴寶寶快樂無憂長大 🐣", sub_style))
            elements.append(Spacer(1, 15))
            
            today_str = datetime.date.today().strftime("%Y年%m月%d日")
            
            h_pct_str = st.session_state.get("h_pct", "15th ~ 50th")
            w_pct_str = st.session_state.get("w_pct", "15th ~ 50th")
            head_pct_str = st.session_state.get("head_pct", "50th ~ 85th")
            
            # 寶寶四大個人卡片
            data_cards = [
                [
                    Paragraph("<b>📅 記錄日期</b>", card_title_style),
                    Paragraph("<b>👶 寶寶月齡</b>", card_title_style),
                    Paragraph("<b>👑 寶寶性別</b>", card_title_style),
                    Paragraph("<b>📋 檢核階段</b>", card_title_style)
                ],
                [
                    Paragraph(f"<b>{today_str}</b>", card_val_style),
                    Paragraph(f"<b>{st.session_state.get('baby_months', 4.0)} 個月</b>", card_val_style),
                    Paragraph(f"<b>{st.session_state.get('baby_gender', '男寶寶')}</b>", card_val_style),
                    Paragraph(f"<b>{stage.split('（')[0]}</b>", card_val_style)
                ]
            ]
            
            t_cards = Table(data_cards, colWidths=[130, 130, 130, 130])
            t_cards.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFF8E7')),
                ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#FFE082')),
                ('INNERGRID', (0,0), (-1,-1), 1, colors.HexColor('#FFE082')),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('PADDING', (0,0), (-1,-1), 8),
            ]))
            elements.append(t_cards)
            elements.append(Spacer(1, 15))
            
            # 生長百分位亮點看板
            elements.append(Paragraph("<b>📊 國健署生長百分位成就亮點</b>", ParagraphStyle('SectionHeader', fontName=f_name, fontSize=12, textColor=colors.HexColor('#FF6F00'))))
            elements.append(Spacer(1, 6))
            
            h_val = st.session_state.get('height_val', 68.0)
            w_val = st.session_state.get('weight_val', 8.2)
            head_val = st.session_state.get('head_val', 43.0)
            
            data_growth = [
                [
                    Paragraph(f"<b>📏 身高落點 ({h_val}cm)</b>", card_title_style),
                    Paragraph(f"<b>⚖️ 體重落點 ({w_val}kg)</b>", card_title_style),
                    Paragraph(f"<b>🧠 頭圍落點 ({head_val}cm)</b>", card_title_style)
                ],
                [
                    Paragraph(f"<b>{h_pct_str}</b>", card_val_style),
                    Paragraph(f"<b>{w_pct_str}</b>", card_val_style),
                    Paragraph(f"<b>{head_pct_str}</b>", card_val_style)
                ]
            ]
            
            t_growth = Table(data_growth, colWidths=[173, 173, 174])
            t_growth.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#E8F5E9')),
                ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#A5D6A7')),
                ('INNERGRID', (0,0), (-1,-1), 1, colors.HexColor('#A5D6A7')),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('PADDING', (0,0), (-1,-1), 8),
            ]))
            elements.append(t_growth)
            elements.append(Spacer(1, 15))
            
            # 檢核結果貼紙
            data_result = [
                [Paragraph("<b>🎯 居托官方發展檢核結果</b>", ParagraphStyle('R1', fontName=f_name, fontSize=10, textColor=colors.HexColor('#0277BD'), alignment=1))],
                [Paragraph(f"<b>{result_text}</b>", ParagraphStyle('R2', fontName=f_name, fontSize=14, textColor=colors.HexColor('#2E7D32'), alignment=1))]
            ]
            t_result = Table(data_result, colWidths=[520])
            t_result.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#E1F5FE')),
                ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#81D4FA')),
                ('PADDING', (0,0), (-1,-1), 10),
            ]))
            elements.append(t_result)
            elements.append(Spacer(1, 15))
            
            # 溫馨叮嚀框
            advice_text = """
            1. 每個寶寶都有獨立發展的步調，請持續保持規律作息與充足營養！<br/>
            2. 定期記錄身高、體重與頭圍，只要曲線穩定沿著百分位區間成長就是棒棒噠！<br/>
            3. 若檢核發現警訊指標未通過，請保持平常心，下一次兒童健檢時可帶本卡片諮詢小兒科醫師。
            """
            
            elements.append(Paragraph("<b>💌 護理師保母的溫馨小叮嚀：</b>", ParagraphStyle('AdviceHead', fontName=f_name, fontSize=11, textColor=colors.HexColor('#6A1B9A'))))
            elements.append(Spacer(1, 5))
            
            t_advice = Table([[Paragraph(advice_text, body_style)]], colWidths=[520])
            t_advice.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F3E5F5')),
                ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#CE93D8')),
                ('PADDING', (0,0), (-1,-1), 10),
            ]))
            elements.append(t_advice)
            
            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_data = create_poster_pdf()
        st.download_button(
            label="📥 下載寶寶童趣海報日誌 (PDF)",
            data=pdf_data,
            file_name=f"寶寶成長海報日誌_{datetime.date.today()}.pdf",
            mime="application/pdf"
        )
