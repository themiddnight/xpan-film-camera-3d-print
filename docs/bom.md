# Bill of Materials: Pinhole Camera v02

Bought parts for the film back, simple body and pinhole module. Printed parts are listed in the module design docs.

Prices are from Lazada Thailand search pages on 2026-10-21, lowest variant shown, before shipping. "Seen" means a price was on the page. "Est." means none was seen. Listings change, so treat prices as a guide. Shopee Thailand did not load for automated research; the same search terms work there.

## Parts

| # | Part | Qty to buy | Spec | Used for | Search terms | Price |
|---:|---|---|---|---|---|---|
| 1 | Stainless 304 round rod | 1m (or 2 x 500mm) | Ø3.0mm, cut to length | Sprocket pin 60mm, rewind shaft 21mm, take-up drive shaft 70mm, pawl pivot 15mm, cover hinge pin 171mm, body latch pin 48mm, shutter lock pivot 9mm (about 394mm total) | "เพลาสแตนเลส 304 3 มิล", "stainless rod 3mm" | ฿35-115 (seen, varies by length) |
| 2 | M42 body cap + rear lens cap pair | 2 pairs (one spare) | M42 x 1, plastic | Rear cap = body female mount; body cap = pinhole module base | "M42 body cap", "ฝาปิดท้ายเลนส์ M42" | ฿39-50 per pair (seen) |
| 3 | Brass shim | 1 sheet | 0.05mm, about 5 x 5in | Pinhole plate | "แผ่นชิมทองเหลือง 0.05", "brass shim 0.05mm" | ฿95 (seen) |
| 4 | Aluminium sheet | 1 | 0.5mm, 30 x 30cm, AL1100 | Dark slide (71 x 58mm: a 71mm plate in the 72mm slot with a 20 x 11mm pull tab) and shutter blade (38 x 23mm with an 11mm tongue, a 4mm hole, two 1.5mm dimple holes and a 3.3mm stop slot) | "แผ่นอลูมิเนียม 0.5 mm AL1100" | ฿70 (seen) |
| 5 | M3 brass heat-set inserts | 1 pack | M3, check OD on arrival (4.0 or 4.6mm) | Rear cover turn-buttons | "น็อตฝังทองเหลือง M3", "heat set insert M3" | ฿102-150 per 100 (seen) |
| 6 | M3 screw kit | 1 | Socket head, includes M3 x 8 | Turn-button pivots | "ชุดน็อตสกรู M3 สแตนเลส" | ฿145-160 (seen) |
| 7 | Compression spring | 1-2 | 0.3mm wire, OD 3-4mm, trim to about 8mm | Pawl spring (target 1-2N) | "สปริงอัด 0.3 มิล" | Est. ฿40-60 (a 0.4mm-wire spring was seen at ฿60, but it is too stiff here) |
| 7b | Stainless spring assortment | 1 set | OD 3-6mm | Clutch spring: needs about 5mm OD so it slides over the 3mm shaft | "สปริง สแตนเลส ชุด" | ฿82 (seen) |
| 8 | Stainless hex nut | 2 (one spare) | 1/4"-20 UNC | Tripod socket, captured in the body | "น็อตตัวเมีย 1/4 เกลียวหุน หยาบ" | ฿6-20 (seen) |
| 9 | Self-adhesive black felt | 1 sheet | 1-2mm thick (3mm is too thick) | Throat light trap, clutch washer | "สักหลาดดำ มีกาว" | ฿56-140 (seen) |
| 10 | Black flocking / velvet adhesive sheet | 1 sheet | Thin flocked paper | Body-to-back seal groove, dark slide slot lips, chamber lining | "black flocking adhesive paper", "กำมะหยี่ดำ มีกาว" | Est. ฿100-200 (not found on Lazada; try Shopee or AliExpress) |
| 11 | EVA foam sheet | 1 | 2mm closed-cell | Pressure pad, cover groove seal strip | "โฟม EVA 2 มิล" | ฿44 per A1 sheet (seen) |
| 12 | Thin black plastic sheet | 1 | About 0.2-0.3mm, smooth | Film-side face of the pressure pad | "แฟ้มพลาสติกดำ", "black PET sheet 0.25mm" | Est. ฿20-40 |
| 13 | Small O-ring | 1 pack | 3mm ID x 1mm section | Rewind knob friction hold, in a 4.8mm counterbore | "โอริง 3x1" | Est. ฿20-50 |
| 14 | Flat black spray paint | 1 can | Flat/matte black | Chamber interiors, dark slide, shutter blade | "สีสเปรย์ ดำด้าน FLAT BLACK" | ฿42-54 (seen, e.g. Red Fox No.4) |
| 15 | Stainless spring wire | Not needed | Ø1.0mm, straight | Was the wire-frame viewfinder; the finder frames are now printed (simple-body.md 5). Skip it | "ลวดสปริงสแตนเลส 304 เส้นตรง 1 มิล" | ฿30-40 (seen) |
| 16 | Empty reloadable 135 cassettes | 1 set of 5 | Standard 135 | Measuring the cassette and spool key; transport tests with scrap film | "ตลับฟิล์มเปล่า 135" | ฿163 per 5 (seen) |
| 17 | 5-minute epoxy | 1 | Two-part | Knobs and fork to shafts, M42 rings into printed pockets, dark slide holder onto the rear cover | "กาวอีพ็อกซี่ 5 นาที" | Est. ฿60-100 |
| 18 | Black PETG filament | 1kg | 1.75mm | All printed parts | "PETG สีดำ 1kg" | Est. ฿400-600 |

**Estimated total:** about ฿1,600-2,300 for the parts above, before shipping. This is an estimate summed from the seen prices plus the estimated rows.

## Tools assumed

Soldering iron with a heat-set insert tip (about ฿207 seen for a tip kit), digital calipers, hacksaw or rotary tool for the rod, fine needle or 0.3mm drill for the pinhole, fine sandpaper, craft knife.

## Measure on arrival (before CAD phase 3 and 4)

These values sit in the docs as nominals. Measure them with calipers and update `cad/params.py` once it exists.

| Part | Measure | Nominal in the docs |
|---|---|---:|
| Cassette (#16) | Shell diameter | 25.0mm |
| Cassette | Felt lip envelope | 29.5mm |
| Cassette | Height between end caps | 39.0mm |
| Cassette | Spool top protrusion, key slot width and depth | 7.5mm, 2.6 x 4.5mm |
| Cassette | Spool bottom stub length and diameter | 2.5mm |
| Rear lens cap (#2) | Ring OD and height | 46mm, 8mm |
| Body cap (#2) | Flange OD; seat face to front face | 53mm, 2.0mm |
| Heat-set insert (#5) | OD and length | 4.0 or 4.6mm |
| Hex nut (#8) | Across flats and thickness | 11.1mm, 5.6mm (est.) |
| Rod (#1) | Actual diameter | 3.00mm |

## Sourcing notes

- **M42 pitch.** M42 x 1 is the camera mount. T-mount (T2) is also 42mm but has a 0.75mm pitch. Check for "x1" or "SLR" in the listing.
- **Insert OD differs by seller.** Lazada "M3 x 5 x 4" inserts are OD 4.0; Ruthex-style are OD 4.6. The hole size is a tunable parameter with a test coupon.
- **Laser-drilled pinholes** are not sold in Thailand. Hand-drilling 0.05mm shim works; an imported laser pinhole (eBay, AliExpress) is optional.
- **Cross-border listings** (marked ต่างประเทศ) take 1-3 weeks.
- **Dowel pins** (฿6 each, seen) come only up to about 40mm long, too short for the shafts here, so the BOM uses cut rod. 304 rod cuts easily; hardened pins do not.
