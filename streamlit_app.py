import streamlit as st
import sqlite3
import uuid
import datetime
import os
import time
import pandas as pd
import plotly.express as px

# ==========================================
# 1. 全局配置
# ==========================================
st.set_page_config(
    page_title="Global Insights | Data Map",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. 样式合并 (基础样式 + 咖啡加强版样式)
# ==========================================
st.markdown("""
<style>
    /* --- 基础设置 --- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {display: none;}
    .stApp { background-color: #FFFFFF !important; }

    /* --- 右上角按钮 --- */
    .neal-btn {
        font-family: 'Inter', sans-serif; background: #fff;
        border: 1px solid #e5e7eb; color: #111; font-weight: 600;
        padding: 8px 16px; border-radius: 8px; cursor: pointer;
        transition: all 0.2s; display: inline-flex; align-items: center;
        justify-content: center; text-decoration: none !important;
        width: 100%;
    }
    .neal-btn:hover { background: #f9fafb; transform: translateY(-1px); }
    .neal-btn-link { text-decoration: none; width: 100%; display: block; }

    /* --- 统计模块 --- */
    .metric-container {
        display: flex; justify-content: center; gap: 20px;
        margin-top: 20px; padding: 10px; background-color: #f8f9fa;
        border-radius: 10px; border: 1px solid #e9ecef;
    }
    .metric-box { text-align: center; }
    .metric-sub { font-size: 0.7rem; color: #adb5bd; }

    /* --- ☕ 咖啡打赏 2.0 专用样式 --- */
    .pay-card {
        background: #fdfdfd;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-top: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .pay-amount-display {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.8rem;
        font-weight: 800;
        margin: 10px 0;
    }
    .pay-label {
        font-size: 0.85rem; color: #64748b; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px;
    }
    .pay-instruction {
        font-size: 0.8rem; color: #94a3b8; margin-top: 15px; margin-bottom: 5px;
    }
    .color-wechat { color: #2AAD67; }
    .color-alipay { color: #1677ff; }
    .color-paypal { color: #003087; }
    
    div[data-testid="stButton"] button { border-radius: 8px; }

    /* 语言切换按钮定位 */
    [data-testid="button-lang_switch"] {
        position: fixed; top: 20px; right: 120px; z-index: 999; width: 80px !important;
    }

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500&display=swap');
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 状态初始化
# ==========================================
if 'start_time' not in st.session_state:
    st.session_state.start_time = datetime.datetime.now()
    st.session_state.access_status = 'free'
    st.session_state.unlock_time = None

if 'language' not in st.session_state:
    st.session_state.language = 'zh'
if 'coffee_num' not in st.session_state:
    st.session_state.coffee_num = 1
  
if 'visitor_id' not in st.session_state:
    st.session_state["visitor_id"] = str(uuid.uuid4())

# ==========================================
# 4. 常量与文本配置
# ==========================================
FREE_PERIOD_SECONDS = 600 # 调试方便改为600秒，实际可改回60
ACCESS_DURATION_HOURS = 24
UNLOCK_CODE = "vip24"
DB_FILE = os.path.join(os.path.expanduser("~/"), "visit_stats.db")

lang_texts = {
    'zh': {
        'coffee_desc': '如果这些工具帮到了你，欢迎支持老登的创作。',
        'footer_btn3': '请老登一杯咖啡 ☕',
        'custom_count': '自定义数量 (杯)',
        'pay_wechat': '微信支付',
        'pay_alipay': '支付宝',
        'pay_paypal': '贝宝',
        'paid_btn': '🎉 我已支付，给老登打气！',
        'pay_success': "收到！感谢打赏。代码写得更有劲了！❤️",
        "coffee_btn": "☕ 请开发者喝咖啡",
        "coffee_title": " ",
        "coffee_amount": "请输入打赏杯数"
    },
    'en': {
        'coffee_desc': "If you enjoyed this, consider buying me a coffee!",
        'footer_btn3': 'Support Me ☕',
        'custom_count': 'Custom count (cups)',
        'pay_wechat': 'WeChat',
        'pay_alipay': 'Alipay',
        'pay_paypal': 'PayPal',
        'paid_btn': '🎉 I have paid!',
        'pay_success': "Received! Thanks for the coffee! ❤️",
        "coffee_btn": "☕ Buy me a coffee",
        "coffee_title": " ",
        "coffee_amount": "Enter Coffee Count"
    }
}
current_text = lang_texts[st.session_state.language]

# ==========================================
# 5. 右上角功能区
# ==========================================
col_empty, col_lang, col_more = st.columns([0.7, 0.1, 0.2])
with col_lang:
    l_btn = "En" if st.session_state.language == 'zh' else "中"
    if st.button(l_btn, key="lang_switch"):
        st.session_state.language = 'en' if st.session_state.language == 'zh' else 'zh'
        st.rerun()

with col_more:
    st.markdown("""
        <a href="https://laodeng.streamlit.app/" target="_blank" class="neal-btn-link">
            <button class="neal-btn">✨ 更多好玩应用</button>
        </a>""", unsafe_allow_html=True)

# ==========================================
# 6. 权限校验逻辑
# ==========================================
current_time = datetime.datetime.now()
access_granted = False

if st.session_state.access_status == 'free':
    time_elapsed = (current_time - st.session_state.start_time).total_seconds()
    if time_elapsed < FREE_PERIOD_SECONDS:
        access_granted = True
        st.info(f"⏳ **免费试用中... 剩余 {FREE_PERIOD_SECONDS - time_elapsed:.1f} 秒。**")
    else:
        st.session_state.access_status = 'locked'
        st.rerun()
elif st.session_state.access_status == 'unlocked':
    unlock_expiry = st.session_state.unlock_time + datetime.timedelta(hours=ACCESS_DURATION_HOURS)
    if current_time < unlock_expiry:
        access_granted = True
        left = unlock_expiry - current_time
        st.info(f"🔓 **付费权限剩余:** {int(left.total_seconds()//3600)} 小时")
    else:
        st.session_state.access_status = 'locked'
        st.rerun()

if not access_granted:
    st.error("🔒 **访问受限。免费试用期已结束！**")
    st.markdown(f"""
    <div style="background-color: #fff; padding: 15px; border-radius: 8px; border: 1px solid #e5e7eb; margin-top: 15px;">
        <p style="font-weight: 600; color: #1f2937; margin-bottom: 5px;">🔑 10元解锁无限制访问权限</p>
        <code style="background-color: #eef2ff; padding: 5px;">#小程序://闲鱼/i4ahD0rqwGB5lba</code>
    </div>""", unsafe_allow_html=True)
    
    with st.form("lock_form"):
        if st.form_submit_button("验证并解锁") and st.text_input("解锁代码", type="password") == UNLOCK_CODE:
            st.session_state.access_status, st.session_state.unlock_time = 'unlocked', datetime.datetime.now()
            st.rerun()
    st.stop()


# ==========================================
# 核心功能区 (已解锁)
# ==========================================
st.divider()
st.title("🗺️ 全球数据透视 | Global Insights")
st.write("以下数据展示了毒品贸易与能源格局的关键流动与对比。")

# --- 功能函数：绘制地图 ---
def plot_world_map(df, loc_col, val_col, hover_cols, title, color_scale="Reds", log_scale=False):
    fig = px.choropleth(
        df,
        locations=loc_col,
        locationmode="country names",
        color=val_col,
        hover_name=loc_col,
        hover_data=hover_cols,
        color_continuous_scale=color_scale,
        title=title,
        projection="equirectangular" 
    )
    fig.update_layout(
        margin={"r":0,"t":40,"l":0,"b":0},
        geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular'),
        height=500
    )
    return fig

# ----------------------------------------------------
# 模块 1: 美国毒品进口来源 (Cocaine & Fentanyl)
# ----------------------------------------------------
with st.expander("💊 美国毒品进口来源与中转 (Cocaine & Fentanyl)", expanded=True):
    drug_type = st.radio("选择毒品类型 / Select Drug Type", ["可卡因 (Cocaine)", "芬太尼 (Fentanyl)"], horizontal=True)

    if "Cocaine" in drug_type:
        st.markdown("""
        > **关键洞察**: 90% 的可卡因经由 **墨西哥** 路线进入美国，**委内瑞拉** 路线约占 10%。
        > 哥伦比亚是最大的源头国。
        """)
        

        # 模拟数据 (基于DEA报告估算)
        data_cocaine = {
            "Country": ["Colombia", "Peru", "Bolivia", "Mexico", "Venezuela", "Ecuador", "United States"],
            "Role": ["主产地 (Primary Source)", "产地 (Source)", "产地 (Source)", "核心中转 (Primary Transit)", "次级中转 (Secondary Transit)", "中转 (Transit)", "目的地 (Destination)"],
            "Flow_Share": [90, 20, 10, 90, 10, 35, 0], # Flow share towards US
            "Rank": [1, 2, 3, "Transit #1", "Transit #2", "Transit #3", "-"]
        }
        df_c = pd.DataFrame(data_cocaine)
        
        fig1 = px.choropleth(
            df_c, locations="Country", locationmode="country names",
            color="Flow_Share", 
            hover_name="Country",
            hover_data={"Role": True, "Rank": True, "Flow_Share": ":.0f%"},
            color_continuous_scale="Oranges",
            labels={"Flow_Share": "Estimated US Flow Impact (%)"},
            title="可卡因流向美国：源头与中转热力图"
        )
        st.plotly_chart(fig1, use_container_width=True)

    else:
        st.markdown("""
        > **关键洞察**: 芬太尼主要由 **墨西哥** 贩毒集团合成，前体化学品多来自亚洲。
        > **委内瑞拉** 在芬太尼供应链中几乎**无角色**。
        """)
        
        data_fentanyl = {
            "Country": ["Mexico", "China", "United States", "Venezuela", "Canada"],
            "Role": ["主要合成地 (Primary Synthesis)", "前体来源 (Precursor Source)", "目的地 (Destination)", "无主要关联 (No Link)", "次要来源 (Minor Source)"],
            "Risk_Score": [95, 60, 0, 1, 5], 
            "Details": ["主要成品供应源", "化学原料供应", "消费国", "无生产记录", "少量跨境走私"]
        }
        df_f = pd.DataFrame(data_fentanyl)
        
        fig2 = px.choropleth(
            df_f, locations="Country", locationmode="country names",
            color="Risk_Score",
            hover_name="Country",
            hover_data={"Role": True, "Details": True},
            color_continuous_scale="Reds",
            labels={"Risk_Score": "Supply Risk Index"},
            title="芬太尼供应风险地图 (US Market)"
        )
        st.plotly_chart(fig2, use_container_width=True)

# ----------------------------------------------------
# 模块 2: 全球石油产量 vs 储量
# ----------------------------------------------------
with st.expander("🛢️ 全球石油：产量 vs 储量 (Production vs Reserves)", expanded=True):
    view_mode = st.radio("查看模式 / View Mode", ["已探明储量 (Reserves)", "日产量 (Production)"], horizontal=True)
    
    # 模拟数据 (2025/2026 预估数据)
    data_oil = {
        "Country": ["Venezuela", "Saudi Arabia", "United States", "Canada", "Iran", "Iraq", "Russia", "China", "UAE", "Kuwait", "Brazil"],
        "Reserves_Billion_Barrels": [303, 267, 68, 171, 208, 145, 107, 26, 111, 101, 13],
        "Production_Million_BPD": [1.1, 9.0, 13.3, 4.8, 3.2, 4.3, 9.5, 4.2, 3.0, 2.5, 3.5],
        "Reserves_Rank": [1, 2, 9, 3, 4, 5, 6, 13, 7, 8, 15],
        "Production_Rank": [20, 2, 1, 4, 8, 6, 3, 5, 7, 9, 8]
    }
    df_oil = pd.DataFrame(data_oil)
    # 计算百分比
    total_reserves = df_oil["Reserves_Billion_Barrels"].sum() * 1.2 # 估算全球总和
    total_prod = df_oil["Production_Million_BPD"].sum() * 1.3
    
    df_oil["Reserves_Share"] = (df_oil["Reserves_Billion_Barrels"] / total_reserves) * 100
    df_oil["Production_Share"] = (df_oil["Production_Million_BPD"] / total_prod) * 100

    if "Reserves" in view_mode:
        st.info("💡 **委内瑞拉**拥有世界第一的石油储量 (约19%)，但受制于基础设施，大部分未被开采。")
        
        
        fig3 = px.choropleth(
            df_oil, locations="Country", locationmode="country names",
            color="Reserves_Billion_Barrels",
            hover_name="Country",
            hover_data={"Reserves_Rank": True, "Reserves_Share": ":.1f%", "Production_Rank": True},
            color_continuous_scale="Viridis",
            labels={"Reserves_Billion_Barrels": "Reserves (Billion Barrels)"},
            title="全球石油储量分布图 (Billion Barrels)"
        )
        st.plotly_chart(fig3, use_container_width=True)
        
    else:
        st.warning("⚠️ 尽管储量第一，**委内瑞拉**的产量仅排名第 20 左右。美国是当前世界最大产油国。")
        
        fig4 = px.choropleth(
            df_oil, locations="Country", locationmode="country names",
            color="Production_Million_BPD",
            hover_name="Country",
            hover_data={"Production_Rank": True, "Production_Share": ":.1f%", "Reserves_Rank": True},
            color_continuous_scale="Plasma",
            labels={"Production_Million_BPD": "Production (Million BPD)"},
            title="全球石油日产量分布图 (Million Barrels/Day)"
        )
        st.plotly_chart(fig4, use_container_width=True)


# ==========================================
# 8. 咖啡打赏系统
# ==========================================

def get_txt(key): 
    return lang_texts[st.session_state.language][key]

st.markdown("<br><br>", unsafe_allow_html=True)    
c1, c2, c3 = st.columns([1, 2, 1])

with c2:
    @st.dialog(" " + get_txt('coffee_title'), width="small")
    def show_coffee_window():
        st.markdown(f"""<div style="text-align:center; color:#666; margin-bottom:15px;">{get_txt('coffee_desc')}</div>""", unsafe_allow_html=True)
        
        presets = [("☕", 1), ("🍗", 3), ("🚀", 5)]
        def set_val(n): st.session_state.coffee_num = n
        
        cols = st.columns(3, gap="small")
        for i, (icon, num) in enumerate(presets):
            with cols[i]:
                if st.button(f"{icon} {num}", use_container_width=True, key=f"p_btn_{i}"): 
                    set_val(num)
        st.write("")

        col_amount, col_total = st.columns([1, 1], gap="small")
        with col_amount: 
            cnt = st.number_input(get_txt('coffee_amount'), 1, 100, step=1, key='coffee_num')
        
        cny_total = cnt * 10
        usd_total = cnt * 2
        
        def render_pay_tab(title, amount_str, color_class, img_path, qr_data_suffix, link_url=None):
            with st.container(border=True):
                st.markdown(f"""
                    <div style="text-align: center; padding-bottom: 10px;">
                        <div class="pay-label {color_class}" style="margin-bottom: 5px;">{title}</div>
                        <div class="pay-amount-display {color_class}" style="margin: 0; font-size: 1.8rem;">{amount_str}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                c_img_1, c_img_2, c_img_3 = st.columns([1, 4, 1])
                with c_img_2:
                    if os.path.exists(img_path): 
                        st.image(img_path, use_container_width=True)
                    else: 
                        qr_data = f"Donate_{cny_total}_{qr_data_suffix}"
                        if link_url: qr_data = link_url
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data={qr_data}", use_container_width=True)
                
                if link_url:
                    st.write("")
                    st.link_button(f"👉 Pay {amount_str}", link_url, type="primary", use_container_width=True)
                else:
                    st.markdown(f"""<div class="pay-instruction" style="text-align: center; padding-top: 10px;">请使用手机扫描上方二维码</div>""", unsafe_allow_html=True)
                    
        st.write("")
        t1, t2, t3 = st.tabs([get_txt('pay_wechat'), get_txt('pay_alipay'), get_txt('pay_paypal')])
        
        with t1: render_pay_tab("WeChat Pay", f"¥{cny_total}", "color-wechat", "wechat_pay.jpg", "WeChat")
        with t2: render_pay_tab("Alipay", f"¥{cny_total}", "color-alipay", "ali_pay.jpg", "Alipay")
        with t3: render_pay_tab("PayPal", f"${usd_total}", "color-paypal", "paypal.png", "PayPal", "https://paypal.me/ytqz")
        
        st.write("")
        if st.button("🎉 " + get_txt('pay_success').split('!')[0], type="primary", use_container_width=True):
            st.balloons()
            st.success(get_txt('pay_success').format(count=cnt))
            time.sleep(1.5)
            st.rerun()

    if st.button(get_txt('coffee_btn'), use_container_width=True):
        show_coffee_window()


# ==========================================
# 9. 数据库统计 (保持原样)
# ==========================================
DB_DIR = os.path.expanduser("~/")
DB_FILE = os.path.join(DB_DIR, "template_visit_stats.db")
    
def track_stats():
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS daily_traffic (date TEXT PRIMARY KEY, pv_count INTEGER DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS visitors (visitor_id TEXT PRIMARY KEY, last_visit_date TEXT)''')
        
        today = datetime.datetime.utcnow().date().isoformat()
        vid = st.session_state["visitor_id"]
        
        if "has_counted" not in st.session_state:
            c.execute("INSERT OR IGNORE INTO daily_traffic (date, pv_count) VALUES (?, 0)", (today,))
            c.execute("UPDATE daily_traffic SET pv_count = pv_count + 1 WHERE date=?", (today,))
            c.execute("INSERT OR REPLACE INTO visitors (visitor_id, last_visit_date) VALUES (?, ?)", (vid, today))
            conn.commit()
            st.session_state["has_counted"] = True
        
        t_uv = c.execute("SELECT COUNT(*) FROM visitors WHERE last_visit_date=?", (today,)).fetchone()[0]
        a_uv = c.execute("SELECT COUNT(*) FROM visitors").fetchone()[0]
        conn.close()
        return t_uv, a_uv
    except Exception as e:
        return 0, 0

today_uv, total_uv = track_stats()

st.markdown(f"""
<style>
    .stats-bar {{
        display: flex; justify-content: center; gap: 25px; margin-top: 40px; 
        padding: 15px 25px; background-color: white; border-radius: 50px; 
        border: 1px solid #eee; color: #6b7280; font-size: 0.85rem; 
        width: fit-content; margin-left: auto; margin-right: auto; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }}
</style>
<div class="stats-bar">
    <div style="text-align: center;"><div>今日 UV</div><div style="font-weight:700; color:#111;">{today_uv}</div></div>
    <div style="border-left:1px solid #eee; padding-left:25px; text-align: center;"><div>历史 UV</div><div style="font-weight:700; color:#111;">{total_uv}</div></div>
</div>
""", unsafe_allow_html=True)
