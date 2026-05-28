---

name: ascii-art
description: >
  Generate ASCII art using pyfiglet (571 fonts), cowsay, boxes, toilet,
  image-to-ascii, remote APIs (asciified, ascii.co.uk), and LLM fallback. No API
  keys required.
metadata:
  tags: [ascii, text-art, terminal, decoration]
  tier: task-specific
  domain: creative
when_to_apply: >
  When generating ASCII art (pyfiglet, cowsay, boxes, toilet, image-to-ASCII).
---
# ASCII Art Skill

Multiple tools for different ASCII art needs. All tools are local CLI programs or free REST APIs — no API keys required.

## Tool 1: Text Banners (pyfiglet — local)

Render text as large ASCII art banners. 571 built-in fonts.

### Setup

```bash
pip install pyfiglet --break-system-packages -q
```

### Usage

```bash
python3 -m pyfiglet "YOUR TEXT" -f slant
python3 -m pyfiglet "TEXT" -f doom -w 80    # Set width
python3 -m pyfiglet --list_fonts             # List all 571 fonts
```

### Recommended fonts

| Style | Font | Best for |
|-------|------|----------|
| Clean & modern | `slant` | Project names, headers |
| Bold & blocky | `doom` | Titles, logos |
| Big & readable | `big` | Banners |
| Classic banner | `banner3` | Wide displays |
| Compact | `small` | Subtitles |
| Cyberpunk | `cyberlarge` | Tech themes |
| 3D effect | `3-d` | Splash screens |
| Gothic | `gothic` | Dramatic text |

### Tips

- Preview 2-3 fonts and let the user pick their favorite
- Short text (1-8 chars) works best with detailed fonts like `doom` or `block`
- Long text works better with compact fonts like `small` or `mini`

## Tool 2: Text Banners (asciified API — remote, no install)

Free REST API that converts text to ASCII art. 250+ FIGlet fonts. Returns plain text directly — no parsing needed. Use this when pyfiglet is not installed or as a quick alternative.

### Usage (via terminal curl)

```bash
# Basic text banner (default font)
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello+World"

# With a specific font
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=Slant"
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=Doom"
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=Star+Wars"
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=3-D"
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=Banner3"

# List all available fonts (returns JSON array)
curl -s "https://asciified.thelicato.io/api/v2/fonts"
```

### Tips

- URL-encode spaces as `+` in the text parameter
- The response is plain text ASCII art — no JSON wrapping, ready to display
- Font names are case-sensitive; use the fonts endpoint to get exact names
- Works from any terminal with curl — no Python or pip needed

## Tool 3: Cowsay (Message Art)

Classic tool that wraps text in a speech bubble with an ASCII character.

### Setup

```bash
# Option A: Traditional Perl cowsay (system package manager)
sudo apt install cowsay -y    # Debian/Ubuntu
brew install cowsay           # macOS

# Option B: Python cowsay (pip - different CLI syntax!)
pip install cowsay
```

### Usage

**Perl cowsay (system install):**
```bash
cowsay "Hello World"
cowsay -f tux "Linux rules"       # Tux the penguin
cowsay -f dragon "Rawr!"          # Dragon
cowsay -f stegosaurus "Roar!"     # Stegosaurus
cowthink "Hmm..."                  # Thought bubble
cowsay -l                          # List all characters
```

**Python cowsay (pip install) - NOTE: Different flags!**
```bash
cowsay -t "Hello World"                            # -t for text (REQUIRED)
cowsay -c tux -t "Linux rules"                     # -c for character
cowsay -c dragon -t "Rawr!"
cowsay -c stegosaurus -t "Roar!"
cowsay --character list                            # List available characters
cowsay -h                                          # Full help
```

⚠️ **Critical difference:** Python cowsay uses `-c`/`--character` and `-t`/`--text` flags,
not positional arguments like the Perl version. The character name may also differ slightly.

### Available Characters

**Perl cowsay:** 50+ characters including:
`beavis.zen`, `bong`, `bunny`, `cheese`, `daemon`, `default`, `dragon`, `dragon-and-cow`, `elephant`, `eyes`, `flaming-skull`, `ghostbusters`, `hellokitty`, `kiss`, `kitty`, `koala`, `luke-koala`, `mech-and-cow`, `meow`, `moofasa`, `moose`, `ren`, `sheep`, `skeleton`, `small`, `stegosaurus`, `stimpy`, `supermilker`, `surgery`, `three-eyes`, `turkey`, `turtle`, `tux`, `udder`, `vader`, `vader-koala`, `www`

**Python cowsay:** Different set, check with `cowsay --character list`
Common ones: `beavis`, `cheese`, `cow`, `daemon`, `dragon`, `fox`, `ghostbusters`, `kitty`, `meow`, `miki`, `milk`, `octopus`, `pig`, `stegosaurus`, `stimpy`, `trex`, `turkey`, `turtle`, `tux`

Note: `skeleton` is NOT in Python cowsay (use `daemon` or `ghostbusters` instead for spooky themes).

### Eye/tongue modifiers (Perl cowsay only)

Python cowsay does NOT support eye/tongue modifiers. Use Perl version for:

```bash
cowsay -b "Borg"       # =_= eyes
cowsay -d "Dead"       # x_x eyes
cowsay -g "Greedy"     # $_$ eyes
cowsay -p "Paranoid"   # @_@ eyes
cowsay -s "Stoned"     # *_* eyes
cowsay -w "Wired"      # O_O eyes
cowsay -e "OO" "Msg"   # Custom eyes
cowsay -T "U " "Msg"   # Custom tongue
```

## Tool 4: Boxes (Decorative Borders)

Draw decorative ASCII art borders/frames around any text. 70+ built-in designs.

### Setup

```bash
sudo apt install boxes -y    # Debian/Ubuntu
# brew install boxes         # macOS
```

### Usage

```bash
echo "Hello World" | boxes                    # Default box
echo "Hello World" | boxes -d stone           # Stone border
echo "Hello World" | boxes -d parchment       # Parchment scroll
echo "Hello World" | boxes -d cat             # Cat border
echo "Hello World" | boxes -d dog             # Dog border
echo "Hello World" | boxes -d unicornsay      # Unicorn
echo "Hello World" | boxes -d diamonds        # Diamond pattern
echo "Hello World" | boxes -d c-cmt           # C-style comment
echo "Hello World" | boxes -d html-cmt        # HTML comment
echo "Hello World" | boxes -a c               # Center text
boxes -l                                       # List all 70+ designs
```

### Combine with pyfiglet or asciified

```bash
python3 -m pyfiglet "HERMES" -f slant | boxes -d stone
# Or without pyfiglet installed:
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=HERMES&font=Slant" | boxes -d stone
```

## Tool 5: TOIlet (Colored Text Art)

Like pyfiglet but with ANSI color effects and visual filters. Great for terminal eye candy.

### Setup

```bash
sudo apt install toilet toilet-fonts -y    # Debian/Ubuntu
# brew install toilet                      # macOS
```

### Usage

```bash
toilet "Hello World"                    # Basic text art
toilet -f bigmono12 "Hello"            # Specific font
toilet --gay "Rainbow!"                 # Rainbow coloring
toilet --metal "Metal!"                 # Metallic effect
toilet -F border "Bordered"             # Add border
toilet -F border --gay "Fancy!"         # Combined effects
toilet -f pagga "Block"                 # Block-style font (unique to toilet)
toilet -F list                          # List available filters
```

### Filters

`crop`, `gay` (rainbow), `metal`, `flip`, `flop`, `180`, `left`, `right`, `border`

**Note**: toilet outputs ANSI escape codes for colors — works in terminals but may not render in all contexts (e.g., plain text files, some chat platforms).

## Tool 6: Image to ASCII Art

Convert images (PNG, JPEG, GIF, WEBP) to ASCII art.

### Option A: ascii-image-converter (recommended, modern)

```bash
# Install
sudo snap install ascii-image-converter
# OR: go install github.com/TheZoraiz/ascii-image-converter@latest
```

```bash
ascii-image-converter image.png                  # Basic
ascii-image-converter image.png -C               # Color output
ascii-image-converter image.png -d 60,30         # Set dimensions
ascii-image-converter image.png -b               # Braille characters
ascii-image-converter image.png -n               # Negative/inverted
ascii-image-converter https://url/image.jpg      # Direct URL
ascii-image-converter image.png --save-txt out   # Save as text
```

### Option B: jp2a (lightweight, JPEG only)

```bash
sudo apt install jp2a -y
jp2a --width=80 image.jpg
jp2a --colors image.jpg              # Colorized
```

## Tool 7: Search Pre-Made ASCII Art

Search curated ASCII art from the web. Use `terminal` with `curl`.

### Source A: ascii.co.uk (recommended for pre-made art)

Large collection of classic ASCII art organized by subject. Art is inside HTML `<pre>` tags. Fetch the page with curl, then extract art with a small Python snippet.

**URL pattern:** `https://ascii.co.uk/art/{subject}`

**Step 1 — Fetch the page:**

```bash
curl -s 'https://ascii.co.uk/art/cat' -o /tmp/ascii_art.html
```

**Step 2 — Extract art from pre tags:**

```python
import re, html
with open('/tmp/ascii_art.html') as f:
    text = f.read()
arts = re.findall(r'<pre[^>]*>(.*?)</pre>', text, re.DOTALL)
for art in arts:
    clean = re.sub(r'<[^>]+>', '', art)
    clean = html.unescape(clean).strip()
    if len(clean) > 30:
        print(clean)
        print('\n---\n')
```

**Available subjects** (use as URL path):
- Animals: `cat`, `dog`, `horse`, `bird`, `fish`, `dragon`, `snake`, `rabbit`, `elephant`, `dolphin`, `butterfly`, `owl`, `wolf`, `bear`, `penguin`, `turtle`
- Objects: `car`, `ship`, `airplane`, `rocket`, `guitar`, `computer`, `coffee`, `beer`, `cake`, `house`, `castle`, `sword`, `crown`, `key`
- Nature: `tree`, `flower`, `sun`, `moon`, `star`, `mountain`, `ocean`, `rainbow`
- Characters: `skull`, `robot`, `angel`, `wizard`, `pirate`, `ninja`, `alien`
- Holidays: `christmas`, `halloween`, `valentine`

**Tips:**
- Preserve artist signatures/initials — important etiquette
- Multiple art pieces per page — pick the best one for the user
- Works reliably via curl, no JavaScript needed

### Source B: GitHub Octocat API (fun easter egg)

Returns a random GitHub Octocat with a wise quote. No auth needed.

```bash
curl -s https://api.github.com/octocat
```

## Tool 8: Fun ASCII Utilities (via curl)

These free services return ASCII art directly — great for fun extras.

### QR Codes as ASCII Art

```bash
curl -s "qrenco.de/Hello+World"
curl -s "qrenco.de/https://example.com"
```

### Weather as ASCII Art

```bash
curl -s "wttr.in/London"          # Full weather report with ASCII graphics
curl -s "wttr.in/Moon"            # Moon phase in ASCII art
curl -s "v2.wttr.in/London"       # Detailed version
```

## Tool 9: LLM-Generated Custom Art (Fallback)

When tools above don't have what's needed, generate ASCII art directly using these Unicode characters:

### Character Palette

**Box Drawing:** `╔ ╗ ╚ ╝ ║ ═ ╠ ╣ ╦ ╩ ╬ ┌ ┐ └ ┘ │ ─ ├ ┤ ┬ ┴ ┼ ╭ ╮ ╰ ╯`

**Block Elements:** `░ ▒ ▓ █ ▄ ▀ ▌ ▐ ▖ ▗ ▘ ▝ ▚ ▞`

**Geometric & Symbols:** `◆ ◇ ◈ ● ○ ◉ ■ □ ▲ △ ▼ ▽ ★ ☆ ✦ ✧ ◀ ▶ ◁ ▷ ⬡ ⬢ ⌂`

### Rules

- Max width: 60 characters per line (terminal-safe)
- Max height: 15 lines for banners, 25 for scenes
- Monospace only: output must render correctly in fixed-width fonts

## Tool 10: Intense/Bold Logo Design with Platform Constraints

Workflow for creating maximum-impact logos (Discord, banners, headers) that must fit within character limits. This follows an iterative "build big → measure → trim" cycle based on user feedback.

### Real-World Example: The Swarmers Logo

**Round 1 — Initial options (too tame):**
Started with simple cowsay mascots + pyfiglet text. User said: *"needs to be bigger and bolder and more intense"*

**Round 2 — Maximum intensity (too big):**
- Full block letters (███)
- Double borders with inner tagline boxes
- 12-bee swarm formation + 10-drone army
- Heavy Unicode everywhere (█ ▓ ▄▀ ╔═╗)
- **Result: 2616 chars** — OVER Discord limit

**Round 3 — Trimmed to fit (just right):**
- Reduced border thickness on lower section
- Trimmed drone army from 10 → 8 units
- Removed one decorative layer
- **Result: 1973 chars** — Discord-safe with 27 char buffer

**Final formula that worked:**
```
Top banner (Block letters with full borders)
+ Middle tagline box (╔═╗ double-line frame)
+ Bee swarm separator (▄▀ pattern with ▓ bodies)
+ Bottom drone army (simplified ▓ formation)
= 1973 chars of maximum intensity
```

### The "Go Big Then Trim" Method

**Step 1 — Generate base text at maximum intensity:**
```bash
# Get multiple font options
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=SWARMERS&font=Block"
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=SWARMERS&font=Big"
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=SWARMERS&font=Doom"
```

**Step 2 — Add intensity layers:**
- Wrap in heavy Unicode borders (█ ▓ ▄▀)
- Add mascot art above/below using Block Elements
- Use double borders (╔═╗ / ███) for impact

**Step 3 — Check constraints and iterate:**
```python
# Check character count
art = """YOUR_ASCII_ART_HERE"""
count = len(art)
print(f"Length: {count}")

# Platform limits:
# Discord: ~2000 chars (mobile renders best under ~100 lines)
# Most terminals: ~80 columns
```

**Step 4 — Trim strategically:**
- Reduce border thickness (████ → ██ → █)
- Shorten taglines
- Remove decorative layers while keeping core impact
- Target: stay 50-100 chars UNDER limit for safety

### When User Says "More Intense"

Common escalation path:
1. **Add borders** → single line → double line → heavy blocks
2. **Thicken mascot** → simple chars → ░ → ▒ → ▓ → █ blocks
3. **Layer effects** → text only → bordered text → text + separators + footer art
4. **Measure after each** — intensity increases size exponentially

### Platform-Specific Limits

| Platform | Char Limit | Width | Notes |
|----------|-----------|-------|-------|
| Discord | ~2000 | ~80 | Mobile cuts off wide lines |
| Discord embed | ~6000 | ~80 | Use code blocks (```) |
| Terminal | unlimited | 80-120 | Default to 80 for safety |
| SMS | 160 | 40 | Rarely use ASCII art here |

### Example: Discord-Safe Intense Logo (1973 chars)

```python
# Target: <2000 chars, max visual impact
logo = """
████████████████████████████████████████████████████████████████████████████████
██    ██╗    ██╗███████╗    ███████╗██╗    ██╗ █████╗ ██████╗ ███╗   ███╗     ██
██    ██║    ██║██╔════╝    ██╔════╝██║    ██║██╔══██╗██╔══██╗████╗ ████║     ██
██    ██║ █╗ ██║███████╗    ███████╗██║ █╗ ██║███████║██████╔╝██╔████╔██║     ██
██    ██║███╗██║╚════██║    ╚════██║██║███╗██║██╔══██║██╔══██╗██║╚██╔╝██║     ██
██    ╚███╔███╔╝███████║    ███████║╚███╔███╔╝██║  ██║██║  ██║██║ ╚═╝ ██║     ██
██     ╚══╝╚══╝ ╚══════╝    ╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝     ██
██                                                                            ██
██               ╔═══════════════════════════════════════╗                   ██
██               ║   >>>  WE  ARE  THE  SWARMERS  <<<    ║                   ██
██               ║       >>>  WE  ARE  LEGION  <<<       ║                   ██
██               ╚═══════════════════════════════════════╝                   ██
██                                                                            ██
██      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄        ██
██    ▄▀ ▄▄▄ ▄▄▄ ▄▄▄ ▄▄▄ ▄▄▄ ▄▄▄ ▄▄▄ ▄▄▄ ▄▄▄ ▄▄▄ ▄▄▄ ▄▄▄ ▄▄▄ ▀▄      ██
██   █░ ▐██▌▐██▌▐██▌▐██▌▐██▌▐██▌▐██▌▐██▌▐██▌▐██▌▐██▌▐██▌ ░█     ██
██  █░░ ▀▀▀ ▀▀▀ ▀▀▀ ▀▀▀ ▀▀▀ ▀▀▀ ▀▀▀ ▀▀▀ ▀▀▀ ▀▀▀ ▀▀▀ ▀▀▀ ░░█    ██
██  █▄░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▄█    ██
██    ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀      ██
████████████████████████████████████████████████████████████████████████████████

     ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
   ▄▀▀ ▓▓▓▓▓ ▓▓▓▓▓ ▓▓▓▓▓ ▓▓▓▓▓ ▓▓▓▓▓ ▓▓▓▓▓ ▓▓▓▓▓ ▓▓▓▓▓ ▀▀▄
  █░ ▓▓░░░▓▓▓░░░▓▓▓░░░▓▓▓░░░▓▓▓░░░▓▓▓░░░▓▓ ░█
 █░░ ▓▓░░░▓▓▓░░░▓▓▓░░░▓▓▓░░░▓▓▓░░░▓▓▓░░░▓▓ ░░█
 █░ ▓▓▓▓▓ ▓▓▓▓▓ ▓▓▓▓▓ ▓▓▓▓▓ ▓▓▓▓▓ ▓▓▓▓▓ ▓▓▓▓▓ ░█
█▄░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▄█
  ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
"""
# Check: 1973 chars — perfect for Discord
```

### Pre-Built Mascot Patterns (Copy-Paste Ready)

**Bee/Swarm Formation:**
```
     ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
  ▄▀▀ ▓▓▓▓▓ ▓▓▓▓▓ ▓▓▓▓▓ ▓▓▓▓▓ ▓▓▓▓▓ ▀▀▄
 █░ ▓▓░░░▓▓▓░░░▓▓▓░░░▓▓▓░░░▓▓▓░░░▓▓ ░█
█▄░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▄█
```

**Heavy Border Box with Tagline:**
```
╔═══════════════════════════════════════════════════╗
║   >>>  YOUR TAGLINE HERE  <<<                   ║
╚═══════════════════════════════════════════════════╝
```

**Block Element Gradient:**
```
# For vertical intensity falloff:
████ (top — most intense)
▓▓▓▓
▒▒▒▒
░░░░ (bottom — lightest)
```

### Combining Techniques for Maximum Effect

Best intense logos mix:
1. **Text banner** from asciified API (Block/Big/Doom fonts)
2. **Heavy borders** using Unicode Block Elements (█)
3. **Custom mascot art** between borders using ▓ ▄▀ patterns
4. **Tagline** in box-drawing characters (╔═╗)

### Unicode Intensity Palette

**Heavy borders:** `█ ▓ ▒ ░` (solid → light)
**Outline borders:** `▄ ▀ ▌ ▐` (half blocks)
**Box drawing:** `╔ ═ ╗ ║ ╚ ╝` (double-line frames)
**Corner pieces:** `┌ ┐ └ ┘` (single-line frames)

### Rules for Intense Logos

- **Build big first** — don't design to the constraint initially
- **Measure after every addition** — use `len()` to check
- **Trim in stages** — reduce one layer at a time
- **Keep 50-100 chars buffer** — platforms sometimes count differently
- **Test monospace rendering** — all art must use fixed-width fonts
- **Iterate on feedback** — "bigger and bolder" usually means add borders/thickness, not just more characters

## Agent Fleet Backroom: Creative Critique Workflow

For multi-agent creative collaboration, establish a peer review pipeline:

### The Pattern

```
Generate → Post → Issue → Critique → Synthesize → Document
```

**Step 1: Generate** — Create 2-4 variations using tools above (pyfiglet, custom Unicode, cowsay)

**Step 2: Post** — Send to Discord #general (or designated backroom channel) with descriptive labels

**Step 3: Issue** — Create Paperclip issue assigned to Knowledge Curator (e.g., Scribe):
- Title: "[Creative Type] Showcase: [Name] — Agent Critique Requested"
- Checklist dimensions: Aesthetic, Hierarchy, Typography, Brand alignment, Technical rendering
- Explicit call for agent reactions (👍) and threaded feedback

**Step 4: Critique** — Agents respond in Discord thread, Knowledge Curator monitors

**Step 5: Synthesize** — Assigned agent consolidates feedback, identifies consensus winner

**Step 6: Document** — Final design + critique summary written to vault knowledge base (visual identity section)

### Example Implementation

**Posted art:** ASCII formation diagram showing 13-agent hierarchy
**Issue EDGA-249:** Assigned to Scribe, labeled [creative, ascii-art, brand-identity, critique]
**Critique dimensions:** 
- [ ] Does formation reflect actual org hierarchy?
- [ ] Unicode intensity appropriate for brand?
- [ ] Mobile rendering issues?
- [ ] Evolution suggestions for v2

**Deliverable:** Consensus → official fleet visual → vault documentation

### Why This Matters

User explicitly desires "backroom" feedback — creative decisions by swarm consensus, not single-agent output. Treats Discord as collaborative space, not just broadcast.

---

## Discord Integration

Posting ASCII art to Discord requires specific formatting and has platform constraints.

### Character Limits

| Discord Feature | Limit |
|----------------|-------|
| Regular message | ~2000 chars |
| Code block (```) | Same limit, but preserves formatting |
| Embeds | ~6000 chars total |
| Mobile display | ~100 lines before truncation |

### Formatting for Discord

Always wrap ASCII art in triple backticks to preserve monospace:

```python
art = """```
[YOUR ASCII ART HERE]
```"""
```

Escape backslashes properly for Python strings sent to Discord:
- Single `\` → `\\` in Python strings
- Double `\\` → `\\\\` for art with many backslashes

### Posting Methods

**Method 1: Bot Token (discord.py)**
```python
import discord

class Poster(discord.Client):
    async def on_ready(self):
        channel = self.get_channel(CHANNEL_ID)
        await channel.send("```\n" + ascii_art + "\n```")
        await self.close()

client = Poster(intents=discord.Intents.default())
client.run(TOKEN)
```

**⚠️ Common Issue**: Bot tokens expire or get 401 Unauthorized if:
- Token was regenerated in Discord Developer Portal
- Bot permissions changed
- IP/location flagged (try same network as existing bot)

**Workaround**: Use webhook or provide formatted text for manual copy-paste.

**Method 2: Webhook (Most Reliable)**
```bash
WEBHOOK="https://discord.com/api/webhooks/..."

# Escape properly for JSON
curl -X POST -H "Content-Type: application/json" \
  -d "{\"content\": \"```\\n$ASCII_ART\\n```\"}" \
  "$WEBHOOK"
```

**Method 3: Manual Copy-Paste**
When automation fails, provide formatted output:

```
🐉 **SWARMERS ASSEMBLE** 🔥

```
[ASCII ART HERE]
```

*Made with 🔥 by [agent name]*
```

### Complete Discord Logo Workflow

Example: Creating and posting a mascot logo for "Swarmers" Discord:

```bash
# 1. Generate options
cowsay -c dragon -t "WE ARE THE SWARM"
pyfiglet -f slant "SWARMERS"

# 2. Format for Discord (escape backslashes)
LOGO='```\n  ________________\n| WE ARE THE SWARM |\n  ================\n                  \\\\'

# 3. Post via webhook or paste manually
```

## Decision Flow

1. **Text as a banner** → pyfiglet if installed, otherwise asciified API via curl
2. **Wrap a message in fun character art** → cowsay (check if you have Perl or Python version!)
3. **Add decorative border/frame** → boxes (can combine with pyfiglet/asciified)
4. **Art of a specific thing** (cat, rocket, dragon) → ascii.co.uk via curl + parsing
5. **Convert an image to ASCII** → ascii-image-converter or jp2a
6. **QR code** → qrenco.de via curl
7. **Weather/moon art** → wttr.in via curl
8. **Something custom/creative** → LLM generation with Unicode palette
9. **Maximum intensity logo for Discord/banners** → Use "Intense/Bold Logo Design" workflow — build big, then trim to fit platform limits
10. **Any tool not installed** → install it, or fall back to next option

**Note on cowsay:** Two incompatible versions exist:
- System package (apt/brew): `cowsay -f dragon "msg"` 
- Python pip: `cowsay -c dragon -t "msg"`
If one syntax fails, try the other!
