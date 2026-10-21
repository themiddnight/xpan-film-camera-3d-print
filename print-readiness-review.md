# Print-Readiness Review — 2026-07-13

สรุปผลการตรวจสอบว่าโมเดลที่มี "พิมพ์ใช้งานได้จริงหรือยัง" พร้อมสิ่งที่แก้ไปแล้วและสิ่งที่ยังขาด

---

## 1. สถานะโดยรวม

| โมดูล | มีโมเดลไหม | พิมพ์ได้จริงไหม (หลังแก้) |
|---|---|---|
| Film Back | ✅ (`film-back-v01-fixed.scad`) | ✅ ชิ้นส่วนหลักพิมพ์ได้ (ต้อง print test coupon ก่อน) |
| Simple Body (pinhole) | ✅ ใหม่ `simple-body-v01.scad` | ⚠️ STARTER — hook/latch ต้อง test-fit, M42 เป็น plain bore |
| Pinhole Module | ✅ ใหม่ `pinhole-module-v01.scad` | ⚠️ STARTER — M42 เป็น plain spigot, ใช้ brass shim จริง |
| Lens Body / Lens Module | ❌ ยังเป็น research | ❌ |

ก่อนหน้านี้ไฟล์เดียวที่มีคือ film back และมันเป็น **โมเดล assembly สำหรับ review** (รวมทุกชิ้นซ้อนกัน มีสี มี mockup) ไม่ใช่ชิ้นส่วนแยกสำหรับ export STL — จึงยังพิมพ์ใช้จริงไม่ได้

---

## 2. ข้อผิดพลาดที่เจอ + สิ่งที่แก้แล้ว (film back)

### 2.1 [CRITICAL] Sprocket pitch ผิด → เลื่อนฟิล์มผิดระยะ
- **เดิม:** วางฟิล์มแนบกับ *ตัวเฟือง* (Ø20.2) ทำให้ 1 รอบเลื่อนฟิล์ม `π×20.2 = 63.46mm`
- **ที่ถูก:** ต้องแนบกับ *pitch circle* (Ø21.17 = 14×4.750/π) → 1 รอบ = `66.50mm` พอดี = 1 เฟรม
- เดิมสั้นไป 3.04mm/เฟรม (4.6%) — สะสม ~0.22mm/รู เฟรมจะเบียดกันและฟันจะหลุดร่องหลังถ่ายไปไม่กี่เฟรม
- **แก้:** `sprocket_center_y = film_plane_y + sprocket_pitch_d/2` (ตอนนี้ตัวเฟืองเว้นฟิล์ม 0.48mm, ปลายฟันจิ้มทะลุรู 0.42mm)

### 2.2 [สำคัญ] รูเพลาไม่มี clearance → หมุนไม่ได้
- **เดิม:** bore = เพลา = Ø4.0 พอดีเป๊ะ (sprocket, cam) — พิมพ์ FDM แล้วฝืด/อัดแน่น
- **แก้:** เพิ่ม `shaft_bore_d = 4.0 + 0.35 = 4.35mm` (clearance รัศมี 0.175mm หมุนคล่อง)

### 2.3 [สำคัญ] ไม่มีตัวเลือกแยกชิ้นเพื่อ export
- **แก้:** เพิ่มตัวแปร `part` ด้านบนไฟล์ + dispatch ด้านล่าง เลือก export ได้ทีละชิ้น:
  `assembly` (ค่าเริ่มต้น, review) · `shell` · `rear_cover` · `sprocket` · `cam` · `takeup_spool` · `rewind_knob` · `advance_knob` · `release_button` · `pawl`
- ชิ้นที่ export จะเป็น solid เดี่ยว ตัด mockup/ฟิล์ม/สักหลาด/แกนโลหะ/เส้น outline ออกหมด

### 2.4 ฝาหลัง (rear cover) เดิมเป็นแค่แผ่น preview
- **แก้:** เพิ่ม `rear_cover_part()` เป็นฝาพิมพ์ได้จริง — แผ่นซีล + ขอบ lip สอดเข้าช่อง + บานพับ 2 จุด + แถบล็อกบน

---

## 3. สิ่งที่ยังต้องทำ/ระวังก่อนพิมพ์จริง

1. **พิมพ์ test coupon ก่อน** — sprocket + cam + รางฟิล์มสั้น ๆ แล้วลองกับฟิล์ม 135 เศษ ตามแผนใน `film_back_design.md` §15 (ค่าฟันเฟืองเป็นค่าเริ่มต้น ต้องจูนจากของจริง)
2. **ขนาดรวมกว้าง 195mm** — ต้องมีเตียงพิมพ์ ≥ ~200mm ในแกน X (หรือหันพิมพ์เอียง/แยกชิ้น) shell สูง 62mm ลึก 54mm
3. **แนะนำหันพิมพ์ shell แบบหน้า +Y คว่ำลงเตียง** เพื่อให้ผิวราง/gate เรียบ ไม่ต้อง support ในห้องฟิล์ม
4. **body ↔ film back hook/latch** ใน `simple-body-v01.scad` เป็น provisional — ต้องพิมพ์แล้วลองประกบจริงเพื่อจูน
5. **M42** ทั้ง body และ module ทำเป็น plain bore/spigot — ต้อง tap เกลียว, พิมพ์วงเกลียวแยก, หรือติด adapter M42 (เกลียวพิมพ์ตรง ๆ ต้องจูนตามเครื่อง)
6. **ชิ้นไม่พิมพ์ (ตามดีไซน์):** dark slide (แผ่นอลู/HIPS ตัด), foam pressure pad, สักหลาด/velvet, เพลาโลหะ Ø4, พินบานพับ, brass pinhole shim, ใบชัตเตอร์ทองเหลือง
7. **ยังไม่มี:** lens body + lens module (ยังเป็น research)

---

## 4. ไฟล์ที่เปลี่ยน/สร้าง

| ไฟล์ | สถานะ |
|---|---|
| `film-back-v01-fixed.scad` | แก้: sprocket pitch, bore clearance, part selector, ฝาหลังจริง |
| `simple-body-v01.scad` | สร้างใหม่ (starter) |
| `pinhole-module-v01.scad` | สร้างใหม่ (starter) |

> หมายเหตุ: ตรวจเรขาคณิตด้วยการคำนวณ Python (ยืนยัน 1 รอบ = 66.50mm, bore clearance, ระยะผนัง) เพราะติดตั้ง OpenSCAD ในแซนด์บ็อกซ์ไม่ได้ (ไม่มีสิทธิ์/เน็ต) — **ควรเปิด F5/F6 ใน OpenSCAD เพื่อ render ยืนยันอีกครั้งก่อนพิมพ์**
