---
name: excalidraw
description: Hand-drawn Excalidraw JSON diagrams (arch, flow, seq).
metadata:
  tags: [excalidraw, diagram, hand-drawn, json]
  tier: task-specific
  domain: creative
when_to_apply: >
  When producing hand-drawn Excalidraw diagrams (architecture, flow, sequence).
---

# Excalidraw Diagram Skill

Create diagrams by writing standard Excalidraw element JSON and saving as `.excalidraw` files. These files can be drag-and-dropped onto [excalidraw.com](https://excalidraw.com) for viewing and editing. No accounts, no API keys, no rendering libraries -- just JSON.

## When to use

Generate `.excalidraw` files for architecture diagrams, flowcharts, sequence diagrams, concept maps, and more. Files can be opened at excalidraw.com or uploaded for shareable links.

## Workflow

1. **Load this skill** (you already did)
2. **Write the elements JSON** -- an array of Excalidraw element objects
3. **Save the file** using `write_file` to create a `.excalidraw` file
4. **Optionally upload** for a shareable link using `scripts/upload.py` via `terminal`

### Saving a Diagram

Wrap your elements array in the standard `.excalidraw` envelope and save with `write_file`:

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "hermes-agent",
  "elements": [ ...your elements array here... ],
  "appState": {
    "viewBackgroundColor": "#ffffff"
  }
}
```

Save to any path, e.g. `~/diagrams/my_diagram.excalidraw`.

### Uploading for a Shareable Link

Run the upload script (located in this skill's `scripts/` directory) via terminal:

```bash
python skills/diagramming/excalidraw/scripts/upload.py ~/diagrams/my_diagram.excalidraw
```

This uploads to excalidraw.com (no account needed) and prints a shareable URL. Requires the `cryptography` pip package (`pip install cryptography`).

---

## Fallback: ImageMagick CLI for PNG Generation

When `execute_code` sandbox lacks PIL/matplotlib **and** Playwright times out on external sites, use ImageMagick (`magick`) to generate PNG diagrams programmatically.

### When to Use
- Python imaging libraries unavailable in sandbox
- Need immediate PNG output without external dependencies
- Excalidraw JSON exists but screenshot generation failing

### Prerequisites
```bash
# Verify ImageMagick is available
which magick || which convert
```

### Basic Pattern

```bash
# 1. Create base canvas
magick -size 1600x1200 xc:#fafafa base.png

# 2. Add title and text
magick base.png \
  -fill '#1e1e1e' -font Arial -pointsize 28 -gravity center \
  -annotate +0+-550 'Diagram Title' \
  output.png

# 3. Draw boxes
magick output.png \
  -fill '#a5d8ff' -stroke '#495057' -strokewidth 2 \
  -draw 'roundrectangle 100,100 300,200 10,10' \
  -fill '#1e1e1e' -pointsize 12 \
  -annotate +150+150 'Box Label' \
  final.png
```

### Key Commands

| Task | ImageMagick Syntax |
|------|-------------------|
| Rounded rectangle | `-draw 'roundrectangle x1,y1 x2,y2 rx,ry'` |
| Text annotation | `-annotate +x+y 'text'` (use `-gravity` for relative) |
| Lines/arrows | `-draw 'line x1,y1 x2,y2'` + polygon for arrowhead |
| Composite | `magick base.png -draw '...' output.png` (chained) |

### Color Reference (same palette as Excalidraw)
```
#d0bfff  Light Purple (Processing/Special)
#b2f2bb  Light Green  (Success/Running)
#ffc9c9  Light Red    (Error/Crashed)
#ffd8a8  Light Orange (Warning/External)
#a5d8ff  Light Blue   (Primary/Input)
#c3fae8  Light Teal   (Storage/Data)
```

### Full Example: System Architecture Diagram

See `references/imagemagick-patterns.md` for complete working examples including:
- Multi-layer diagram with 50+ elements
- Status color coding
- Arrow connections between components
- Legend and status boxes

### Combining with Excalidraw

1. Generate Excalidraw JSON for interactive editing
2. If screenshot fails, use ImageMagick to create equivalent PNG
3. Share both: PNG for immediate viewing, Excalidraw link for editing

---

## Element Format Reference

### Required Fields (all elements)
`type`, `id` (unique string), `x`, `y`, `width`, `height`

### Defaults (skip these -- they're applied automatically)
- `strokeColor`: `"#1e1e1e"`
- `backgroundColor`: `"transparent"`
- `fillStyle`: `"solid"`
- `strokeWidth`: `2`
- `roughness`: `1` (hand-drawn look)
- `opacity`: `100`

Canvas background is white.

### Element Types

**Rectangle**:
```json
{ "type": "rectangle", "id": "r1", "x": 100, "y": 100, "width": 200, "height": 100 }
```
- `roundness: { "type": 3 }` for rounded corners
- `backgroundColor: "#a5d8ff"`, `fillStyle: "solid"` for filled

**Ellipse**:
```json
{ "type": "ellipse", "id": "e1", "x": 100, "y": 100, "width": 150, "height": 150 }
```

**Diamond**:
```json
{ "type": "diamond", "id": "d1", "x": 100, "y": 100, "width": 150, "height": 150 }
```

**Labeled shape (container binding)** -- create a text element bound to the shape:

> **WARNING:** Do NOT use `"label": { "text": "..." }` on shapes. This is NOT a valid
> Excalidraw property and will be silently ignored, producing blank shapes. You MUST
> use the container binding approach below.

The shape needs `boundElements` listing the text, and the text needs `containerId` pointing back:
```json
{ "type": "rectangle", "id": "r1", "x": 100, "y": 100, "width": 200, "height": 80,
  "roundness": { "type": 3 }, "backgroundColor": "#a5d8ff", "fillStyle": "solid",
  "boundElements": [{ "id": "t_r1", "type": "text" }] },
{ "type": "text", "id": "t_r1", "x": 105, "y": 110, "width": 190, "height": 25,
  "text": "Hello", "fontSize": 20, "fontFamily": 1, "strokeColor": "#1e1e1e",
  "textAlign": "center", "verticalAlign": "middle",
  "containerId": "r1", "originalText": "Hello", "autoResize": true }
```
- Works on rectangle, ellipse, diamond
- Text is auto-centered by Excalidraw when `containerId` is set
- The text `x`/`y`/`width`/`height` are approximate -- Excalidraw recalculates them on load
- `originalText` should match `text`
- Always include `fontFamily: 1` (Virgil/hand-drawn font)

**Labeled arrow** -- same container binding approach:
```json
{ "type": "arrow", "id": "a1", "x": 300, "y": 150, "width": 200, "height": 0,
  "points": [[0,0],[200,0]], "endArrowhead": "arrow",
  "boundElements": [{ "id": "t_a1", "type": "text" }] },
{ "type": "text", "id": "t_a1", "x": 370, "y": 130, "width": 60, "height": 20,
  "text": "connects", "fontSize": 16, "fontFamily": 1, "strokeColor": "#1e1e1e",
  "textAlign": "center", "verticalAlign": "middle",
  "containerId": "a1", "originalText": "connects", "autoResize": true }
```

**Standalone text** (titles and annotations only -- no container):
```json
{ "type": "text", "id": "t1", "x": 150, "y": 138, "text": "Hello", "fontSize": 20,
  "fontFamily": 1, "strokeColor": "#1e1e1e", "originalText": "Hello", "autoResize": true }
```
- `x` is the LEFT edge. To center at position `cx`: `x = cx - (text.length * fontSize * 0.5) / 2`
- Do NOT rely on `textAlign` or `width` for positioning

**Arrow**:
```json
{ "type": "arrow", "id": "a1", "x": 300, "y": 150, "width": 200, "height": 0,
  "points": [[0,0],[200,0]], "endArrowhead": "arrow" }
```
- `points`: `[dx, dy]` offsets from element `x`, `y`
- `endArrowhead`: `null` | `"arrow"` | `"bar"` | `"dot"` | `"triangle"`
- `strokeStyle`: `"solid"` (default) | `"dashed"` | `"dotted"`

### Arrow Bindings (connect arrows to shapes)

```json
{
  "type": "arrow", "id": "a1", "x": 300, "y": 150, "width": 150, "height": 0,
  "points": [[0,0],[150,0]], "endArrowhead": "arrow",
  "startBinding": { "elementId": "r1", "fixedPoint": [1, 0.5] },
  "endBinding": { "elementId": "r2", "fixedPoint": [0, 0.5] }
}
```

`fixedPoint` coordinates: `top=[0.5,0]`, `bottom=[0.5,1]`, `left=[0,0.5]`, `right=[1,0.5]`

### Drawing Order (z-order)
- Array order = z-order (first = back, last = front)
- Emit progressively: background zones → shape → its bound text → its arrows → next shape
- BAD: all rectangles, then all texts, then all arrows
- GOOD: bg_zone → shape1 → text_for_shape1 → arrow1 → arrow_label_text → shape2 → text_for_shape2 → ...
- Always place the bound text element immediately after its container shape

### Sizing Guidelines

**Font sizes:**
- Minimum `fontSize`: **16** for body text, labels, descriptions
- Minimum `fontSize`: **20** for titles and headings
- Minimum `fontSize`: **14** for secondary annotations only (sparingly)
- NEVER use `fontSize` below 14

**Element sizes:**
- Minimum shape size: 120x60 for labeled rectangles/ellipses
- Leave 20-30px gaps between elements minimum
- Prefer fewer, larger elements over many tiny ones

### Color Palette

See `references/colors.md` for full color tables. Quick reference:

| Use | Fill Color | Hex |
|-----|-----------|-----|
| Primary / Input | Light Blue | `#a5d8ff` |
| Success / Output | Light Green | `#b2f2bb` |
| Warning / External | Light Orange | `#ffd8a8` |
| Processing / Special | Light Purple | `#d0bfff` |
| Error / Critical | Light Red | `#ffc9c9` |
| Notes / Decisions | Light Yellow | `#fff3bf` |
| Storage / Data | Light Teal | `#c3fae8` |

### Tips
- Use the color palette consistently across the diagram
- **Text contrast is CRITICAL** -- never use light gray on white backgrounds. Minimum text color on white: `#757575`
- Do NOT use emoji in text -- they don't render in Excalidraw's font
- For dark mode diagrams, see `references/dark-mode.md`
- For larger examples, see `references/examples.md`
- **For ImageMagick CLI patterns** (fallback when Python unavailable), see `references/imagemagick-patterns.md`

---

## When the User Asks for a Screenshot

### Common User Request Pattern
> "Can you make a diagram... and share a screenshot of it here?"

### Failure Mode to Avoid
**DON'T** silently try multiple failing approaches (PIL → matplotlib → Playwright → ImageMagick) while the user waits and wonders why nothing is appearing. This creates frustration.

**DON'T** say "the screenshot isn't working" without explaining why or offering the alternative.

### Correct Workflow

1. **Acknowledge the request** and set expectations immediately:
   > "I'll create the diagram. For screenshots, I need to check which rendering tools are available in this environment."

2. **Check tool availability first** (one quick command):
   ```bash
   python3 -c "from PIL import Image; print('PIL ok')" 2>/dev/null || echo "PIL unavailable"
   ```

3. **If PIL/matplotlib unavailable** (common in sandboxes), **immediately pivot**:
   > "The Python imaging libraries aren't available here. I'll generate the diagram as Excalidraw JSON and provide a shareable link you can view instantly — you can also edit it there."

4. **Provide BOTH outputs**:
   - Excalidraw JSON file (for editing)
   - Shareable link via `scripts/upload.py` (for immediate viewing)

5. **If user insists on PNG** (e.g., for embedding in Discord), use ImageMagick CLI as fallback, but **warn about text rendering limitations**:
   > "I can generate a PNG via ImageMagick, but text rendering may have glyph issues. The Excalidraw link above will look better."

### Decision Tree

```
User: "Share a screenshot"
│
├─ PIL/matplotlib available? ──→ Generate PNG with Python ──→ MEDIA:/path/to.png
│
├─ PIL unavailable ──→ 
│   ├─ Generate Excalidraw JSON ──→ Upload ──→ Share link
│   └─ Tell user: "Best viewable at [link] (interactive)"
│
└─ User specifically needs PNG ──→ ImageMagick CLI ──→ Warn about text quality
```

### Response Template

**Good response** (user gets useful output quickly):
```
I've created your diagram as an interactive Excalidraw. 

🔗 **View here:** https://excalidraw.com/#json=...

The Python imaging tools aren't available in this environment, so I can't generate a direct PNG screenshot. The link above lets you view, zoom, and edit the diagram instantly — no account needed.

Want me to also try a PNG via ImageMagick? (Text may not render perfectly.)
```

**What NOT to say** (leaves user confused):
```
"The screenshot isn't working."
"I tried PIL, matplotlib, Playwright, and ImageMagick but they all failed."
"Let me try again..." [repeats failures]
```

---

## Common Tool Failures & Solutions

| Failure | Cause | Solution |
|---------|-------|----------|
| `ModuleNotFoundError: PIL` | Sandbox lacks Pillow | Use ImageMagick CLI, or provide Excalidraw link |
| `matplotlib not available` | Same as above | Same |
| Playwright timeout | Excalidraw canvas heavy/complex | Skip screenshot, use upload.py for shareable link |
| ImageMagick text garbled | Font rendering issues | Use larger fonts (-pointsize 16+), simpler labels |
| MEDIA: tag doesn't attach | Binary read not supported | Use direct file path, or share Excalidraw link |
