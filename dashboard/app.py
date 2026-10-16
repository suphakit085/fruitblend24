"""FruitBlend24 — Dashboard ประกอบกรณีศึกษา Data Analyst."""

from html import escape
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_model import DATA_PATH, SCENARIO_NAMES, load_tables, month_label, simulate_price, summarize

st.set_page_config(page_title="FruitBlend24 · Business Dashboard", page_icon="🍊", layout="wide")
st.markdown(f"<style>{Path(__file__).with_name('styles.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

ORANGE, GREEN, RED, MUTED = "#E56A2C", "#315E49", "#B64D36", "#BAC4B9"
PAGES = ["ภาพรวมธุรกิจ", "เมนูและครัว", "ราคาและโปรโมชัน", "แผน 3 เดือน", "ข้อมูลและวิธีคิด"]


@st.cache_data(show_spinner=False)
def cached_tables(modified_time):
    return load_tables()


def money(value):
    return f"{value:,.0f}"


def section(title, note=""):
    st.markdown(f'<div class="section-label">{escape(title)}</div><div class="section-note">{escape(note)}</div>', unsafe_allow_html=True)


def cards(items):
    blocks = []
    for title, value, unit, note, tone in items:
        blocks.append(f'<div class="kpi {tone}"><div class="kpi-label">{escape(title)}</div>'
                      f'<div class="kpi-value">{escape(value)}<span class="kpi-unit">{escape(unit)}</span></div>'
                      f'<div class="kpi-note">{escape(note)}</div></div>')
    st.markdown('<div class="kpi-grid">' + ''.join(blocks) + '</div>', unsafe_allow_html=True)


def insight(text):
    st.markdown(f'<div class="insight">{escape(text)}</div>', unsafe_allow_html=True)


def action(tag, title, body):
    st.markdown(f'<div class="action"><div class="action-tag">{escape(tag)}</div>'
                f'<div class="action-title">{escape(title)}</div><div class="action-body">{escape(body)}</div></div>', unsafe_allow_html=True)


def plot(fig, key, height=330):
    fig.update_layout(height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      margin=dict(l=10, r=24, t=22, b=10), font=dict(family="Tahoma, sans-serif", size=12, color="#67746B"),
                      legend=dict(orientation="h", y=1.17, x=0, font=dict(size=11)),
                      hoverlabel=dict(bgcolor="white", font_size=13), separators=".,")
    fig.update_xaxes(showgrid=False, zeroline=False, automargin=True)
    fig.update_yaxes(gridcolor="#EFF0E9", zerolinecolor="#C4CCBF", automargin=True)
    st.plotly_chart(fig, width="stretch", key=key, config={"displayModeBar": False, "scrollZoom": False})


def bar_chart(frame, label, value, key, unit="บาท", color_by_sign=True):
    data = frame.sort_values(value)
    colors = np.where(data[value] < 0, RED, GREEN) if color_by_sign else ORANGE
    fig = go.Figure(go.Bar(x=data[value], y=data[label], orientation="h", marker_color=colors,
                          text=[money(v) for v in data[value]], textposition="outside", cliponaxis=False,
                          hovertemplate="%{y}<br>%{x:,.0f} " + unit + "<extra></extra>"))
    fig.update_xaxes(title=unit, tickformat=",.0f")
    low, high = min(data[value].min(), 0), max(data[value].max(), 0)
    span = max(high - low, 1)
    fig.update_xaxes(range=[low - span * .18, high + span * .26])
    plot(fig, key, 340)


def detail_table(frame, filename):
    st.dataframe(frame, hide_index=True, width="stretch")
    st.download_button("ดาวน์โหลดตาราง CSV", frame.to_csv(index=False).encode("utf-8-sig"),
                       file_name=filename, mime="text/csv", key=filename)


try:
    tables = cached_tables(DATA_PATH.stat().st_mtime_ns)
except (OSError, ValueError, KeyError) as error:
    st.error("เปิดข้อมูลไม่ได้ กรุณาตรวจไฟล์ data/FruitBlend24_Analysis_Results.xlsx")
    st.caption(str(error))
    st.stop()

monthly = tables["Monthly_PnL"].sort_values("month")
summary = tables["Summary"].set_index("metric")["value"]

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">f</div><div><div class="brand-name">fruitblend<span style="color:#e56a2c">24</span></div><div class="brand-sub">BUSINESS INTELLIGENCE</div></div></div>', unsafe_allow_html=True)
    st.caption("พื้นที่วิเคราะห์")
    page = st.radio("เลือกมุมมอง", PAGES, label_visibility="collapsed")
    st.divider()
    if page == "ภาพรวมธุรกิจ":
        labels = monthly["เดือน"].tolist()
        selected_months = st.select_slider("ช่วงผลประกอบการ", options=labels, value=(labels[0], labels[-1]))
        first = monthly.loc[monthly["เดือน"] == selected_months[0], "month"].iloc[0]
        last = monthly.loc[monthly["เดือน"] == selected_months[1], "month"].iloc[0]
        selected = monthly[monthly["month"].between(first, last)]
        st.caption("ตัวกรองนี้ใช้กับทุกตัวเลขและกราฟในหน้าภาพรวม")
    st.markdown('<div class="sidebar-note"><b>กรณีศึกษา FruitBlend24</b><br>ข้อมูลจำลองจากแบบทดสอบบริษัท<br>ผลจริง ก.ย. 2025 – ส.ค. 2026<br>ประมาณการ ก.ย. – พ.ย. 2026<br><br>จัดทำโดย ศุภกฤต แก้วแกมทอง</div>', unsafe_allow_html=True)
    st.download_button("↓  ผลวิเคราะห์ Excel", DATA_PATH.read_bytes(), file_name=DATA_PATH.name,
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")

subtitles = {
    PAGES[0]: "มองรายได้ กำไร และต้นทุนร่วมกัน เพื่อเลือกจุดที่ควรแก้ก่อน",
    PAGES[1]: "รักษาเมนูที่สร้างกำไร และเจาะจุดที่ของเสียหรือค่าใช้จ่ายกดผลประกอบการ",
    PAGES[2]: "ทดสอบแนวคิดเรื่องราคา และดูว่าโปรโมชันสร้างเงินเหลือเพิ่มหรือไม่",
    PAGES[3]: "เตรียมพร้อมสำหรับความต้องการขาย พร้อมเห็นช่องว่างก่อนถึงจุดคุ้มทุน",
    PAGES[4]: "ที่มาของตัวเลข นิยาม และข้อจำกัดที่ใช้ประกอบการตัดสินใจ",
}
st.markdown('<div class="topline"><div class="eyebrow">FRUITBLEND24 / DECISION DASHBOARD</div><div class="status">●  CASE STUDY · ข้อมูลจำลอง</div></div>', unsafe_allow_html=True)
st.markdown(f'<h1 class="page-title">{page}</h1><div class="subtitle">{subtitles[page]}</div>', unsafe_allow_html=True)

if page == PAGES[0]:
    metrics = summarize(selected)
    budget = tables["Budget_vs_Actual"]
    budget = budget[budget["month"].between(first, last)].sort_values("month")
    period = f"{month_label(first)} – {month_label(last)}"
    achieved = ((budget["gross_revenue_thb"] >= budget["budget_revenue_thb"]) &
                (budget["gross_profit_thb"] >= budget["budget_gross_profit_thb"])).sum()
    cards([
        ("รายได้รวม", money(metrics["revenue"]), "บาท", f'{money(metrics["units"])} แก้ว · {len(selected)} เดือน', "dark"),
        ("กำไรขั้นต้น", money(metrics["gp"]), "บาท", f'หลังหักของเสีย · อัตรากำไร {metrics["margin"]:.1%}', ""),
        ("กำไร / ขาดทุนดำเนินงาน", money(metrics["op"]), "บาท", "หลังหักค่าใช้จ่ายประจำแล้ว", "negative" if metrics["op"] < 0 else "positive"),
    ])
    left, right = st.columns([2.05, 1], gap="large")
    with left:
        with st.container(border=True):
            section("รายได้ถึงเป้าหมายหรือยัง", f"{period} · หน่วยล้านบาท")
            fig = go.Figure()
            fig.add_scatter(x=budget["เดือน"], y=budget["gross_revenue_thb"] / 1e6, name="รายได้จริง", mode="lines+markers",
                            line=dict(color=ORANGE, width=3), marker=dict(size=6), fill="tozeroy", fillcolor="rgba(229,106,44,.08)",
                            hovertemplate="%{x}<br>รายได้ %{y:.3f} ล้านบาท<extra></extra>")
            fig.add_scatter(x=budget["เดือน"], y=budget["budget_revenue_thb"] / 1e6, name="เป้าหมาย", mode="lines",
                            line=dict(color="#9CAB9B", dash="dash", width=2), hovertemplate="เป้าหมาย %{y:.2f} ล้านบาท<extra></extra>")
            fig.update_yaxes(rangemode="tozero", tickformat=".1f")
            plot(fig, "revenue")
        with st.container(border=True):
            section("รายได้เหลือเป็นกำไรเท่าไร", f"เส้นทางจากรายได้ถึงกำไรดำเนินงาน · {period} · ล้านบาท")
            costs = selected[["commission_thb", "fruit_cost_thb", "packaging_cost_thb", "labor_cost_thb"]].sum().sum()
            fig = go.Figure(go.Waterfall(
                x=["รายได้", "ต้นทุนขาย¹", "ของเสีย", "กำไรขั้นต้น", "ค่าใช้จ่ายประจำ", "กำไรดำเนินงาน"],
                measure=["absolute", "relative", "relative", "total", "relative", "total"],
                y=np.array([metrics["revenue"], -costs, -metrics["waste"], 0, -selected["fixed_overhead_thb"].sum(), 0]) / 1e6,
                text=[f'{v / 1e6:,.2f}' for v in [metrics["revenue"], -costs, -metrics["waste"], metrics["gp"], -selected["fixed_overhead_thb"].sum(), metrics["op"]]],
                textposition="outside", decreasing=dict(marker_color="#D8BCA7"), increasing=dict(marker_color=ORANGE),
                totals=dict(marker_color=GREEN), connector=dict(line=dict(color="#DDDCD2", width=1)),
                hovertemplate="%{x}<br>%{text} ล้านบาท<extra></extra>"))
            plot(fig, "bridge", 300)
            st.caption("¹ รวมค่าคอมมิชชัน ผลไม้ บรรจุภัณฑ์ และแรงงาน")
    with right:
        with st.container(border=True):
            section("สิ่งที่ตัวเลขบอก", period)
            action("01 / BUDGET", f"ถึงเป้าพร้อมกัน {achieved} จาก {len(selected)} เดือน", "นับเดือนที่ทั้งรายได้และกำไรขั้นต้นไม่น้อยกว่าเป้าหมาย")
            gap = metrics["revenue"] - budget["budget_revenue_thb"].sum()
            action("02 / REVENUE GAP", f'{"ต่ำกว่า" if gap < 0 else "สูงกว่า"}เป้ารายได้ {money(abs(gap))} บาท', "คำนวณจากผลรวมช่วงเดือนที่เลือก")
            action("03 / WASTE", f'ต้นทุนของเสีย {money(metrics["waste"])} บาท', "ติดตามของเสียควบคู่กับกำไร เพื่อประเมินปริมาณที่ควรเตรียม")
            action("04 / NEXT STEP", "ตรวจค่าใช้จ่ายประจำและส่วนผสมยอดขาย", "เปิดหน้าเมนูและครัว เพื่อดูผลตลอดช่วงข้อมูลและจุดที่ควรตรวจต่อ")
        with st.container(border=True):
            section("กำไรขั้นต้นเทียบเป้า", "ล้านบาท · ช่วงเดียวกับกราฟรายได้")
            fig = go.Figure()
            fig.add_bar(x=budget["เดือน"], y=budget["gross_profit_thb"] / 1e6, marker_color=GREEN, name="กำไรขั้นต้น")
            fig.add_scatter(x=budget["เดือน"], y=budget["budget_gross_profit_thb"] / 1e6, mode="lines", line=dict(color=ORANGE, dash="dash"), name="เป้า")
            fig.update_layout(showlegend=False)
            fig.update_yaxes(rangemode="tozero")
            plot(fig, "gp-budget", 230)
            st.caption("แท่งเขียว = กำไรขั้นต้น · เส้นส้ม = เป้าหมาย")
    with st.expander("ดูตัวเลขรายเดือนและดาวน์โหลด"):
        detail_table(budget[["เดือน", "gross_revenue_thb", "gross_profit_thb", "operating_profit_thb", "budget_revenue_thb", "budget_gross_profit_thb"]]
                     .rename(columns={"gross_revenue_thb": "รายได้ (บาท)", "gross_profit_thb": "กำไรขั้นต้น (บาท)", "operating_profit_thb": "กำไรดำเนินงาน (บาท)", "budget_revenue_thb": "เป้ารายได้ (บาท)", "budget_gross_profit_thb": "เป้ากำไรขั้นต้น (บาท)"}).round(2), "monthly_performance.csv")

elif page == PAGES[1]:
    view = st.radio("ดูผลประกอบการตาม", ["เมนู", "ครัว"], horizontal=True)
    st.caption("ผลรวม ก.ย. 2025 – ส.ค. 2026 · Mixed Berry เริ่มขาย มี.ค. 2026")
    frame = tables["SKU_PnL" if view == "เมนู" else "Kitchen_PnL"]
    label = "เมนู" if view == "เมนู" else "ครัว"
    metric = "gross_profit_thb" if view == "เมนู" else "operating_profit_thb"
    metric_name = "กำไรขั้นต้น" if view == "เมนู" else "กำไรดำเนินงาน"
    with st.container(border=True):
        section(f"{view}ไหนสร้างกำไร", "เขียว = กำไร · อิฐ = ขาดทุน · แสดงครบทุก" + view)
        bar_chart(frame, label, metric, "portfolio")
    choice = st.selectbox(f"เจาะรายละเอียด{view}", frame[label].tolist())
    row = frame.loc[frame[label] == choice].iloc[0]
    cards([
        (f"รายได้ · {choice}", money(row["gross_revenue_thb"]), "บาท", f'{money(row["units_sold"])} แก้ว', "dark"),
        (metric_name, money(row[metric]), "บาท", "หักของเสียแล้ว" if view == "เมนู" else "หักของเสียและค่าใช้จ่ายประจำแล้ว", "negative" if row[metric] < 0 else "positive"),
        ("อัตราของเสีย", f'{row["waste_rate_pct"]:.1%}', "ของแก้วขายและทิ้ง", f'ต้นทุนของเสีย {money(row["waste_cost_thb"])} บาท', ""),
    ])
    if view == "เมนู" and row["sku"] == "MixedBerryPremium":
        share = row["waste_cost_thb"] / frame["waste_cost_thb"].sum()
        insight(f'Mixed Berry มีต้นทุนของเสีย {share:.1%} ของต้นทุนของเสียรวม ส่วนอัตราของเสีย {row["waste_rate_pct"]:.1%} ใช้จำนวนแก้วขายและทิ้งเป็นฐาน ควรลดการเตรียมและทดลองราคา')
    actions = tables["Kitchen_SKU_Actions"]
    actions = actions[actions[label] == choice]
    with st.container(border=True):
        section("จุดที่ควรตรวจต่อ", "มี.ค. – ส.ค. 2026 เท่านั้น · ช่วง 6 เดือนนี้ต่างจากกราฟรวมด้านบน")
        action_names = {
            "Reduce preparation and review price/cost": "ลดเตรียมและทบทวนราคา/ต้นทุน",
            "Reduce preparation and ordering level": "ลดปริมาณเตรียมและสั่งซื้อ",
            "Review price, recipe cost, or assortment": "ทบทวนราคา ต้นทุนสูตร หรือเมนู",
            "Protect availability and monitor stockouts": "รักษาของพร้อมขายและติดตามของขาด",
            "Maintain and monitor": "รักษาระดับและติดตาม",
        }
        detail = actions[["เมนู", "ครัว", "gross_profit_thb", "waste_rate_pct", "priority", "recommended_action"]].copy()
        detail["waste_rate_pct"] = (detail["waste_rate_pct"] * 100).round(1)
        detail["recommended_action"] = detail["recommended_action"].map(action_names)
        detail["priority"] = detail["priority"].map({"High": "สูง", "Medium": "กลาง", "Low": "ต่ำ"})
        detail_table(detail.rename(columns={"gross_profit_thb": "กำไรขั้นต้น (บาท)", "waste_rate_pct": "ของเสีย (%)", "priority": "เร่งด่วน", "recommended_action": "แนวทางตรวจต่อ"}).round(2), "portfolio_actions.csv")
        st.caption("ระดับเร่งด่วนเป็นกฎคัดกรอง ไม่ใช่ผลรับรองว่าการปรับจะเพิ่มกำไร")

elif page == PAGES[2]:
    left, right = st.columns([1, 1], gap="large")
    with left:
        with st.container(border=True):
            section("ลองปรับราคา", "แบบจำลองจากรายการราคาปกติ · ยังไม่หักของเสียและค่าใช้จ่ายประจำ")
            pricing = tables["Pricing"]
            menu = st.selectbox("เลือกเมนู", pricing["เมนู"].tolist())
            row = pricing.loc[pricing["เมนู"] == menu].iloc[0]
            price_period = "มี.ค. – ส.ค. 2026" if row["sku"] == "MixedBerryPremium" else "ก.ย. 2025 – ส.ค. 2026"
            st.caption(f'ฐาน {price_period} · รายการราคาปกติ {money(row["standard_units"])} แก้ว')
            increase = st.slider("ขึ้นราคา (%)", 0, 15, 5)
            loss = st.slider("คาดว่าจำนวนแก้วจะลด (%)", 0, 40, 2)
            result = simulate_price(row, increase, loss)
            fig = go.Figure(go.Bar(x=["ราคาปัจจุบัน", "ราคาทดลอง"], y=[row["current_contribution_per_cup_thb"], result["contribution"]],
                                   marker_color=[MUTED, ORANGE], text=[f'{row["current_contribution_per_cup_thb"]:.2f}', f'{result["contribution"]:.2f}'], textposition="outside"))
            fig.update_yaxes(title="เงินเหลือหลังต้นทุนขาย (บาท/แก้ว)", rangemode="tozero")
            plot(fig, "price", 300)
            a, b = st.columns(2)
            a.metric("ราคาทดลอง / แก้ว", f'{result["price"]:.2f} บาท')
            b.metric("เงินเหลือรวมเปลี่ยนแปลง", f'{result["difference"]:+,.0f} บาท')
            insight(f'จำนวนแก้วลดได้ไม่เกิน {result["breakeven_loss"]:.1%} ก่อนเงินเหลือรวมจะต่ำกว่าเดิม ภายใต้ต้นทุนต่อแก้วและอัตราคอมมิชชันเดิม')
            st.caption("ผลรวมใช้จำนวนแก้วราคาปกติในประวัติของเมนูที่เลือก ไม่ใช่กำไรคาดการณ์ 3 เดือน และยังไม่มีข้อมูล Price elasticity")
    with right:
        with st.container(border=True):
            section("โปรโมชันเพิ่มเงินเหลือหรือไม่", "เทียบรายการที่มีเงื่อนไขใกล้กัน · ก.ย. 2025 – ส.ค. 2026")
            promo = tables["Promotions"].copy()
            promo["โปรโมชัน"] = promo["rate_code_name"].replace({"Double Day New User": "Double Day"})
            bar_chart(promo, "โปรโมชัน", "incremental_contribution_thb", "promotions")
            insight("ทั้ง 3 โปรโมชันมีเงินเหลือหลังต้นทุนขายต่ำกว่ากลุ่มเปรียบเทียบในรายการที่จับคู่ได้ ควรทบทวน Seasonal Push ก่อนใช้ต่อ")
            detail = promo[["โปรโมชัน", "match_coverage_pct", "units_lift_pct"]].copy()
            detail[["match_coverage_pct", "units_lift_pct"]] *= 100
            st.dataframe(detail.rename(columns={"match_coverage_pct": "จับคู่ได้ (%)", "units_lift_pct": "แก้วเพิ่มในคู่เทียบ (%)"}).round(1), hide_index=True, width="stretch")
            st.caption("จับคู่ตามเมนู ครัว แพลตฟอร์ม วันในสัปดาห์ และชั่วโมง ครอบคลุมเพียง 41–45% ของรายการโปรโมชัน ยังยืนยันเหตุและผลไม่ได้")
        with st.container(border=True):
            section("ข้อเสนอเริ่มต้น")
            action("PRICE", "เริ่มทดลอง Mixed Berry ก่อน", "แตงโมและสับปะรดคงราคา ฝรั่งติดตามกำไร เสาวรสลดของเสียและต้นทุนก่อน")
            action("PROMOTION", "ทดลองเล็กและวัดเงินเหลือรวม", "ติดตามจำนวนแก้วควบคู่กับเงินเหลือหลังต้นทุนขาย ก่อนขยายราคาและแคมเปญ")

elif page == PAGES[3]:
    scenario = st.selectbox("สมมติฐานประมาณการ", list(SCENARIO_NAMES), format_func=SCENARIO_NAMES.get)
    pnl = tables["Forecast_PnL"]
    forecast = pnl[pnl["scenario"] == scenario].sort_values("month")
    base_op = pnl.loc[pnl["scenario"] == "Base", "operating_profit_thb"].sum()
    op = forecast["operating_profit_thb"].sum()
    cards([
        ("จำนวนแก้วคาดการณ์", money(forecast["units"].sum()), "แก้ว", "ก.ย. – พ.ย. 2026 · รวม 3 เดือน", "dark"),
        ("กำไร / ขาดทุนคาดการณ์", money(op), "บาท", SCENARIO_NAMES[scenario], "negative" if op < 0 else "positive"),
        ("กำไรเปลี่ยนจากกรณีเดิม", f"{op - base_op:+,.0f}", "บาท", "เทียบดำเนินงานแบบเดิมในช่วงเดียวกัน", ""),
    ])
    notes = {"Base": "ใช้ประมาณการเดิม โดยยังไม่ปรับราคาและของเสีย",
             "Action plan": "Mixed Berry ขึ้นราคา 5% แก้วขายลด 2% และลดต้นทุนของเสียเฉพาะ Mixed Berry 20%",
             "Demand -10%": "สมมติจำนวนแก้วขายลด 10% เทียบกรณีเดิม ตามตารางจำลองใน Notebook",
             "Fruit cost +10%": "สมมติต้นทุนผลไม้เพิ่ม 10% ตามตารางจำลองใน Notebook"}
    insight(notes[scenario] + " · เป็นการจำลอง ไม่ใช่ผลทดลองจริง")
    a, b = st.columns(2, gap="large")
    with a, st.container(border=True):
        section("เตรียมรับความต้องการแต่ละเดือน", SCENARIO_NAMES[scenario] + " · หน่วยแก้ว")
        fig = go.Figure(go.Bar(x=forecast["เดือน"], y=forecast["units"], marker_color=["#EAC5A4", ORANGE, "#EAC5A4"],
                              text=[money(v) for v in forecast["units"]], textposition="outside"))
        fig.update_yaxes(rangemode="tozero", tickformat=",.0f")
        plot(fig, "forecast")
        st.caption(f'ใช้ค่าเฉลี่ยตามวันในสัปดาห์จาก 4 สัปดาห์ล่าสุด · WAPE ในชุดทดสอบ {summary["Forecast WAPE"]:.1%}')
    with b, st.container(border=True):
        section("แต่ละสมมติฐานยังห่างจากกำไรเท่าไร", "กำไรดำเนินงานรวม 3 เดือน · บาท")
        totals = pnl.groupby("scenario", as_index=False)["operating_profit_thb"].sum()
        totals["สมมติฐาน"] = totals["scenario"].map(SCENARIO_NAMES)
        bar_chart(totals, "สมมติฐาน", "operating_profit_thb", "scenarios")
    with st.container(border=True):
        section("เป้าพร้อมขายรายครัวและเมนู", "ใช้กรณีฐานเสมอ · รวม safety stock แล้ว · หน่วยแก้วเทียบเท่า ไม่ใช่จำนวนซื้อ")
        inventory = tables["Inventory_Monthly"]
        x, y, z = st.columns(3)
        month = x.selectbox("เดือนที่เตรียม", inventory["เดือน"].drop_duplicates().tolist())
        kitchen = y.selectbox("ครัวที่เตรียม", ["ทุกครัว"] + inventory["ครัว"].drop_duplicates().tolist())
        menu = z.selectbox("เมนูที่เตรียม", ["ทุกเมนู"] + inventory["เมนู"].drop_duplicates().tolist())
        detail = inventory[inventory["เดือน"] == month]
        if kitchen != "ทุกครัว":
            detail = detail[detail["ครัว"] == kitchen]
        if menu != "ทุกเมนู":
            detail = detail[detail["เมนู"] == menu]
        if detail.empty:
            st.info("ไม่มีข้อมูลสำหรับตัวเลือกนี้")
        else:
            detail_table(detail[["ครัว", "เมนู", "forecast_units", "average_daily_target_cups", "peak_daily_target_cups"]]
                         .rename(columns={"forecast_units": "คาดขายทั้งเดือน (แก้ว)", "average_daily_target_cups": "เป้าพร้อมขายเฉลี่ย/วัน", "peak_daily_target_cups": "เป้าพร้อมขายสูงสุด/วัน"}).round(1), "inventory_targets.csv")
        st.caption("จำนวนเติม = เป้าพร้อมขาย − สต็อกที่ใช้ได้ − ของที่จะรับทัน ต้องเก็บสูตรผลิต อายุสินค้า และเวลาส่งก่อนแปลงเป็นวัตถุดิบ เพดาน 2 วันเป็นสมมติฐาน")

else:
    quality = tables["Quality"].set_index("check")["rows"]
    cards([
        ("รายการขายที่ใช้วิเคราะห์", money(quality["Rows retained"]), "แถว", f'จากข้อมูลต้นทาง {money(quality["Raw order rows"])} แถว', "dark"),
        ("รายการที่แยกออก", money(quality["Raw order rows"] - quality["Rows retained"]), "แถว", "ข้อมูลซ้ำ 372 · สินค้านอกเมนู 370", ""),
        ("ยอดขายไม่ตรงสูตร", money(quality["Revenue arithmetic mismatches"]), "แถว", "ตรวจจำนวน × ราคา เทียบรายได้", ""),
    ])
    a, b = st.columns(2, gap="large")
    with a, st.container(border=True):
        section("อ่านตัวเลขด้วยนิยามเดียวกัน")
        st.markdown("""
**รายได้** — จำนวนแก้ว × ราคาหลังส่วนลด ไม่หักส่วนลดซ้ำ

**เงินเหลือหลังต้นทุนขาย (Contribution)** — รายได้หักค่าคอมมิชชัน ผลไม้ บรรจุภัณฑ์ และแรงงาน

**กำไรขั้นต้น (GP)** — Contribution หักต้นทุนของเสีย

**กำไรดำเนินงาน** — กำไรขั้นต้นหักค่าใช้จ่ายประจำ

**อัตราของเสีย** — แก้วทิ้ง ÷ (แก้วขาย + แก้วทิ้ง)

**WAPE** — ผลรวมค่าคลาดเคลื่อนสัมบูรณ์ ÷ ผลรวมยอดขายจริงในชุดทดสอบ
""")
    with b, st.container(border=True):
        section("ขอบเขตที่ต้องรู้ก่อนตัดสินใจ")
        st.markdown("""
- ข้อมูลทั้งหมดเป็น **ข้อมูลจำลอง** จากแบบทดสอบ ไม่ใช่ผลประกอบการปัจจุบันของบริษัท
- ผลจริงครอบคลุม ก.ย. 2025 – ส.ค. 2026 และ Mixed Berry มีข้อมูล 6 เดือน
- มีการเติมต้นทุนผลไม้ 75 แถว และต้นทุนของเสีย 4 แถว รวม 4,002.24 บาท ตาม Notebook
- ราคาและแผนปรับปรุงเป็นสมมติฐาน ต้องทดลองกับลูกค้าจริง
- ผลโปรโมชันเป็นการเทียบรายการใกล้เคียง ไม่ใช่การทดลองสุ่ม
- เป้าสินค้าคงคลังยังไม่ใช่ใบสั่งซื้อ ขาดสูตรผลิต สต็อกจริง อายุสินค้า และเวลาส่ง
""")
    with st.expander("แหล่งข้อมูลและการอัปเดต"):
        st.write("อ่านจาก FruitBlend24_Analysis_Results.xlsx รุ่นหลักที่ใช้ส่งงาน โดยเก็บสำเนาไว้ในโฟลเดอร์ dashboard/data")
        st.write("เป็น snapshot ของกรณีศึกษา ไม่ได้เชื่อมฐานข้อมูลสด อัปเดตได้โดยรัน Notebook ตรวจผล แล้วแทนที่ไฟล์ผลวิเคราะห์ใน dashboard/data")
        st.write("ชีตที่ใช้: Monthly_PnL, Budget_vs_Actual, SKU_PnL, Kitchen_PnL, Pricing, Promotions, Kitchen_SKU_Actions, Forecast_Monthly, Inventory_Monthly, Forecast_PnL, Summary และ Quality")
        st.caption("Python · pandas · NumPy · Plotly · Streamlit")

st.markdown('<div class="source">FRUITBLEND24 · ANALYST CASE STUDY &nbsp; / &nbsp; แหล่งข้อมูล ผลวิเคราะห์ Excel รุ่นหลัก<br>Snapshot ของข้อมูลจำลอง สิ้นสุด ส.ค. 2026 · ตัวเลขแสดงผลปัดเศษเพื่ออ่านง่าย การคำนวณใช้ค่าความละเอียดเดิม</div>', unsafe_allow_html=True)
