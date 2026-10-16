"""ตรวจตัวเลขและเส้นทางใช้งานหลัก ก่อนเปิดนำเสนอ."""
from pathlib import Path

import numpy as np
from streamlit.testing.v1 import AppTest

from data_model import load_tables, simulate_price, summarize

tables = load_tables()
totals = summarize(tables["Monthly_PnL"])
assert np.isclose(totals["revenue"], 31146932.57, atol=.01, rtol=0)
assert np.isclose(totals["op"], -403231.0228, atol=.01, rtol=0)
berry = tables["Pricing"].query("sku == 'MixedBerryPremium'").iloc[0]
unchanged = simulate_price(berry, 0, 0)
assert abs(unchanged["difference"]) < .01
test_price = simulate_price(berry, 5, 0)
assert np.isclose(test_price["contribution"], berry["tested_contribution_per_cup_thb"], atol=1e-8)
assert abs(simulate_price(berry, 5, test_price["breakeven_loss"] * 100)["difference"]) < .01

app = AppTest.from_file(Path(__file__).with_name("app.py"), default_timeout=30).run()
assert not app.exception
assert len(app.get("plotly_chart")) == 3
assert len(app.dataframe[0].value) == 12
app.select_slider[0].set_value(("มี.ค. 2026", "พ.ค. 2026")).run()
assert not app.exception
assert len(app.dataframe[0].value) == 3
assert np.isclose(app.dataframe[0].value["รายได้ (บาท)"].sum(),
                  tables["Monthly_PnL"].iloc[6:9]["gross_revenue_thb"].sum(), atol=.01, rtol=0)

app.sidebar.radio[0].set_value("เมนูและครัว").run()
assert not app.exception
app.selectbox[0].select("Mixed Berry").run()
assert not app.exception
assert len(app.dataframe[0].value) == 4
assert (app.dataframe[0].value["เมนู"] == "Mixed Berry").all()
next(widget for widget in app.radio if widget.label == "ดูผลประกอบการตาม").set_value("ครัว").run()
assert not app.exception
assert len(app.dataframe[0].value) == 5

app.sidebar.radio[0].set_value("ราคาและโปรโมชัน").run()
assert not app.exception
assert len(app.get("plotly_chart")) == 2
app.slider[0].set_value(0)
app.slider[1].set_value(0).run()
assert not app.exception
assert app.metric[1].value == "+0 บาท"

app.sidebar.radio[0].set_value("แผน 3 เดือน").run()
assert not app.exception
for scenario in ["Action plan", "Demand -10%", "Fruit cost +10%", "Base"]:
    app.selectbox[0].select(scenario).run()
    assert not app.exception
    assert len(app.get("plotly_chart")) == 2
app.selectbox[2].select("กรุงเทพฯ · ลาดพร้าว")
app.selectbox[3].select("Mixed Berry").run()
assert not app.exception
assert len(app.dataframe[0].value) == 1

app.sidebar.radio[0].set_value("ข้อมูลและวิธีคิด").run()
assert not app.exception
print("PASS: 5 pages, month/menu/kitchen/inventory filters, 4 forecast scenarios, pricing baseline and break-even, charts and detail tables.")
