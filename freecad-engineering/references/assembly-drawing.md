# Assembly Engineering Drawing

## Minimum A3 content

- border and title block;
- drawing title and drawing number;
- declared scale and projection convention;
- principal front view and a complementary side or section view;
- centerlines and center marks;
- overall height, width, depth, and mounting dimensions available from evidence;
- item balloons that map unambiguously to the BOM;
- BOM with item, part number or standard, name, quantity, and material;
- section hatching where hidden interfaces matter;
- technical notes and fits when supplied.

## Geometry generation

Generate view curves from accepted assembly solids using TechDraw or `TechDraw.projectToSVG`. Normalize rotation, scale, and placement deliberately. Keep projection geometry separate from annotation layers.

Use extension lines for dimensions. Do not leave dimension arrows floating without a geometric relationship to the measured feature. Use thin centerline patterns distinct from visible outlines.

For repeated fasteners, one balloon can identify the item when the BOM quantity is clear. Every BOM item must still be locatable in at least one view or section.

## Export verification

Keep SVG as editable source. Export PDF at the exact sheet size and verify the PDF media box. For A3 landscape, expect approximately 420 x 297 mm.

Rasterize to PNG and inspect:

- missing or boxed Chinese characters;
- line clipping and excessive line weight;
- crossed or ambiguous leaders;
- text outside cells;
- balloons overlapping geometry or dimensions;
- blank or rotated projections.

Qt headless SVG rendering can replace CJK text with boxes when fonts are unavailable. Use a Windows browser print engine or another renderer that can access installed CJK fonts, and recheck the raster result.
