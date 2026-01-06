import streamlit as st
import sqlite3
import uuid
import datetime
import os
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. 全局配置
# ==========================================
st.set_page_config(
    page_title="Global Insights | Data Map V2",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. 样式合并 (保留原样)
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
    
    /* 调整表格样式使其更紧凑 */
    div[data-testid="stDataFrame"] div[class^="stDataFrame"] {
        font-size: 0.9rem;
    }

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500&display=swap');
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 状态初始化 (修改默认语言为 en)
# ==========================================
if 'start_time' not in st.session_state:
    st.session_state.start_time = datetime.datetime.now()
    st.session_state.access_status = 'free'
    st.session_state.unlock_time = None

# 修改：默认设为 'en'
if 'language' not in st.session_state:
    st.session_state.language = 'en'
    
if 'coffee_num' not in st.session_state:
    st.session_state.coffee_num = 1
  
if 'visitor_id' not in st.session_state:
    st.session_state["visitor_id"] = str(uuid.uuid4())

# ==========================================
# 4. 常量与文本配置 (扩充字典)
# ==========================================
FREE_PERIOD_SECONDS = 600 
ACCESS_DURATION_HOURS = 24
UNLOCK_CODE = "vip24"
DB_FILE = os.path.join(os.path.expanduser("~/"), "visit_stats.db")

lang_texts = {
    'zh': {
        # Footer & Pay
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
        "coffee_amount": "请输入打赏杯数",
        
        # Main UI
        "main_title": "🗺️ 不要为我哭泣，委内瑞拉",
        "main_subtitle": "数据展示美国侵略委内瑞拉为了毒品还是石油",
        
        # Expander 1: Drugs
        "exp1_title": "💊 美国毒品进口来源与中转 (Cocaine & Fentanyl)",
        "drug_select": "选择毒品类型",
        "opt_cocaine": "可卡因 (Cocaine)",
        "opt_fentanyl": "芬太尼 (Fentanyl)",
        "insight_cocaine": "> **关键洞察**: 90% 的可卡因经由 **墨西哥** 路线进入美国，**委内瑞拉** 路线约占 10%。\n> 哥伦比亚是最大的源头国。",
        "insight_fentanyl": "> **关键洞察**: 芬太尼主要由 **墨西哥** 贩毒集团合成，前体化学品多来自亚洲。\n> **委内瑞拉** 在芬太尼供应链中几乎**无角色**。",
        "chart1_title": "可卡因流向美国：源头与中转热力图",
        "chart1_label": "流向美国影响因子 (%)",
        "chart2_title": "芬太尼供应风险地图 (US Market)",
        "chart2_label": "供应风险指数",
        "tab_caption_flow": "📊 数据明细 (按影响因子排序)",
        "tab_caption_risk": "📊 风险数据明细",
        
        # Data Labels (Drugs)
        "role_primary_src": "主产地", "role_src": "产地", "role_transit_core": "核心中转", "role_transit_sec": "次级中转", "role_transit": "中转", "role_dest": "目的地",
        "rank_src_1": "源头#1", "rank_src_2": "源头#2", "rank_src_3": "源头#3", "rank_trans_1": "中转#1", "rank_trans_2": "中转#2", "rank_trans_3": "中转#3",
        "role_syn": "主要合成地", "role_pre": "前体来源", "role_none": "无主要关联", "role_minor": "次要来源",
        "det_syn": "主要成品供应源", "det_pre": "化学原料供应", "det_cons": "消费国", "det_none": "无生产记录", "det_smug": "少量跨境走私",

        # Expander 2: Oil
        "exp2_title": "🛢️ 全球石油：产量 vs 储量 (Production vs Reserves)",
        "view_mode": "查看模式",
        "opt_reserves": "已探明储量 (Reserves)",
        "opt_prod": "日产量 (Production)",
        "insight_reserves": "💡 **委内瑞拉**拥有世界第一的石油储量 (约19%)，但受制于基础设施，大部分未被开采。",
        "insight_prod": "⚠️ 尽管储量第一，**委内瑞拉**的产量仅排名第 20 左右。美国是当前世界最大产油国。",
        "chart3_title": "全球石油储量分布图",
        "chart3_label": "储量 (十亿桶)",
        "chart4_title": "全球石油日产量分布图",
        "chart4_label": "日产量 (百万桶)",
        "tab_caption_res": "📊 储量排行榜 (Top Reserves)",
        "tab_caption_prod": "📊 产量排行榜 (Top Production)",
        
        # Table Columns
        "col_country": "国家", "col_role": "角色", "col_rank": "排名", "col_share": "份额", "col_risk": "风险指数", 
        "col_reserves": "储量 (十亿桶)", "col_prod": "日产量 (百万桶)", "col_global_share": "全球占比"
    },
    'en': {
        # Footer & Pay
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
        "coffee_amount": "Enter Coffee Count",
        
        # Main UI
        "main_title": "🗺️ Don't Cry for Me, Venezuela",
        "main_subtitle": "Data map showing if US interest is driven by Drugs or Oil",
        
        # Expander 1: Drugs
        "exp1_title": "💊 US Drug Import Sources & Transit (Cocaine & Fentanyl)",
        "drug_select": "Select Drug Type",
        "opt_cocaine": "Cocaine",
        "opt_fentanyl": "Fentanyl",
        "insight_cocaine": "> **Key Insight**: 90% of Cocaine enters the US via **Mexico**, while **Venezuela** accounts for ~10%.\n> Colombia is the primary source.",
        "insight_fentanyl": "> **Key Insight**: Fentanyl is mainly synthesized by **Mexican** cartels with precursors from Asia.\n> **Venezuela** has almost **no role** in the Fentanyl supply chain.",
        "chart1_title": "Cocaine Flow to US: Source & Transit Heatmap",
        "chart1_label": "Flow Impact Factor (%)",
        "chart2_title": "Fentanyl Supply Risk Map (US Market)",
        "chart2_label": "Supply Risk Index",
        "tab_caption_flow": "📊 Data Details (Sorted by Impact)",
        "tab_caption_risk": "📊 Risk Data Details",

        # Data Labels (Drugs)
        "role_primary_src": "Primary Source", "role_src": "Source", "role_transit_core": "Primary Transit", "role_transit_sec": "Secondary Transit", "role_transit": "Transit", "role_dest": "Destination",
        "rank_src_1": "Source #1", "rank_src_2": "Source #2", "rank_src_3": "Source #3", "rank_trans_1": "Transit #1", "rank_trans_2": "Transit #2", "rank_trans_3": "Transit #3",
        "role_syn": "Primary Synthesis", "role_pre": "Precursor Source", "role_none": "No Major Link", "role_minor": "Minor Source",
        "det_syn": "Finished Product Source", "det_pre": "Raw Material Source", "det_cons": "Consumer", "det_none": "No Production Record", "det_smug": "Minor Trafficking",

        # Expander 2: Oil
        "exp2_title": "🛢️ Global Oil: Production vs Reserves",
        "view_mode": "View Mode",
        "opt_reserves": "Proven Reserves",
        "opt_prod": "Daily Production",
        "insight_reserves": "💡 **Venezuela** holds the world's #1 oil reserves (~19%), but mostly untapped due to infrastructure.",
        "insight_prod": "⚠️ Despite #1 reserves, **Venezuela's** production ranks ~20th. The **US** is the world's largest producer.",
        "chart3_title": "Global Oil Reserves Distribution",
        "chart3_label": "Reserves (Bn Barrels)",
        "chart4_title": "Global Oil Daily Production",
        "chart4_label": "Production (Mn BPD)",
        "tab_caption_res": "📊 Top Reserves Ranking",
        "tab_caption_prod": "📊 Top Production Ranking",
        
        # Table Columns
        "col_country": "Country", "col_role": "Role", "col_rank": "Rank", "col_share": "Share", "col_risk": "Risk Index", 
        "col_reserves": "Reserves (Bn bbl)", "col_prod": "Production (Mn bpd)", "col_global_share": "Global Share"
    }
}
# 辅助函数：获取当前语言文本
def get_txt(key):
    return lang_texts[st.session_state.language].get(key, key)

# ==========================================
# 5. 右上角功能区 (保留原样)
# ==========================================
col_empty, col_lang, col_more = st.columns([0.7, 0.1, 0.2])
with col_lang:
    # 按钮显示 "中" 或 "En"
    l_btn = "En" if st.session_state.language == 'zh' else "中"
    if st.button(l_btn, key="lang_switch"):
        st.session_state.language = 'en' if st.session_state.language == 'zh' else 'zh'
        st.rerun()

with col_more:
    st.markdown("""
        <a href="https://laodeng.streamlit.app/" target="_blank" class="neal-btn-link">
            <button class="neal-btn">✨ More Apps</button>
        </a>""", unsafe_allow_html=True)


# ==========================================
# 核心功能区 (已解锁)
# ==========================================
st.divider()
st.title(get_txt("main_title"))
st.write(get_txt("main_subtitle"))

# --- 功能函数：在地图上添加文本标签 ---
def add_map_labels(fig, df, lat_col='lat', lon_col='lon', text_col='Label_Text', color='#333333', size=9):
    fig.add_trace(go.Scattergeo(
        lon=df[lon_col],
        lat=df[lat_col],
        text=df[text_col],
        mode='text',
        showlegend=False,
        textfont=dict(size=size, color=color, family="Arial Black"),
        hoverinfo='skip'
    ))
    return fig

# ----------------------------------------------------
# 模块 1: 美国毒品进口来源 (Cocaine & Fentanyl)
# ----------------------------------------------------
with st.expander(get_txt("exp1_title"), expanded=True):
    drug_option = st.radio(get_txt("drug_select"), ["Cocaine", "Fentanyl"], format_func=lambda x: get_txt("opt_cocaine") if x == "Cocaine" else get_txt("opt_fentanyl"), horizontal=True)

    if drug_option == "Cocaine":
        st.markdown(get_txt("insight_cocaine"))
        
        # 动态生成数据 (使用字典中的文本)
        data_cocaine = {
            "Country": ["Colombia", "Peru", "Bolivia", "Mexico", "Venezuela", "Ecuador", "United States"],
            "Role": [get_txt("role_primary_src"), get_txt("role_src"), get_txt("role_src"), get_txt("role_transit_core"), get_txt("role_transit_sec"), get_txt("role_transit"), get_txt("role_dest")],
            "Flow_Share": [90, 20, 10, 90, 10, 35, 0],
            "Rank": [get_txt("rank_src_1"), get_txt("rank_src_2"), get_txt("rank_src_3"), get_txt("rank_trans_1"), get_txt("rank_trans_3"), get_txt("rank_trans_2"), "-"],
            "lat": [4.57, -9.19, -16.29, 23.63, 6.42, -1.83, 37.09],
            "lon": [-74.30, -75.01, -63.58, -102.55, -66.59, -78.18, -95.71]
        }
        df_c = pd.DataFrame(data_cocaine)
        df_c['Label_Text'] = df_c.apply(lambda x: f"{x['Country']}\n({x['Flow_Share']}%)" if x['Flow_Share'] > 0 else x['Country'], axis=1)

        col_map, col_table = st.columns([2, 1], gap="medium")

        with col_map:
            fig1 = px.choropleth(
                df_c, locations="Country", locationmode="country names",
                color="Flow_Share", 
                hover_name="Country",
                hover_data={"Role": True, "Rank": True, "Flow_Share": ":.0f%", "lat":False, "lon":False, "Label_Text":False},
                color_continuous_scale="Oranges",
                labels={"Flow_Share": get_txt("chart1_label")},
                title=get_txt("chart1_title")
            )
            fig1 = add_map_labels(fig1, df_c)
            fig1.update_geos(fitbounds="locations", visible=True)
            fig1.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, height=450)
            st.plotly_chart(fig1, use_container_width=True)

        with col_table:
            st.caption(get_txt("tab_caption_flow"))
            df_display = df_c[['Country', 'Role', 'Rank', 'Flow_Share']].sort_values(by='Flow_Share', ascending=False)
            df_display['Flow_Share'] = df_display['Flow_Share'].apply(lambda x: f"{x}%")
            st.dataframe(
                df_display, hide_index=True, use_container_width=True,
                column_config={
                    "Country": get_txt("col_country"),
                    "Role": get_txt("col_role"),
                    "Rank": get_txt("col_rank"),
                    "Flow_Share": get_txt("col_share")
                }
            )

    else:
        st.markdown(get_txt("insight_fentanyl"))
        
        data_fentanyl = {
            "Country": ["Mexico", "China", "United States", "Venezuela", "Canada"],
            "Role": [get_txt("role_syn"), get_txt("role_pre"), get_txt("role_dest"), get_txt("role_none"), get_txt("role_minor")],
            "Risk_Score": [95, 60, 0, 1, 5], 
            "Details": [get_txt("det_syn"), get_txt("det_pre"), get_txt("det_cons"), get_txt("det_none"), get_txt("det_smug")],
            "lat": [23.63, 35.86, 37.09, 6.42, 56.13],
            "lon": [-102.55, 104.19, -95.71, -66.59, -106.34]
        }
        df_f = pd.DataFrame(data_fentanyl)
        df_f['Label_Text'] = df_f.apply(lambda x: f"{x['Country']}\n(Risk:{x['Risk_Score']})", axis=1)

        col_map, col_table = st.columns([2, 1], gap="medium")

        with col_map:
            fig2 = px.choropleth(
                df_f, locations="Country", locationmode="country names",
                color="Risk_Score",
                hover_name="Country",
                hover_data={"Role": True, "Details": True, "lat":False, "lon":False, "Label_Text":False},
                color_continuous_scale="Reds",
                labels={"Risk_Score": get_txt("chart2_label")},
                title=get_txt("chart2_title")
            )
            fig2 = add_map_labels(fig2, df_f)
            fig2.update_geos(fitbounds="locations", visible=True)
            fig2.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, height=450)
            st.plotly_chart(fig2, use_container_width=True)

        with col_table:
            st.caption(get_txt("tab_caption_risk"))
            df_display_f = df_f[['Country', 'Role', 'Risk_Score']].sort_values(by='Risk_Score', ascending=False)
            st.dataframe(
                df_display_f, hide_index=True, use_container_width=True,
                column_config={
                    "Country": get_txt("col_country"),
                    "Role": get_txt("col_role"),
                    "Risk_Score": st.column_config.ProgressColumn(
                        get_txt("col_risk"),
                        format="%d", min_value=0, max_value=100,
                    )
                }
            )

# ----------------------------------------------------
# 模块 2: 全球石油产量 vs 储量
# ----------------------------------------------------
with st.expander(get_txt("exp2_title"), expanded=True):
    view_mode = st.radio(get_txt("view_mode"), ["Reserves", "Production"], format_func=lambda x: get_txt("opt_reserves") if x == "Reserves" else get_txt("opt_prod"), horizontal=True)
    
    data_oil = {
        "Country": ["Venezuela", "Saudi Arabia", "United States", "Canada", "Iran", "Iraq", "Russia", "China", "UAE", "Kuwait", "Brazil"],
        "Reserves_Billion_Barrels": [303, 267, 68, 171, 208, 145, 107, 26, 111, 101, 13],
        "Production_Million_BPD": [1.1, 9.0, 13.3, 4.8, 3.2, 4.3, 9.5, 4.2, 3.0, 2.5, 3.5],
        "Reserves_Rank": [1, 2, 9, 3, 4, 5, 6, 13, 7, 8, 15],
        "Production_Rank": [20, 2, 1, 4, 8, 6, 3, 5, 7, 9, 8],
        "lat": [6.42, 23.88, 37.09, 56.13, 32.42, 33.22, 61.52, 35.86, 23.42, 29.31, -14.23],
        "lon": [-66.59, 45.07, -95.71, -106.34, 53.68, 43.67, 105.31, 104.19, 53.84, 47.48, -51.92]
    }
    df_oil = pd.DataFrame(data_oil)
    
    total_reserves = df_oil["Reserves_Billion_Barrels"].sum() * 1.2
    total_prod = df_oil["Production_Million_BPD"].sum() * 1.3
    
    df_oil["Reserves_Share"] = (df_oil["Reserves_Billion_Barrels"] / total_reserves) * 100
    df_oil["Production_Share"] = (df_oil["Production_Million_BPD"] / total_prod) * 100

    col_map_oil, col_table_oil = st.columns([2, 1], gap="medium")

    if view_mode == "Reserves":
        with col_map_oil:
            st.info(get_txt("insight_reserves"))
            df_oil['Label_Text'] = df_oil.apply(lambda x: f"{x['Country']}\n({x['Reserves_Billion_Barrels']} Bn)", axis=1)
            
            fig3 = px.choropleth(
                df_oil, locations="Country", locationmode="country names",
                color="Reserves_Billion_Barrels",
                hover_name="Country",
                hover_data={"Reserves_Rank": True, "Reserves_Share": ":.1f%", "Production_Rank": True, "lat":False, "lon":False, "Label_Text":False},
                color_continuous_scale="Viridis",
                labels={"Reserves_Billion_Barrels": get_txt("chart3_label")},
                title=get_txt("chart3_title")
            )
            fig3 = add_map_labels(fig3, df_oil)
            fig3.update_geos(fitbounds="locations", visible=True)
            fig3.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, height=500)
            st.plotly_chart(fig3, use_container_width=True)
        
        with col_table_oil:
            st.caption(get_txt("tab_caption_res"))
            df_display_oil = df_oil[['Reserves_Rank', 'Country', 'Reserves_Billion_Barrels', 'Reserves_Share']].sort_values(by='Reserves_Rank')
            st.dataframe(
                df_display_oil, hide_index=True, use_container_width=True,
                column_config={
                    "Reserves_Rank": get_txt("col_rank"),
                    "Country": get_txt("col_country"),
                    "Reserves_Billion_Barrels": st.column_config.NumberColumn(get_txt("col_reserves"), format="%d"),
                    "Reserves_Share": st.column_config.NumberColumn(get_txt("col_global_share"), format="%.1f%%")
                }
            )
        
    else:
        with col_map_oil:
            st.warning(get_txt("insight_prod"))
            df_oil['Label_Text'] = df_oil.apply(lambda x: f"{x['Country']}\n({x['Production_Million_BPD']} M)", axis=1)

            fig4 = px.choropleth(
                df_oil, locations="Country", locationmode="country names",
                color="Production_Million_BPD",
                hover_name="Country",
                hover_data={"Production_Rank": True, "Production_Share": ":.1f%", "Reserves_Rank": True, "lat":False, "lon":False, "Label_Text":False},
                color_continuous_scale="Plasma",
                labels={"Production_Million_BPD": get_txt("chart4_label")},
                title=get_txt("chart4_title")
            )
            fig4 = add_map_labels(fig4, df_oil, color='#ffffff')
            fig4.update_geos(fitbounds="locations", visible=True)
            fig4.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, height=500)
            st.plotly_chart(fig4, use_container_width=True)

        with col_table_oil:
            st.caption(get_txt("tab_caption_prod"))
            df_display_prod = df_oil[['Production_Rank', 'Country', 'Production_Million_BPD', 'Production_Share']].sort_values(by='Production_Rank')
            st.dataframe(
                df_display_prod, hide_index=True, use_container_width=True,
                column_config={
                    "Production_Rank": get_txt("col_rank"),
                    "Country": get_txt("col_country"),
                    "Production_Million_BPD": st.column_config.NumberColumn(get_txt("col_prod"), format="%.1f"),
                    "Production_Share": st.column_config.NumberColumn(get_txt("col_global_share"), format="%.1f%%")
                }
            )


# ==========================================
# 8. 咖啡
