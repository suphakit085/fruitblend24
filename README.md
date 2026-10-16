# FruitBlend24 Case Study

## Interactive Dashboard

มี Streamlit Dashboard ภาษาไทยใน `dashboard/` สำหรับเปิดนำเสนอผลวิเคราะห์ พร้อมตัวกรองเดือน เมนู ครัว และแบบจำลองราคา อ่านวิธีรันใน `dashboard/README.md` หรือดับเบิลคลิก `dashboard/Start_Dashboard.cmd` บนเครื่องนี้ แล้วเปิด http://localhost:8501

Dashboard ใช้สำเนาผลวิเคราะห์รุ่นหลักใน `dashboard/data` เป็น snapshot ของข้อมูลจำลอง ไม่ได้เชื่อมข้อมูลสด

ชุดงานนี้วิเคราะห์ข้อมูลย้อนหลัง 12 เดือนของ FruitBlend24 เพื่อประเมินคุณภาพข้อมูล ผลประกอบการ ราคา โปรโมชัน portfolio และความต้องการวัตถุดิบใน 3 เดือนถัดไป

## ไฟล์หลัก

- รายการไฟล์รุ่นหลักและตัวเลขอ้างอิงอยู่ใน `SUBMISSION_FILES.md` ยืนยันเมื่อ 30 กันยายน 2026 ใช้รายการนี้ในการปรับสไลด์และเตรียมส่งงาน
- `FruitBlend24_Analytics_Colab.ipynb` คือ Notebook หลักสำหรับเปิดใน Google Colab
- `analysis.py` คือ pipeline แบบ modular รุ่นเดิมสำหรับรันในเครื่อง ส่วน Notebook รุ่นปัจจุบันเขียนขั้นตอนวิเคราะห์ไว้โดยตรงและไม่ import ไฟล์นี้
- เมื่อรัน Notebook ผลลัพธ์ใหม่จะอยู่ใน `outputs/notebook_run/` เพื่อไม่เขียนทับ Excel รุ่นหลักที่เตรียมส่ง
- `outputs/FruitBlend24_Analysis_Results.xlsx` รวม summary, recommendations, P&L และ forecast เป็นไฟล์ผลวิเคราะห์รุ่นหลัก
- `outputs/01a0e8c7-6f36-7211-83f0-28b981dcd1a6/FruitBlend24_Orders_Cleaned_Ready.xlsx` เป็น cleaned-orders appendix สำหรับส่งพร้อม Notebook
- `outputs/analysis/FruitBlend24_Analysis_Results.xlsx` และ `FruitBlend24_Analysis_Outputs.zip` เป็นรุ่นเก่า ไม่ใช้เป็นฐานตัวเลขของสไลด์หรือชุดส่งปัจจุบัน

## วิธีรันใน Google Colab

1. เปิด `FruitBlend24_Analytics_Colab.ipynb` ใน Google Colab
2. เลือก **Runtime > Run all**
3. อัปโหลด `FruitBlend24_Intern_Case_Data.xlsx` เมื่อ Notebook ถามหาไฟล์
4. รอให้ Notebook สร้างตาราง กราฟ และไฟล์ `FruitBlend24_Analysis_Results.xlsx`
5. ดาวน์โหลดไฟล์ Excel จากหน้าต่างดาวน์โหลดของ Colab

Notebook ใช้ `pandas` กับ `numpy` สำหรับการคำนวณ ใช้ `matplotlib` สำหรับกราฟ และใช้ `openpyxl` เฉพาะการส่งออก Excel เขียนตามลำดับขั้นตอน มีฟังก์ชันเฉพาะ forecast ที่เรียกซ้ำ ไม่มี class หรือ framework วิเคราะห์เพิ่มเติม

หัวข้อและคำอธิบายเป็นภาษาไทย แยก cell สำหรับการเตรียมต้นทุน กำไรสินค้า กำไรครัว และการทดสอบ forecast เพื่อเปิดอธิบายระหว่างสัมภาษณ์ได้ง่าย ตัวเลขคำนวณยังเก็บความละเอียดเดิม ไม่ปัดเศษก่อนวิเคราะห์

## วิธีวิเคราะห์

Pipeline ทำงานตามลำดับดังนี้

1. ตรวจจำนวนแถว ชนิดข้อมูล missing values exact duplicates ความสมเหตุสมผลของยอดขาย และ coverage ของรหัสอ้างอิง
2. จัดชื่อสินค้าภาษาไทยและอังกฤษเป็น 5 SKU เก็บสินค้านอกเมนูและสำเนาไว้ใน exceptions
3. เชื่อมต้นทุนผลไม้รายสัปดาห์ packaging ค่าแรง ค่าคอมมิชชัน waste และ overhead
4. สร้าง P&L รายเดือน แยกสินค้าและครัว พร้อมเทียบ monthly budget
5. วิเคราะห์ demand ตามเดือน วัน และชั่วโมง ประเมินจุดคุ้มทุนเมื่อทดลองราคา และเปรียบเทียบโปรโมชันกับแถวมาตรฐานที่มีลักษณะใกล้กัน
6. สร้างตาราง Kitchen × SKU priorities ระบุระดับความสำคัญ สิ่งที่ควรทำ และหลักฐานจากกำไร margin และอัตราของเสีย
7. ทดสอบ forecast แบบค่าเฉลี่ยตามวันในสัปดาห์จาก 4 และ 8 สัปดาห์ล่าสุดกับข้อมูลเดือนมิถุนายนถึงสิงหาคม 2026
8. สร้าง forecast เดือนกันยายนถึงพฤศจิกายน 2026 และ inventory target เป็นจำนวนแก้วเทียบเท่า
9. ประเมิน P&L ภายใต้กรณีฐาน demand ลด ต้นทุนผลไม้เพิ่ม และ action plan

## สมมติฐานสำคัญ

- `price_thb` เป็นราคาหลังส่วนลด จึงไม่หักส่วนลดซ้ำ
- กำไรขั้นต้นที่ใช้เทียบ budget คือรายได้หลังหัก commission, fruit, packaging, labor และ waste ก่อน overhead เนื่องจากโจทย์ไม่ได้ให้นิยามโดยละเอียด
- ต้นทุน Mixed Berry ของวันเปิดตัว 1 มีนาคม 2026 ใช้ค่าของสัปดาห์แรกที่เริ่ม 2 มีนาคม
- วันซึ่งไม่มีรายการขายหลังสินค้าเริ่มจำหน่ายถือเป็นศูนย์แก้วเมื่อสร้าง daily demand panel
- Inventory target ใช้ forecast รายวันบวก safety stock จาก error percentile ที่ 90 และจำกัดไม่เกิน demand สองวัน
- ตาราง Kitchen × SKU ใช้ข้อมูล 6 เดือนล่าสุด โดยใช้อัตราของเสีย 10% และ gross margin 20% เป็น trigger เพื่อคัดกรองงาน ไม่ใช่เป้าหมายอย่างเป็นทางการของบริษัท
- Action scenario สมมติจำนวนแก้ว Mixed Berry ลด 2% ราคาที่รับรู้เพิ่ม 5% และต้นทุน waste ลด 20%

## ข้อจำกัด

- ข้อมูลไม่มี customer ID จึงวิเคราะห์ RFM หรือ customer lifetime value ไม่ได้
- ข้อมูลไม่มี order ID จึงทำ market basket หรือ association rules ไม่ได้
- มีประวัติเพียง 12 เดือน จึงประเมินฤดูกาลแบบเทียบปีก่อนไม่ได้ และ forecast มี WAPE ประมาณ 26%
- ไม่มีสูตรวัตถุดิบต่อแก้ว inventory on hand stockout หรือ supplier lead time จริง จึงยังแปลงแผนเป็นกิโลกรัมหรือ purchase order ไม่ได้
- การเปรียบเทียบโปรโมชันเป็น observational matching ไม่ใช่ randomized experiment
- โปรโมชันใช้เฉพาะแถวที่มี standard-rate benchmark ตรงกันครบตามสินค้า ครัว แพลตฟอร์ม วันในสัปดาห์ และชั่วโมง แถวที่ match ไม่ได้จะอยู่ในรายละเอียดแต่ไม่ถูกรวมในผลกระทบ
- ตาราง Kitchen × SKU เป็นกฎคัดกรองเพื่อชี้จุดที่ควรตรวจต่อ ไม่ได้ยืนยันว่า action จะทำให้กำไรดีขึ้นโดยอัตโนมัติ

## การตรวจสอบคุณภาพงาน

- Notebook รุ่นสำหรับสัมภาษณ์ผ่านการรัน code ทั้ง 28 cell ตั้งแต่ต้นจนจบ และผลทั้ง 14 sheet ตรงกับ Excel รุ่นหลักหลังปรับความอ่านง่ายเมื่อ 30 กันยายน 2026
- รายงานตรวจรอบนี้อยู่ใน `tmp/notebook_interview_qa.json` มีการตรวจว่า Raw และ Excel ที่เตรียมส่งไม่ถูกแก้ไข
- ตรวจการกระทบยอดจำนวนแถว รายได้ ต้นทุนที่หายไป สูตร P&L ช่วง forecast และ WAPE กับข้อมูลต้นฉบับ
- `qa_validate.py` และ `outputs/analysis/qa_report.json` เป็นชุดตรวจของ pipeline รุ่นเดิม
- สไลด์ Canva ปัจจุบันคือ `DAHWmMuULfA` และ PDF รุ่นล่าสุดที่ตรวจยังต้องแก้เนื้อหาและการจัดวางก่อนส่ง ใช้ Excel รุ่นหลักตาม `SUBMISSION_FILES.md` เป็นฐานของตัวเลข

## สิ่งที่ควรศึกษาต่อ

- เพิ่ม customer ID และ order ID เพื่อวัดการกลับมาซื้อ ผลระยะยาวของแคมเปญหาลูกค้าใหม่ และ basket composition
- เก็บ inventory on hand, stockout, recipe yield, shelf life และ lead time จริงเพื่อปรับ reorder point
- ทดลองราคา Mixed Berry Premium แบบแบ่งกลุ่มหรือแบ่งช่วงเวลา และวัด contribution profit ต่อแก้วควบคู่กับจำนวนแก้ว
- ทดลองลดการเตรียม Mixed Berry ใน BKK_Ladprao ซึ่งมี waste rate สูงสุด แล้วติดตามของเสียและ stockout รายสัปดาห์
