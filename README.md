这是一个为您量身定制的 `README.md` 文件模板。它涵盖了项目介绍、功能特性、安装运行步骤以及部署指南。

您可以直接复制以下内容保存为 `README.md` 文件。

---

# 🗺️ Global Insights: Don't Cry for Me, Venezuela

### (数据透视：委内瑞拉的地缘政治悖论)

**English** | [中文说明](https://www.google.com/search?q=%23%E4%B8%AD%E6%96%87%E8%AF%B4%E6%98%8E)

## 📖 Introduction

This interactive data dashboard explores the complex geopolitical relationship between the United States and Venezuela. By visualizing global data on **Drug Trafficking** (Cocaine/Fentanyl) and **Oil Production vs. Reserves**, the application aims to answer a critical question: *Is foreign interest driven by the war on drugs, or the thirst for energy?*

Built with **Streamlit** and **Plotly**, this app features interactive choropleth maps, bilingual support (En/Zh), and a custom access control system.

## ✨ Key Features

* **🌍 Interactive Geopolitics Maps**:
* **Drug Routes**: Visualizes Cocaine trafficking flows and Fentanyl supply risks, highlighting Venezuela's role (or lack thereof).
* **Energy Landscape**: Compares Global Oil Reserves (Venezuela #1) vs. Actual Production, highlighting the infrastructure gap.


* **🇨🇳/🇺🇸 Bilingual Support**: Seamlessly switch between English (default) and Chinese via the top navigation bar.
* **🔒 Access Control System**:
* Includes a "Free Trial" mode (timed access).
* Unlock mechanism with a passcode (Default: `vip24`).


* **☕ "Buy Me a Coffee" Module**: A customized, responsive donation UI supporting WeChat Pay, Alipay, and PayPal (Mockup/Template).
* **📊 Traffic Analytics**: Built-in SQLite tracking for Daily UV (Unique Visitors) and PV (Page Views).

## 🛠️ Installation & Local Run

### Prerequisites

* Python 3.8 or higher
* pip

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/your-username/venezuela-insights.git
cd venezuela-insights

```


2. **Install dependencies**
It is recommended to use a virtual environment.
```bash
pip install -r requirements.txt

```


3. **Run the app**
```bash
streamlit run streamlit_app.py

```


4. **Access the app**
Open your browser and navigate to `http://localhost:8501`.

## 📦 Requirements

Create a `requirements.txt` file with the following content to ensure smooth deployment:

```text
streamlit>=1.30.0
pandas>=2.0.0
plotly>=5.18.0

```

## 🚀 Deployment (Streamlit Cloud)

1. Push your code to a **GitHub** repository.
2. Log in to [Streamlit Cloud](https://streamlit.io/cloud).
3. Click **"New app"** and select your repository, branch, and main file path (`streamlit_app.py`).
4. Click **"Deploy"**. The system will automatically install dependencies from `requirements.txt`.

## 📂 Project Structure

```text
.
├── streamlit_app.py    # Main application entry point
├── requirements.txt    # Python dependencies
├── visit_stats.db      # SQLite database (auto-generated for analytics)
├── assets/             # Images for payment QR codes (optional)
│   ├── wechat_pay.jpg
│   ├── ali_pay.jpg
│   └── paypal.png
└── README.md           # Project documentation

```

## ⚠️ Disclaimer

This project is for educational and data visualization demonstration purposes. The data points used (e.g., specific drug flow percentages) are based on general reports (DEA/OPEC) and simplified for visualization; they should not be cited as primary academic sources.

---

<a name="中文说明"></a>

## 🇨🇳 中文说明

## 📖 简介

这是一个基于 Python Streamlit 开发的交互式数据仪表板，旨在探讨美国与委内瑞拉之间复杂的地缘政治关系。通过可视化**毒品贸易**（可卡因/芬太尼）和**石油储量与产量**的数据，本项目试图通过数据回答一个关键问题：*外部势力的介入究竟是为了禁毒，还是为了能源？*

## ✨ 核心功能

* **🌍 交互式地缘政治地图**：
* **毒品路线**：展示可卡因流向和芬太尼供应风险，并在地图上直接标记关键数据。
* **能源格局**：对比全球石油储量（委内瑞拉世界第一）与实际产量，揭示“储量巨人，产量侏儒”的现状。


* **🇨🇳/🇺🇸 双语支持**：内置完整的国际化方案，默认英文，支持一键切换中文。
* **🔒 访问控制系统**：
* 包含“免费试用”倒计时逻辑。
* 通过验证码解锁完整内容（默认验证码：`vip24`）。


* **☕ 打赏系统 (演示)**：集成了微信支付、支付宝和 PayPal 的 UI 模态框，支持金额计算和二维码展示。
* **📊 流量统计**：内置基于 SQLite 的简易访客统计系统（今日 UV / 历史 UV）。

## 🛠️ 安装与运行

1. **安装依赖**
```bash
pip install -r requirements.txt

```


2. **启动应用**
```bash
streamlit run streamlit_app.py

```



## 📝 注意事项

* **解锁码**：本地测试时，若试用期结束，请输入代码 `vip24` 解锁。
* **支付二维码**：若要让打赏功能生效，请将您的收款码图片放入项目根目录或 `assets` 文件夹，并更新代码中的图片路径。

---

*Created with ❤️ by [Your Name]*
