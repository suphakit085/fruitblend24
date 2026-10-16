"""อ่านผลวิเคราะห์ที่ตรวจแล้ว และเตรียมตัวเลขสำหรับ Dashboard."""

from pathlib import Path

import numpy as np
import pandas as pd

DATA_PATH = Path(__file__).parent / "data" / "FruitBlend24_Analysis_Results.xlsx"
MENU_NAMES = {
    "Watermelon": "แตงโม",
    "Pineapple": "สับปะรด",
    "Guava": "ฝรั่ง",
    "PassionFruit": "เสาวรส",
    "MixedBerryPremium": "Mixed Berry",
}
KITCHEN_NAMES = {
    "BKK_Ladprao": "กรุงเทพฯ · ลาดพร้าว",
    "BKK_Sukhumvit": "กรุงเทพฯ · สุขุมวิท",
    "Pattaya_Beach": "พัทยา · ชายหาด",
    "Pattaya_Central": "พัทยา · กลาง",
}
SCENARIO_NAMES = {
    "Base": "ดำเนินงานแบบเดิม",
    "Action plan": "ปรับราคาและลดของเสีย",
    "Demand -10%": "ยอดขายลด 10%",
    "Fruit cost +10%": "ต้นทุนผลไม้เพิ่ม 10%",
}
MONTHS_TH = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
             "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]


def month_label(value):
    date = pd.Timestamp(value)
    return f"{MONTHS_TH[date.month - 1]} {date.year}"


def load_tables(path=DATA_PATH):
    tables = pd.read_excel(path, sheet_name=None)
    required = {"Summary", "Quality", "Monthly_PnL", "Budget_vs_Actual", "SKU_PnL",
                "Kitchen_PnL", "Pricing", "Promotions", "Kitchen_SKU_Actions",
                "Forecast_Monthly", "Inventory_Monthly", "Forecast_PnL"}
    missing = required.difference(tables)
    if missing:
        raise ValueError(f"ไฟล์ผลวิเคราะห์ขาดชีต {', '.join(sorted(missing))}")
    if any(tables[name].empty for name in required):
        raise ValueError("ชีตที่จำเป็นไม่มีข้อมูล กรุณาตรวจผลวิเคราะห์ก่อนอัปเดต")
    for table in tables.values():
        if "month" in table:
            table["month"] = pd.to_datetime(table["month"])
            table["เดือน"] = table["month"].map(month_label)
        if "sku" in table:
            table["เมนู"] = table["sku"].map(MENU_NAMES).fillna(table["sku"])
        if "kitchen" in table:
            table["ครัว"] = table["kitchen"].map(KITCHEN_NAMES).fillna(table["kitchen"])
    monthly = tables["Monthly_PnL"]
    for column in ["gross_revenue_thb", "gross_profit_thb"]:
        total = monthly[column].sum()
        if not all(np.isclose(total, tables[name][column].sum(), atol=0.01, rtol=0)
                   for name in ["SKU_PnL", "Kitchen_PnL"]):
            raise ValueError(f"ยอด {column} รายเดือน เมนู และครัวไม่ตรงกัน")
    expected = monthly["gross_profit_thb"] - monthly["fixed_overhead_thb"]
    if not np.allclose(expected, monthly["operating_profit_thb"], atol=0.01, rtol=0):
        raise ValueError("กำไรดำเนินงานไม่ตรงกับกำไรขั้นต้นหักค่าใช้จ่ายประจำ")
    return tables


def summarize(frame):
    revenue = frame["gross_revenue_thb"].sum()
    gp = frame["gross_profit_thb"].sum()
    return {
        "revenue": revenue,
        "gp": gp,
        "op": frame["operating_profit_thb"].sum(),
        "margin": gp / revenue if revenue else 0,
        "units": frame["units_sold"].sum(),
        "waste": frame["waste_cost_thb"].sum(),
    }


def simulate_price(row, increase_pct, volume_loss_pct):
    """สมมติต้นทุนต่อแก้วและอัตราคอมมิชชันคงเดิม ใช้เฉพาะรายการราคาปกติ."""
    price = row["standard_avg_price_thb"] * (1 + increase_pct / 100)
    contribution = price * (1 - row["commission_rate"]) - row["non_commission_cost_per_cup_thb"]
    baseline = row["current_contribution_per_cup_thb"]
    units = row["standard_units"] * (1 - volume_loss_pct / 100)
    return {
        "price": price,
        "contribution": contribution,
        "total": units * contribution,
        "difference": units * contribution - row["standard_units"] * baseline,
        "breakeven_loss": 1 - baseline / contribution if contribution > 0 else np.nan,
    }
