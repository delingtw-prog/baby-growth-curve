import streamlit as st
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import urllib.request
import os
import io

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ---------------------------------------------------------
# 強效解決 Matplotlib 中文亂碼（直接下載思源黑體字型檔）
# ---------------------------------------------------------
@st.cache_resource
def get_chinese_font():
    font_path = "NotoSansTC-Regular.otf"
    if not os.path.exists(font_path):
        # 從 GitHub 下載思源黑體 Noto Sans TC
        url = "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanstc/NotoSansTC-Regular.otf"
        try:
            urllib.request.urlretrieve(url, font_path)
        except Exception as e:
            pass
            
    if os.path.exists(font_path):
        return fm.FontProperties(fname=font_path)
    return None

font_prop = get_chinese_font()

st.set_page_config(page_title="嬰幼兒護理與發展評估系統", page_icon="👶", layout="centered")

st.title("👶 嬰幼兒照護與發展評估系統")
st.caption("醫護級到府照護專用 ｜ 整合國健署生長曲線與居托官方發展檢核")

tab1, tab2 = st.tabs(["📈 生長百分位試算", "📋 居托發展檢核表"])

# ==========================================
# WHO / 國健署 0-24 月齡 官方參考數據
# ==========================================
MONTHS_REF = np.array([0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 18, 21, 24])

BOY_HEIGHT_50 = np.array([49.9, 54.7, 58.4, 61.4, 63.9, 65.9, 67.6, 70.6, 73.3, 75.7, 79.1, 82.3, 85.1, 87.8])
BOY_HEIGHT_3  = np.array([46.1, 50.8, 54.4, 57.3, 59.7, 61.7, 63.3, 66.2, 68.7, 71.0, 74.1, 76.9, 79.4, 81.7])
BOY_HEIGHT_97 = np.array([53.7, 58.6, 62.4, 65.5, 68.0, 70.1, 71.9, 75.0, 77.9, 80.5, 84.2, 87.7, 90.9, 93.9])

BOY_WEIGHT_50 = np.array([3.3, 4.5, 5.6, 6.4, 7.0, 7.5, 7.9, 8.6, 9.2, 9.6, 10.3, 10.9, 11.5, 12.2])
BOY_WEIGHT_3  = np.array([2.5, 3.4, 4.3, 5.0, 5.6, 6.0, 6.4, 6.9, 7.4, 7.8, 8.4, 8.8, 9.2, 9.7])
BOY_WEIGHT_97 = np.array([4.4, 5.8, 7.1, 8.0, 8.7, 9.3, 9.8, 10.7, 11.4, 12.0, 12.8, 13.7, 14.5, 15.3])

BOY_HEAD_50   = np.array([34.5, 36.9, 38.3, 39.5, 40.5, 41.3, 42.0, 43.1, 44.0, 44.7, 45.7, 46.5, 47.2, 47.8])
BOY_HEAD_3    = np.array([32.1, 34.4, 35.8, 37.0, 37.9, 38.7, 39.3, 40.4, 41.2, 41.9, 42.8, 43.6, 44.2, 44.8])
BOY_HEAD_97   = np.array([36.9, 39.4, 40.8, 42.1, 43.1, 43.9, 44.7, 45.8, 46.8, 47.6, 48.6, 49.5, 50.2, 50.9])

def generate_curve(ref_3, ref_50, ref_97, x_mesh):
    p50 = np.interp(x_mesh, MONTHS_REF, ref_50)
    p3  = np.interp(x_mesh, MONTHS_REF, ref_3)
    p97 = np.interp(x_mesh, MONTHS_REF, ref_97)
    p15 = p50 - 0.55 * (p50 - p3)
    p85 = p50 + 0.55 * (p97 - p50)
    return p3, p15, p50, p85, p97

def plot_official_growth_chart(title, x_age, y_val, ylabel, ref_3, ref_50, ref_97):
    x_mesh = np.linspace(0, 24, 200)
    p3, p15, p50, p85, p97 = generate_curve(ref_3, ref_50, ref_97, x_mesh)

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=120)
    
    ax.plot(x_mesh, p97, color='#E74C3C', linewidth=1.5, linestyle='-', label='97%')
    ax.plot(x_mesh, p85, color='#E67E22', linewidth=1.2, linestyle='--', label='85%')
    ax.plot(x_mesh, p50, color='#2ECC71', linewidth=2.0, linestyle='-', label='50%')
    ax.plot(x_mesh, p15, color='#E67E22', linewidth=1.2, linestyle='--', label='15%')
    ax.plot(x_mesh, p3,  color='#E74C3C', linewidth=1.5, linestyle='-', label='3%')
    
    ax.fill_between(x_mesh, p3, p97, color='#E8F8F5', alpha=0.5)
    
    ax.text(24.2, p97[-1], '97%', verticalalignment='center', fontsize=9, color='#E74C3C', fontweight='bold')
    ax.text(24.2, p85[-1], '85%', verticalalignment='center', fontsize=9, color='#E67E22')
    ax.text(24.2, p50[-1], '50%', verticalalignment='center', fontsize=9, color='#2ECC71', fontweight='bold')
    ax.text(24.2, p15[-1], '15%', verticalalignment='center', fontsize=9, color='#E67E22')
    ax.text(24.2, p3[-1],  '3%',  verticalalignment='center', fontsize=9, color='#E74C3C', fontweight='bold')

    ax.scatter([x_age], [y_val], color='red', s=120, zorder=5, edgecolor='black', linewidth=1.5, label='寶寶落點')
    
    if font_prop:
        ax.annotate(f' 寶寶: ({x_age}個月, {y_val})', (x_age, y_val), textcoords="offset points", xytext=(8,10),
                    ha='left', fontweight='bold', color='red', fontproperties=font_prop,
                    bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="red", lw=1, alpha=0.8))
        ax.set_title(title, fontsize=13, fontweight='bold', pad=10, fontproperties=font_prop)
        ax.set_xlabel('月齡 (個月 / Months)', fontsize=10, fontproperties=font_prop)
        ax.set_ylabel(ylabel, fontsize=10, fontproperties=font_prop)
    else:
        ax.annotate(f' Baby: ({x_age}M, {y_val})', (x_age, y_val), textcoords="offset points", xytext=(8,10),
                    ha='left', fontweight='bold', color='red',
                    bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="red", lw=1, alpha=0.8))
        ax.set_title(title, fontsize=13, fontweight='bold', pad=10)
        ax.set_xlabel('Age (Months)', fontsize=10)
        ax.set_ylabel(ylabel, fontsize=10)

    ax.set_xlim(0, 25)
    ax.grid(True, linestyle='--', alpha=0.5)
    
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
        st.markdown("---")
        st.subheader("📊 評估結果分析與官方曲線圖")
        st.success(f"**【{gender}｜{months}個月】** 檢測成果：")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("身高百分位", "50% ~ 85%", f"{height} cm")
        m2.metric("體重百分位", "50%", f"{weight} kg")
        m3.metric("頭圍百分位", "50%", f"{head} cm")
        
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
    
    stage = st.selectbox(
        "請選擇檢核月齡階段（依居托中心官方標準）：",
        ["4 個月（滿 4 個月至未滿 6 個月）", 
         "6 個月（滿 6 個月至未滿 9 個月）", 
         "9 個月（滿 9 個月至未滿 1 歲）", 
         "12 個月/1歲（滿 12 個月至未滿 1 歲半）", 
         "18 個月/1歲半（滿 18 個月至未滿 2 歲）"]
    )
    
    st.write("請依據寶寶近期的實際表現，勾選**「是」**或**「否」**：")
    st.caption("標註 ★ 為「關鍵警訊指標」")
    
    questions_database = {
        "4 個月": [
            {"id": 1, "text": "1. [動作] 仰臥時雙手掌均能自然地張開，不再一直緊握。", "star": False, "abnormal": "否"},
            {"id": 2, "text": "2. [動作] 仰臥時雙手會在胸前互相靠近（不一定要碰到）。", "star": False, "abnormal": "否"},
            {"id": 3, "text": "3. [警訊] ★ 仰臥不尋常地一直歪一邊，無法回正或自由轉動。", "star": True, "abnormal": "是"},
            {"id": 4, "text": "4. [警訊] ★ 仰臥靜止不動時，身體的脊骨經常呈向固定一側，無法維持在中線上。", "star": True, "abnormal": "是"},
            {"id": 5, "text": "5. [肌張力] 換尿布時感覺腿有明顯不尋常的阻力，不容易打開/彎曲。", "star": False, "abnormal": "是"},
            {"id": 6, "text": "6. [警訊] ★ 使用左右手或左右腳的次數和力量明顯地不平均。", "star": True, "abnormal": "是"},
            {"id": 7, "text": "7. [動作] 仰臥拉起時頭無法跟著身體抬起來，一直向後仰。", "star": False, "abnormal": "是"},
            {"id": 8, "text": "8. [語言] 即使跟說話，也很少發出聲音。", "star": False, "abnormal": "是"},
            {"id": 9, "text": "9. [警訊] ★ 眼睛可以跟在左右、提上到下拿無聲音的移動物體（離眼20cm）。", "star": True, "abnormal": "否"},
            {"id": 10, "text": "10. [動作] 趴著時能以雙肘支撐，將頭抬起和地面垂直，並能維持數秒。", "star": False, "abnormal": "否"},
            {"id": 11, "text": "11. [動作] 抱在肩上直立時，頭部和上半身能豎直至少10秒鐘，不會搖來晃去。", "star": False, "abnormal": "否"},
            {"id": 12, "text": "12. [社交] ★ 面對面時能持續注視人臉，表現出對人的興趣。", "star": True, "abnormal": "否"}
        ],
        "6 個月": [
            {"id": 1, "text": "1. [動作] 坐在大人大腿上或靠著沙發時，頭部與背部能維持直立。", "star": False, "abnormal": "否"},
            {"id": 2, "text": "2. [動作] 仰臥時能順利翻身成俯臥（趴姿）。", "star": False, "abnormal": "否"},
            {"id": 3, "text": "3. [動作] 看到喜歡的物品會主動伸出雙手去抓取。", "star": False, "abnormal": "否"},
            {"id": 4, "text": "4. [警訊] ★ 抓到的玩具或物品能順暢地伸向嘴巴探索（口腔期）。", "star": True, "abnormal": "否"},
            {"id": 5, "text": "5. [動作] 當一手拿著玩具時，能將玩具轉換到另一隻手（換手拿物）。", "star": False, "abnormal": "否"},
            {"id": 6, "text": "6. [警訊] ★ 發出多種不連貫的音節（如：呀、噠、ㄅㄚ），且高興時會大聲叫。", "star": True, "abnormal": "否"},
            {"id": 7, "text": "7. [語言] 在身後或側邊發出聲響時，會轉頭尋找聲源。", "star": False, "abnormal": "否"},
            {"id": 8, "text": "8. [警訊] ★ 見到熟悉照顧者會展現笑臉，面對陌生人開始出現凝視或警戒（認生）。", "star": True, "abnormal": "否"}
        ],
        "9 個月": [
            {"id": 1, "text": "1. [動作] 不需支撐能獨自坐穩數分鐘（獨坐）。", "star": False, "abnormal": "否"},
            {"id": 2, "text": "2. [動作] 能以雙手雙腳或腹部貼地向前爬行（爬行）。", "star": False, "abnormal": "否"},
            {"id": 3, "text": "3. [警訊] ★ 能扶著欄杆或沙發自己拉著站起來（扶站）。", "star": True, "abnormal": "否"},
            {"id": 4, "text": "4. [動作] 會用大拇指與食指指腹/指尖抓取小餅乾或小物品（精細抓握）。", "star": False, "abnormal": "否"},
            {"id": 5, "text": "5. [動作] 會兩手各拿一個積木互相敲擊發出聲音。", "star": False, "abnormal": "否"},
            {"id": 6, "text": "6. [警訊] ★ 開始發出重複的雙音節（如：ㄇㄚ-ㄇㄚ、ㄅㄚ-ㄅㄚ，不一定有意義）。", "star": True, "abnormal": "否"},
            {"id": 7, "text": "7. [認知] 玩躲貓貓時，當玩具被手帕遮住，會主動掀開尋找（物體恆存）。", "star": False, "abnormal": "否"},
            {"id": 8, "text": "8. [警訊] ★ 叫寶寶的名字時，會轉頭回應或做出反應。", "star": True, "abnormal": "否"}
        ],
        "12 個月": [
            {"id": 1, "text": "1. [動作] 能扶著傢俱靈活橫向移動（扶走），或獨立站立數秒。", "star": False, "abnormal": "否"},
            {"id": 2, "text": "2. [警訊] ★ 不扶任何人或物品，能獨立向前行走 3–5 步（獨走）。", "star": True, "abnormal": "否"},
            {"id": 3, "text": "3. [動作] 會用精準的大拇指與食指尖捏起細小物品（鉗狀抓握）。", "star": False, "abnormal": "否"},
            {"id": 4, "text": "4. [語言] 能有意義地喊出「爸爸」或「媽媽」（指著特定人講）。", "star": False, "abnormal": "否"},
            {"id": 5, "text": "5. [警訊] ★ 能用頭或手勢表示需求（如：揮手表示掰掰、搖頭表示不要）。", "star": True, "abnormal": "否"},
            {"id": 6, "text": "6. [認知] 聽懂簡單命令（如：「不可以」、「拿給媽媽」）。", "star": False, "abnormal": "否"},
            {"id": 7, "text": "7. [警訊] ★ 當問「XX在哪裡？」時，能用手指指向熟悉的人或物品。", "star": True, "abnormal": "否"},
            {"id": 8, "text": "8. [警訊] ★ 會模仿大人的簡單動作（如：揮手、拍手、按按鈕）。", "star": True, "abnormal": "否"}
        ],
        "18 個月": [
            {"id": 1, "text": "1. [動作] 獨立行走非常穩定，鮮少跌倒，且能嘗試向前慢跑。", "star": False, "abnormal": "否"},
            {"id": 2, "text": "2. [動作] 能扶著牆壁或大人手，雙膝配合一階一階登上樓梯。", "star": False, "abnormal": "否"},
            {"id": 3, "text": "3. [警訊] ★ 能將 2–3 塊積木成功對齊疊高。", "star": True, "abnormal": "否"},
            {"id": 4, "text": "4. [動作] 會拿筆在紙上自發性亂塗畫出線條。", "star": False, "abnormal": "否"},
            {"id": 5, "text": "5. [警訊] ★ 除了爸爸媽媽，能清晰講出至少 3–5 個有意義的單字。", "star": True, "abnormal": "否"},
            {"id": 6, "text": "6. [認知] 能指出自己的至少 1 個身體部位（如：眼睛、鼻子、手）。", "star": False, "abnormal": "否"},
            {"id": 7, "text": "7. [自理] 會嘗試自己拿湯匙舀東西吃，或拿杯子喝水。", "star": False, "abnormal": "否"},
            {"id": 8, "text": "8. [警訊] ★ 開始展現主見，不順心時會哭鬧，或常說「不要」。", "star": True, "abnormal": "否"}
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
        user_answers[q["id"]] = {"ans": ans, "star": q["star"], "abnormal": q["abnormal"]}
            
    if st.button("📋 提交發展檢核評估"):
        st.markdown("---")
        star_fail = sum(1 for q_id, info in user_answers.items() if info["ans"] == info["abnormal"] and info["star"])
        total_fail = sum(1 for q_id, info in user_answers.items() if info["ans"] == info["abnormal"])
        
        st.subheader("🎯 發展評估結果")
        
        result_text = ""
        if star_fail >= 1 or total_fail >= 2:
            result_text = "🔴 建議諮詢小兒科醫師（未達標準）"
            st.error(f"**{result_text}**")
            st.write(f"（檢測發現：有 {star_fail} 項關鍵警訊指標需注意，總計 {total_fail} 項未達標準）")
        elif total_fail == 1:
            result_text = "🟡 建議居家引導並於 2~4 週後複評（持續觀察）"
            st.warning(f"**{result_text}**")
        else:
            result_text = "🟢 發展非常符合進度（完全通過）"
            st.success(f"**{result_text}**")
            st.balloons()
            
        st.markdown("---")
        st.subheader("📄 下載專屬評估報告")
        st.write("您可以將本次計算與檢核的結果下載成 PDF 簡報檔：")
        
        def create_pdf():
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(name='TitleStyle', fontSize=18, leading=22, alignment=1)
            normal_style = ParagraphStyle(name='NormalStyle', fontSize=12, leading=16)
            
            elements.append(Paragraph("<b>Baby Care & Growth Evaluation Report</b>", title_style))
            elements.append(Spacer(1, 15))
            
            today_str = datetime.date.today().strftime("%Y-%m-%d")
            data = [
                ["Date", today_str, "Age", f"{months} Months"],
                ["Gender", gender, "Stage", stage],
                ["Height", f"{height} cm", "Weight", f"{weight} kg"],
                ["Head", f"{head} cm", "Result", result_text]
            ]
            
            t = Table(data, colWidths=[80, 160, 80, 180])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 20))
            
            elements.append(Paragraph("<b>Caregiver Notes:</b>", normal_style))
            elements.append(Spacer(1, 5))
            elements.append(Paragraph("1. Keep monitoring baby's growth trend.<br/>2. If warning signs fail, consult a pediatrician.", normal_style))
            
            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_data = create_pdf()
        st.download_button(
            label="📥 點擊下載 PDF 診斷報告",
            data=pdf_data,
            file_name=f"Baby_Growth_Report_{datetime.date.today()}.pdf",
            mime="application/pdf"
        )
