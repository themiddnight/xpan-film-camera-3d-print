# Engineering and Optical Design for DIY 60x24mm Panoramic 135 Film Systems

The development of a bespoke panoramic camera using 135 film requires a sophisticated synthesis of optical physics, mechanical engineering, and material science. The specific target of a 60x24mm frame size on standard 35mm film represents a significant departure from the traditional 24x36mm format, nearly doubling the horizontal field of view while maintaining the vertical dimension associated with standard 35mm still photography.\[1, 2\] This 2.5:1 aspect ratio is visually reminiscent of professional cinematic formats like Techniscope or anamorphic widescreen, offering a field of view that closely aligns with human peripheral perception.\[2, 3\] To realize such a system in a DIY capacity, one must address the critical requirement of an image circle large enough to illuminate a 60mm width without significant vignetting or loss of resolution at the periphery.\[1, 4, 5\]  
Optical Foundations and Image Circle Requirements  
The primary constraint in any camera design is the "covering power" of the lens. For a standard 35mm frame (24x36mm), the diagonal is approximately 43.3mm, calculated as D=  
24  
2  
\+36  
2

​  
. Most lenses designed for 135 film are optimized for this specific diagonal to minimize size, weight, and manufacturing costs.\[1, 5\] When the frame is widened to 60mm, the required diagonal (D  
pano  
​  
) increases significantly:  
D  
pano  
​  
\=  
24  
2  
\+60  
2

​  
≈64.62 mm  
This indicates that a standard lens designed for a 35mm SLR or rangefinder will likely suffer from severe mechanical vignetting, as its image circle is rarely much larger than 45-50mm.\[1, 6\] Consequently, the designer must identify optics designed for larger film formats that naturally project a larger image circle while maintaining the desired focal length of approximately 50mm to provide a "normal" perspective on the vertical axis.\[6, 7, 8\]  
The relationship between the film format, focal length, and angle of view is central to the panoramic effect. While a 50mm lens is considered "normal" on a standard 35mm frame, its horizontal angle of view expands when the film gate is widened, providing a perspective that feels wide-angle horizontally but remains normal in its magnification and compression of background elements.\[7, 8, 9\]  
Comparative Optical Performance of Targeted Lens Systems  
Lenses from the 127 roll film era and early 6x4.5cm or 6x6cm medium format systems offer the most viable candidates for a 60x24mm frame due to their inherent covering power.\[7, 10, 11\] The following table outlines the technical specifications of prime candidates identified through historical performance data and mechanical compatibility.

| Lens Model | Native Format | Focal Length | Shutter Type | Aperture Range | Est. Image Circle |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Schneider Super-Angulon XL | 4x5" / 6x12cm | 47mm | Copal \#0 | f/5.6 \- f/32 | 166mm @ f/22 |
| Mamiya-Sekor (C330 TLR) | 6x6cm | 55mm | Seiko \#0 | f/4.5 \- f/32 | \~80mm |
| Schneider Xenar (Baby Rollei) | 127 (4x4cm) | 60mm | Synchro-Compur | f/3.5 \- f/22 | \~70mm |
| Zeiss Tessar (Nagel Pupille) | 127 (3x4cm) | 50mm | Compur | f/2.8 \- f/22 | \~65mm |
| Mamiya Press Super-Wide | 6x9cm | 50mm | Seiko \#0 | f/6.3 \- f/32 | \~100mm |
| Dakon (Kodak Brownie 127\) | 127 (4x6.5cm) | 65mm | Simple Leaf | Fixed f/14 | \~75mm |
| Industar-23 (Moskva 5\) | 6x9cm | 110mm | Moment | f/4.5 \- f/32 | \~115mm |

The Schneider Super-Angulon 47mm f/5.6 XL stands as the professional-grade benchmark for this application. It provides an astounding 120-degree angle of view at f/22, ensuring that even with the extreme 60mm frame width, there is ample illumination and sharpness across the entire negative.\[12, 13\] However, its cost and complexity may be prohibitive for entry-level DIY builds. Conversely, lenses salvaged from 127-format cameras like the Nagel Pupille or the Rolleiflex 4x4 (Baby Rollei) provide a much more compact form factor, aligning with the user's requirement for a non-bulky system.\[14, 15, 16, 17\]  
Lens Archeology: Sourcing Compact Vintage Optics  
To satisfy the requirement for a lens with fewer elements and a compact profile, the research highlights the era of "Vest Pocket" and early roll film cameras. These lenses were often constructed using the Tessar or triplet formulas, which utilize four and three elements respectively.\[18, 19, 20\]  
The 127 Format Advantage  
The 127 film format, introduced by Kodak in 1912, utilized a 46mm wide film strip, positioned between 35mm and 120 film.\[10, 17\] Cameras designed for this format, such as the "Baby" Rolleiflex or the Zeiss Ikon Kolibri, utilized lenses with focal lengths ranging from 50mm to 60mm to cover frame sizes of 3x4cm or 4x4cm.\[14, 16, 21\] Because the diagonal of a 4x4cm frame is approximately 56.6mm, these lenses are naturally capable of covering a 60x24mm panoramic frame with only minimal softening or light fall-off at the extreme corners.\[20, 22\]  
The Schneider-Kreuznach Xenar 60mm f/3.5, commonly found on the postwar "Grey Baby" Rolleiflex, is a premier candidate. It is a Tessar-type lens known for its exceptional sharpness and micro-contrast, housed in a very compact Synchro-Compur shutter assembly.\[14, 15, 20\] For builders seeking a slightly wider perspective closer to the requested 50mm, the Zeiss Tessar 50mm f/2.8 or the Schneider Xenar 50mm f/3.5 from the Nagel Pupille (circa 1930\) offers professional-level optics in a helical mount that is relatively easy to adapt to a DIY chassis.\[16, 17, 23\]  
Simplified Meniscus and Landscape Lenses  
For a more "pictorialist" or lo-fi aesthetic with fewer lens elements, the 65mm Dakon lens found on the Kodak Brownie 127 is a unique option.\[24, 25\] The Brownie 127 used a 4x6.5cm frame, meaning its simple plastic meniscus lens possesses a massive image circle that comfortably covers the 60mm panoramic width.\[24, 26\] While it lacks variable aperture and shutter speed controls—typically fixed at f/14 and 1/50th of a second—it represents the absolute minimum in terms of element count and weight.\[24\] Optical designers note that these simple meniscus lenses can achieve surprisingly sharp results in the center, with a pleasingly soft fall-off toward the edges that can enhance the cinematic feel of panoramic photography.\[24, 25\]  
Mechanical Shutter Architectures for Bespoke Builds  
The integration of a shutter system is arguably the most complex mechanical challenge in DIY camera construction. The research suggests three primary pathways: utilizing integrated leaf shutters, engineering gravity-fed guillotine shutters, or adapting electronic/servo-controlled systems.\[27, 28, 29\]  
Integrated Mechanical Leaf Shutters  
The most reliable approach is to select a lens already housed in a mechanical shutter, such as the Copal \#0, Compur, or Seiko shutters.\[11, 30, 31\] These self-contained units provide accurate timing (typically from 1 second to 1/500th of a second) and integrated aperture control.\[12, 32\] Lenses from the Mamiya C330 TLR system (e.g., the 55mm f/4.5) are particularly popular for DIY panoramic builds because they include their own shutter and are designed for a 6x6cm image circle, making them perfectly suited for 60x24mm panoramas.\[31, 33\] The Infidex 176 project specifically leverages the leaf shutter from the Mamiya C330 to simplify the camera body design to a simple light-tight box.\[31\]  
DIY Guillotine Shutter Mechanics  
For lenses without a shutter (barrel lenses), a guillotine shutter is a historically accurate and mechanically accessible solution.\[27, 34\] This design utilizes a sliding blade with a slit that falls or is pulled across the lens opening.\[27, 35, 36\]

1. Gravity-Powered Sliders: A vertical guide allows a blade made of 3mm Foamex or black ABS plastic to drop by gravity.\[27, 36\] The exposure time is determined by the width of the slit and the speed of the fall at the point it crosses the lens.\[27, 35\]  
2. Spring-Loaded Variants: To achieve higher speeds and more consistent horizontal operation, builders use tension springs to pull the blade across the aperture.\[28, 35\]  
3. Accuracy and Reliability: While gravity shutters are extremely accurate for slower speeds, they are susceptible to inconsistencies if the camera is not perfectly level.\[27, 36\] Advanced DIY designs incorporate a "dual-plate" system where one plate opens and a second trailing plate closes, mimicking the operation of a focal-plane shutter.\[28, 29\]

| Shutter Speed (Approx.) | Slit Width (mm) | Mechanism | Best Use |
| :---- | :---- | :---- | :---- |
| 1/15 s | 15.0 | Gravity Fall (Standard Height) | Low light / Tripod |
| 1/30 s | 7.5 | Gravity Fall (Standard Height) | Overcast daylight |
| 1/60 s | 4.0 | Gravity Fall (Standard Height) | Sunny daylight |
| 1/125 s | 2.0 | Spring Tension (Low Tension) | Handheld / Fast Film |
| 1/250 s | 1.0 | Spring Tension (High Tension) | Fast Action |

Servo and Microcontroller Controlled Shutters  
Modern DIY builders have successfully utilized Arduino-controlled servos to actuate simple blade shutters.\[29\] This allows for precise electronic timing, although the "rolling blind" or "butterfly" shutter designs typically used with servos may have difficulty achieving speeds faster than 1/125th of a second due to the physical limitations of hobbyist servo motors.\[29\] These systems are ideal for long exposures or specialized applications where remote triggering is required.\[29, 37\]  
The Pinhole Perspective: Physics of the Lensless Panorama  
A panoramic pinhole camera offers the most simplified execution of the 60x24mm format, eliminating the need for lens elements and focusing mechanisms.\[38, 39\] For a focal length (f) of 50mm, the optimal pinhole diameter (d) is determined by the wavelength of light (λ) and a constant (c) typically set at 1.9 for the highest resolution \[38, 40, 41\]:  
d=1.9⋅  
f⋅λ

​  
Assuming a standard green light wavelength of 550 nm (0.00055 mm):  
d=1.9⋅  
50⋅0.00055

​  
≈0.315 mm  
A pinhole of approximately 0.3mm at a 50mm distance results in an effective aperture of f/167 (50/0.3=166.6).\[40, 41\] The panoramic format is particularly well-suited to pinhole photography because the infinite depth of field ensures that the entire wide scene remains in focus, from the extreme foreground to the horizon.\[38\]  
Flat vs. Curved Film Planes  
In a panoramic build, the choice between a flat and a curved film plane significantly impacts the final image's geometry.\[25, 39\]

* Flat Plane: Produces a traditional rectilinear perspective where straight lines remain straight. However, this causes "light fall-off" (vignetting) at the edges of the 60mm width due to the cos  
* 4  
* θ law of illumination, where the edges are significantly further from the pinhole/lens than the center.\[4, 25\]  
* Curved Plane: By curving the film in a semi-circle with the pinhole at the center, the distance from the pinhole to every part of the film remains constant.\[25, 39\] This eliminates light fall-off and ensures uniform exposure and resolution across the entire 60mm width, although it introduces "cylindrical perspective," where horizontal straight lines (except the horizon) appear curved.\[25, 39\]

Film Transport and Frame Spacing Engineering for 135 Film  
The standard 35mm film advance is designed for a 24x36mm frame, typically advancing by 8 sprocket holes per frame.\[42, 43\] A 60x24mm frame requires a significantly longer advance to avoid overlapping images.\[43\]  
Sprocket Counting and Indexing  
The standardized distance between 35mm sprocket hole centers is 4.75mm.\[42, 44\] To accommodate a 60mm wide frame with a reasonable inter-frame gap, the advance must be calculated precisely.  
Advance Length=Frame Width+Gap  
If a 2.5mm gap is targeted for a 60mm frame, the total film travel per shot is 62.5mm.  
Number of Sprockets=  
4.75 mm  
62.5 mm  
​  
≈13.16  
In mechanical design, it is standard to use an integer number of sprocket holes. Advancing 14 sprocket holes (14×4.75 mm=66.5 mm) provides a 60mm frame with a 6.5mm gap, or a 64mm frame with a 2.5mm gap.\[43, 44\] This 14-sprocket advance is used by the Hasselblad XPan (24x65mm format), which yields approximately 21 exposures on a standard 36-exposure roll.\[9, 44\]  
DIY Winding Solutions  
For a simplified DIY build, two winding methods are prevalent:

* Turn-Counting: Builders calculate the number of turns on the take-up knob required to move the film by \~66mm.\[45, 46\] However, because film builds up on the take-up spool, the spool's diameter increases, and fewer turns are needed at the end of the roll than at the beginning.\[26, 45\]  
* Mechanical Ratchet: The most reliable DIY solution is to salvage the sprocket gear and ratchet from a donor 35mm camera and modify the gear ratio or the stopping point so it locks after 14 sprocket holes instead of 8.\[43, 47\]  
* Double-Advance: Some builders use standard 35mm camera bodies and modify them to "advance twice" without tripping the shutter, though this typically yields a 74-76mm frame (2×38 mm total advance), which may exceed the image circle of many 50mm lenses.\[43\]

DIY Lens Assembly and Aperture Control  
When using a barrel lens or a simple DIY optical element, integrating an aperture control system is essential for managing exposure and depth of field.\[48, 49\]  
Purchasing and Integrating Iris Modules  
Adjustable iris diaphragm modules can be purchased as modular components from suppliers on eBay or AliExpress.\[48, 50\] These units are available in various sizes, with the M30 to M37 thread mounts being common for DIY lens modifications.\[50, 51\]

1. Placement: The iris should ideally be placed at the lens's "nodal point," typically between the elements in a symmetric design.\[49, 52\] For simple lenses (like a meniscus), placing the iris approximately 15-30mm in front of the lens can act as a "Waterhouse stop," reducing spherical aberrations and improving sharpness at the cost of a slightly larger physical profile.\[25, 49\]  
2. Housing: A 3D-printed housing is the most efficient way to align the lens elements and the iris module.\[48\] The housing must ensure the optical path is perfectly centered and light-tight.\[48, 53\]  
3. Calibration: Once integrated, the aperture settings should be calibrated using a light meter.\[48\] By measuring the light transmitted at the largest opening and then closing the iris until the light meter shows a one-stop drop (50% reduction in light), the builder can mark the f-stop positions (f/5.6, f/8, f/11, etc.).\[48, 54\]

| Iris Module Spec | Value | Application |
| :---- | :---- | :---- |
| Min. Aperture | 1.5 mm | High depth of field / Bright light |
| Max. Aperture | 26 mm | Low light / Wide-open portraits |
| Mounting Thread | M30 to M37 | Standard DIY lens barrel fitting |
| Material | Aluminum Alloy | Durability and thermal stability |
| Blade Count | 8 to 15 blades | Circular bokeh and smooth transitions |

Material Science and Structural Construction  
The camera body (chassis) must be entirely light-tight and rigid enough to maintain the "flange focal distance" (FFD)—the precise distance from the lens mount to the film plane—within tolerances of ±0.1 mm.\[30, 45\]  
Manufacturing Methodologies

* 3D Printing (FDM/Resin): High-performance filaments like PETG, ABS, or Carbon Fiber Nylon are preferred for their opacity and resistance to heat (e.g., in a hot car).\[30, 55\] Resin printing offers higher precision for small mechanical parts like gears and ratchets.\[56\]  
* Laser-Cut Plywood/Acrylic: 1/8-inch (3.175mm) plywood is a common choice due to its ease of assembly with wood glue.\[45, 57\] Acrylic must be opaque (usually black) and requires specialized solvent cement.\[45\]  
* Foam Core and Cardboard: Suitable only for prototypes or lo-fi "trash" cameras.\[27, 39\] While easy to work with, these materials lack the structural rigidity required to keep the film flat over a 60mm span.\[39\]

Light Sealing and Internal Treatment  
A critical "third-order" insight for DIY builds is the treatment of the camera's interior.\[27, 45\] Light reflecting off the internal walls of the camera can cause "flare" or "ghosting," significantly reducing the contrast of the panoramic image.\[39, 45\]

1. Matte Black Paint: The entire interior of the lens box and film chamber should be sprayed with the flattest matte black paint available.\[27, 39, 45\]  
2. Labyrinth Joints: Designing joints with overlapping "V" or "U" shapes ensures that light must bounce multiple times before reaching the film, effectively killing its energy.\[27, 35\]  
3. Black Felt and Yarn: Using black felt at the film entrance/exit and black yarn or foam in the door grooves provides a final barrier against light leaks.\[27, 45\]

Calibration, Testing, and Infinity Focus Alignment  
The success of a fixed-focus panoramic camera depends on the precise alignment of the lens to the film plane for infinity focus.\[12, 30, 58\]  
Determining Flange Focal Distance (FFD)  
Every lens has a specified FFD—the distance from the rear of the mounting flange to the film when focused at infinity.\[12, 45\] For the Schneider 47mm XL, this is 59.1mm; for many vintage folder lenses, it is roughly equal to the focal length.\[12, 13\]  
The Ground Glass Method for Calibration:

1. Mount the lens to the camera body.\[30\]  
2. Open the back of the camera and stretch a piece of "frosted" or matte Scotch tape across the film gate where the film will sit.\[30, 45\]  
3. Open the lens shutter and aperture to their widest settings.\[4, 45\]  
4. Point the camera at a distant object (at least 100 meters away).\[12, 59\]  
5. Check the image on the frosted tape using a magnifying loupe.\[30\]  
6. If the image is blurry, use thin shims (made of cardstock or 0.1mm brass shim stock) to move the lens forward, or sand the lens board to move it backward, until the image is tack-sharp.\[12, 30, 58\]

Ensuring Film Flatness  
In a 60mm wide frame, film has a natural tendency to "curl" or "bow" toward the lens.\[39, 45\] This bowing changes the FFD in the center of the frame, causing the center to be out of focus while the edges are sharp (or vice versa).\[39, 43\]

* Pressure Plate: A DIY camera must incorporate a spring-loaded pressure plate at the back.\[30, 39, 45\] A common solution is to use a piece of flat metal or rigid plastic backed by a thin layer of black foam.\[39, 45, 47\]  
* Film Rails: The film should slide across smooth, rounded "matte plates" or rails that keep the edges at a fixed distance from the lens.\[45, 47\] Shaving and sanding these rails to be perfectly smooth is essential to prevent scratching the emulsion.\[39, 45\]

Technical Summary of Findings and Recommendations  
The research into DIY 60x24mm panoramic 135 systems reveals that the most viable and efficient path for the user's specific request is a hybrid approach involving vintage medium-format optics and modern manufacturing techniques.\[30, 31\]

| Component | Recommendation | Reasoning |
| :---- | :---- | :---- |
| Primary Lens | 55mm f/4.5 Mamiya-Sekor (C330) | Integrated shutter, compact, designed for 6x6 image circle. |
| Alt. Vintage Lens | 50mm f/3.5 Schneider/Zeiss (127 format) | Ultra-compact, few elements (Tessar), covers the 60mm width. |
| Shutter System | Integrated Leaf Shutter | Highest reliability and accuracy for a wide range of speeds. |
| Frame Spacing | 14-Sprocket Hole Advance | Standardized for XPan format; avoids overlap; consistent spacing. |
| Body Construction | 3D Printed (PETG or Nylon) | Complex internal geometries for light-trapping and sprocket indexing. |
| Focusing | Fixed Infinity Focus | Best for landscapes; utilizes depth of field at f/8-f/11 to cover near subjects. |
| Light Seal | Labyrinth Joints \+ Black Yarn | Proven DIY method for ensuring absolute light-tightness. |

Final Engineering Insight  
A panoramic camera is fundamentally a "wide-angle machine." The most critical insight for the builder is to respect the image circle.\[1, 5\] While it is tempting to use a high-quality 50mm lens from a 35mm SLR (like a Nikon Nikkor or Canon FD), these lenses are designed with baffles and internal optics that strictly limit the image circle to 43-45mm to reduce flare.\[5, 6, 60\] Attempting to use them for a 60mm frame will result in black unexposed corners.\[4, 5\] By sourcing lenses from the 127 roll film era or medium format systems, the builder taps into the "surplus" coverage necessary to create a professional-quality panoramic image.\[5, 7\] Furthermore, by adhering to the 14-sprocket advance standard, the user ensures compatibility with standard scanning and developing workflows, resulting in a DIY tool that is as functional as it is unique.\[9, 43, 44\]  
\--------------------------------------------------------------------------------

1. A Filmmaker's Guide to Sensor Sizes and Formats \- OLD FAST GLASS, [https://www.oldfastglass.com/news/2023/2/14/a-filmmakers-guide-to-sensor-sizes-and-formats](https://www.oldfastglass.com/news/2023/2/14/a-filmmakers-guide-to-sensor-sizes-and-formats)  
2. How To – 35mm Panoramic Film Images — Jeremy Mudd Photography, [https://www.jeremymuddphoto.com/blog/2020/3/4/how-to-35mm-panoramic-film-images](https://www.jeremymuddphoto.com/blog/2020/3/4/how-to-35mm-panoramic-film-images)  
3. 2-Perf vs 3-Perf vs 4-Perf: 35mm Film Formats Explained \- In Depth Cine, [https://www.indepthcine.com/videos/perf-35mm-film](https://www.indepthcine.com/videos/perf-35mm-film)  
4. The Image Circle \- Photo-Analogue, [http://photo-analogue.blogspot.com/2017/01/the-image-circle.html](http://photo-analogue.blogspot.com/2017/01/the-image-circle.html)  
5. Crop Factor | Woodland Hills Camera, [https://whcamera.com/crop-factor](https://whcamera.com/crop-factor)  
6. Help me understand the correlation of image circle and film format. | Photrio.com Photography Forums, [https://www.photrio.com/forum/threads/help-me-understand-the-correlation-of-image-circle-and-film-format.131498/](https://www.photrio.com/forum/threads/help-me-understand-the-correlation-of-image-circle-and-film-format.131498/)  
7. Understanding Medium Format vs 35mm Lenses and Equivalent Focal Lengths, [https://shootitwithfilm.com/understanding-medium-format-vs-35mm-lenses/](https://shootitwithfilm.com/understanding-medium-format-vs-35mm-lenses/)  
8. 'Equivalent' 35 mm format (24x36 mm) focal lengths \- Hasselblad Historical, [http://www.hasselbladhistorical.eu/HW/HWequifoc.aspx](http://www.hasselbladhistorical.eu/HW/HWequifoc.aspx)  
9. Hasselblad X-Pan Review \- Fulfilling a Vision \- By Cal Stewart \- 35mmc, [https://www.35mmc.com/07/04/2018/hasselblad-xpan-review/](https://www.35mmc.com/07/04/2018/hasselblad-xpan-review/)  
10. 127 film \- Wikipedia, [https://en.wikipedia.org/wiki/127\_film](https://en.wikipedia.org/wiki/127_film)  
11. Mamiya Press \- Wikipedia, [https://en.wikipedia.org/wiki/Mamiya\_Press](https://en.wikipedia.org/wiki/Mamiya_Press)  
12. Schneider 47mm f/5.6 Super Angulon XL \- Path to Eternal, [http://pathtoeternal.blogspot.com/2018/03/schneider-47mm-f56-super-angulon-xl.html](http://pathtoeternal.blogspot.com/2018/03/schneider-47mm-f56-super-angulon-xl.html)  
13. Schneider 47mm f/5.6 Super Angulon XL \- Ken Rockwell, [https://www.kenrockwell.com/schneider/47xl.htm](https://www.kenrockwell.com/schneider/47xl.htm)  
14. Rollei Rolleiflex Baby 4x4 Gray TLR Xenar 60mm f3.5 Tested Boxed Rare | eBay, [https://www.ebay.com/itm/397421661147](https://www.ebay.com/itm/397421661147)  
15. Rolleiflex Baby – Grey TLR Medium Format Camera \- HTF Store, [https://www.htf-store.com/products/rolleiflex-2-8e-tlr-medium-format-camera](https://www.htf-store.com/products/rolleiflex-2-8e-tlr-medium-format-camera)  
16. German folding camera — Concert and travel photographer with the passion to present beautiful and interesting images \- Dan Cuny, [https://www.dancuny.com/camera-collecting-blog/tag/German+folding+camera](https://www.dancuny.com/camera-collecting-blog/tag/German+folding+camera)  
17. 127 rollfilm cameras, [http://www.cjs-classic-cameras.co.uk/other/127\_film.html](http://www.cjs-classic-cameras.co.uk/other/127_film.html)  
18. 6x4.5/6x6 Enlarging Lens Recomendationi | Photrio.com Photography Forums, [https://www.photrio.com/forum/threads/6x4-5-6x6-enlarging-lens-recomendationi.181781/](https://www.photrio.com/forum/threads/6x4-5-6x6-enlarging-lens-recomendationi.181781/)  
19. Tessar 4.5 \- Etsy, [https://www.etsy.com/market/tessar\_4.5](https://www.etsy.com/market/tessar_4.5)  
20. The Rolleiflex Black Baby 4×4 Camera, [https://cameralegend.com/2015/07/06/the-rolleiflex-black-baby-4x4-camera/](https://cameralegend.com/2015/07/06/the-rolleiflex-black-baby-4x4-camera/)  
21. 127 Film \- The Darkroom Photo Lab, [https://thedarkroom.com/film-formats/127-film/](https://thedarkroom.com/film-formats/127-film/)  
22. Baby Rolleiflex, light painted photograph by Harold Ross, [https://www.lightpaintingworkshops.com/blog/baby-rollei](https://www.lightpaintingworkshops.com/blog/baby-rollei)  
23. film camera collectors — Concert and travel photographer with the passion to present beautiful and interesting images, [https://www.dancuny.com/camera-collecting-blog/tag/film+camera+collectors](https://www.dancuny.com/camera-collecting-blog/tag/film+camera+collectors)  
24. Fantastic plastic: Moments from a Kodak Brownie 127 \- Raymond Parker Photography, [https://raymondparkerphoto.com/fantastic-plastic-moments-from-a-kodak-brownie-127/](https://raymondparkerphoto.com/fantastic-plastic-moments-from-a-kodak-brownie-127/)  
25. Lens for spherical focal plane | Photrio.com Photography Forums, [https://www.photrio.com/forum/threads/lens-for-spherical-focal-plane.118636/](https://www.photrio.com/forum/threads/lens-for-spherical-focal-plane.118636/)  
26. Kodak Brownie 127\. Sort of… \- The Mile Cross Man, [https://themilecrossman.com/2017/10/10/kodak-brownie-127-sort-of/](https://themilecrossman.com/2017/10/10/kodak-brownie-127-sort-of/)  
27. Vintage Guillotine Shutter Guide | PDF | Camera Lens \- Scribd, [https://www.scribd.com/document/807492330/Guillotine-Shutter](https://www.scribd.com/document/807492330/Guillotine-Shutter)  
28. A Guide to Camera Shutter Designs: Focal-Plane, Leaf, and the Rest | PetaPixel, [https://petapixel.com/camera-shutter-designs/](https://petapixel.com/camera-shutter-designs/)  
29. Large Format Camera Lens Shutter \- Hackaday.io, [https://hackaday.io/project/180913-large-format-camera-lens-shutter](https://hackaday.io/project/180913-large-format-camera-lens-shutter)  
30. RBPan 35mm Panoramic Camera \- Free 3D Print Model \- MakerWorld, [https://makerworld.com/en/models/1761194-rbpan-35mm-panoramic-camera](https://makerworld.com/en/models/1761194-rbpan-35mm-panoramic-camera)  
31. A clever, mechanical take on the amazing XPan camera – without the $4000 price tag, [https://www.digitalcameraworld.com/cameras/film-cameras/a-clever-mechanical-take-on-the-xpan-without-the-usd4-000-price-tag](https://www.digitalcameraworld.com/cameras/film-cameras/a-clever-mechanical-take-on-the-xpan-without-the-usd4-000-price-tag)  
32. Schneider Super Angulon MC 47mm F5.6 Lens in black dot Copal \#0 Shutter \#1466 | eBay, [https://www.ebay.com/itm/277472976761](https://www.ebay.com/itm/277472976761)  
33. Thoughts on compact 6x6 wide-angle medium format cameras? : r/AnalogCommunity, [https://www.reddit.com/r/AnalogCommunity/comments/17yfbw4/thoughts\_on\_compact\_6x6\_wideangle\_medium\_format/](https://www.reddit.com/r/AnalogCommunity/comments/17yfbw4/thoughts_on_compact_6x6_wideangle_medium_format/)  
34. How I use a DIY Guillotine Shutter for my barrel lenses \- YouTube, [https://www.youtube.com/watch?v=M1D1mFvZgII](https://www.youtube.com/watch?v=M1D1mFvZgII)  
35. The guillotine shutter | Details \- Hackaday.io, [https://hackaday.io/project/184837/log/205586-the-guillotine-shutter](https://hackaday.io/project/184837/log/205586-the-guillotine-shutter)  
36. The Camera Eccentrica Guillotine Shutter | Teddington Tintype, [https://www.teddingtontintype.co.uk/product-page/the-camera-eccentrica-guillotine-shutter](https://www.teddingtontintype.co.uk/product-page/the-camera-eccentrica-guillotine-shutter)  
37. "guillotine camera shutter" 3D Models to Print \- yeggi \- page 2, [https://www.yeggi.com/q/guillotine+camera+shutter/2/](https://www.yeggi.com/q/guillotine+camera+shutter/2/)  
38. What is the optimal pinhole size? \- Lomography, [https://www.lomography.com/school/what-is-the-optimal-pinhole-size-fa-r1epg3l4](https://www.lomography.com/school/what-is-the-optimal-pinhole-size-fa-r1epg3l4)  
39. DIY High Capacity Panoramic Pinhole Camera \- TeamDroid, [https://www.teamdroid.com/diy-high-capacity-panoramic-pinhole-camera/](https://www.teamdroid.com/diy-high-capacity-panoramic-pinhole-camera/)  
40. Pinhole calculations \- Martin Winfield, [https://martinwinfield.co.uk/pinholetech.html](https://martinwinfield.co.uk/pinholetech.html)  
41. How to determine the appropriate size for a pinhole camera : r/PinholePhotography \- Reddit, [https://www.reddit.com/r/PinholePhotography/comments/18voqj3/how\_to\_determine\_the\_appropriate\_size\_for\_a/](https://www.reddit.com/r/PinholePhotography/comments/18voqj3/how_to_determine_the_appropriate_size_for_a/)  
42. Is the space between frames on film standardised? \- Photography Stack Exchange, [https://photo.stackexchange.com/questions/88153/is-the-space-between-frames-on-film-standardised](https://photo.stackexchange.com/questions/88153/is-the-space-between-frames-on-film-standardised)  
43. Building a 135 film format panoramic camera from old camera parts. | Photrio.com Photography Forums, [https://www.photrio.com/forum/threads/building-a-135-film-format-panoramic-camera-from-old-camera-parts.206487/](https://www.photrio.com/forum/threads/building-a-135-film-format-panoramic-camera-from-old-camera-parts.206487/)  
44. anyone know why the xpan is specifically 65:24? just curious if there is some kinda reason : r/hasselblad \- Reddit, [https://www.reddit.com/r/hasselblad/comments/15ahh9r/anyone\_know\_why\_the\_xpan\_is\_specifically\_6524/](https://www.reddit.com/r/hasselblad/comments/15ahh9r/anyone_know_why_the_xpan_is_specifically_6524/)  
45. DIY 35mm Panoramic Camera \- CAD Files and Instructions — Galen ..., [https://galenweld.com/blog/2019/5/14/diy-35mm-panoramic-camera-cad-files-and-instructions](https://galenweld.com/blog/2019/5/14/diy-35mm-panoramic-camera-cad-files-and-instructions)  
46. Using 35mm Film in a Brownie 127 to Get Exposed Sprockets \- Lomography, [https://www.lomography.com/magazine/98893-using-35mm-film-in-a-brownie-127-to-get-exposed-sprockets](https://www.lomography.com/magazine/98893-using-35mm-film-in-a-brownie-127-to-get-exposed-sprockets)  
47. Panoramic Film Camera Made From 3D Printed Parts | Hackaday, [https://hackaday.com/2026/02/20/panoramic-film-camera-made-from-3d-printed-parts/](https://hackaday.com/2026/02/20/panoramic-film-camera-made-from-3d-printed-parts/)  
48. A Deep Dive into the Adjustable Aperture Iris Diaphragm for DIY Lens Projects \- AliExpress, [https://www.aliexpress.com/s/wiki-ssr/article/Adjustable-Aperture-Iris-Diaphragm](https://www.aliexpress.com/s/wiki-ssr/article/Adjustable-Aperture-Iris-Diaphragm)  
49. Diaphragm (optics) \- Wikipedia, [https://en.wikipedia.org/wiki/Diaphragm\_(optics)](https://en.wikipedia.org/wiki/Diaphragm_\(optics\))  
50. Adjustable Aperture 1.5-26mm Iris Diaphragm M30 to M37 Goggles Lens Module DIY | eBay, [https://www.ebay.com/itm/115509240413](https://www.ebay.com/itm/115509240413)  
51. Adjustable Aperture 1.5-26mm Iris Diaphragm M30 to M37 Camera Lens Module DIY Retrofi2884 \- Walmart.ca, [https://www.walmart.ca/en/ip/Adjustable-Aperture-1-5-26mm-Iris-Diaphragm-M30-to-M37-Camera-Lens-Module-DIY-Retrofi2884/5APIFGQ6YVFA?selectedSellerId=B7A18B00F0E840C795241E0869695A2A](https://www.walmart.ca/en/ip/Adjustable-Aperture-1-5-26mm-Iris-Diaphragm-M30-to-M37-Camera-Lens-Module-DIY-Retrofi2884/5APIFGQ6YVFA?selectedSellerId=B7A18B00F0E840C795241E0869695A2A)  
52. Behind the lens Iris? Effects thereof? \- Photrio.com Photography Forums, [https://www.photrio.com/forum/threads/behind-the-lens-iris-effects-thereof.135802/](https://www.photrio.com/forum/threads/behind-the-lens-iris-effects-thereof.135802/)  
53. US5576792A \- Method for assembling an iris diaphragm \- Google Patents, [https://patents.google.com/patent/US5576792A/en](https://patents.google.com/patent/US5576792A/en)  
54. Pinhole \- Math \- Owa Moosa, [http://owamoosa.com/pinhole/pinholemath.htm](http://owamoosa.com/pinhole/pinholemath.htm)  
55. I 3d Printed a 6x24 Panoramic Medium Format Camera : r/AnalogCommunity \- Reddit, [https://www.reddit.com/r/AnalogCommunity/comments/1psatri/i\_3d\_printed\_a\_6x24\_panoramic\_medium\_format\_camera/](https://www.reddit.com/r/AnalogCommunity/comments/1psatri/i_3d_printed_a_6x24_panoramic_medium_format_camera/)  
56. 3DP3BLRD60A Mechanical shutter for 3d printing \- YouTube, [https://www.youtube.com/watch?v=E6NPXd7Fves](https://www.youtube.com/watch?v=E6NPXd7Fves)  
57. DIY 6x17 Panoramic Film Camera : 9 Steps (with Pictures) \- Instructables, [https://www.instructables.com/DIY-6x17-Panoramic-Film-Camera/](https://www.instructables.com/DIY-6x17-Panoramic-Film-Camera/)  
58. First test roll was a success\! DIY 35mm panoramic camera : r/AnalogCommunity \- Reddit, [https://www.reddit.com/r/AnalogCommunity/comments/1mj1x4p/first\_test\_roll\_was\_a\_success\_diy\_35mm\_panoramic/](https://www.reddit.com/r/AnalogCommunity/comments/1mj1x4p/first_test_roll_was_a_success_diy_35mm_panoramic/)  
59. Mamiya 6 \- Ken Rockwell, [https://www.kenrockwell.com/mamiya/6.htm](https://www.kenrockwell.com/mamiya/6.htm)  
60. 50mm Lens comparison II – Overview, [https://mbphotox.wordpress.com/2015/12/22/overview/](https://mbphotox.wordpress.com/2015/12/22/overview/)

