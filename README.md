# The World Today — Friday, November 20, 2026 (v5)

A one-page photo-magazine cover summing up the world news of
**Friday, November 20, 2026**, for the make.fun competition
`news-image-20261120` ($250, top 50).

## The cover

Unlike the newspaper-grid layout of v4, v5 is a full-bleed photo cover:
the burning Kyiv bridge fills the top ~70% of the page, with a small
white masthead, a red date ribbon, and the headline set in white serif
over the dark foot of the photograph. A dark band across the bottom
~30% carries three smaller photo stories and a one-line in-brief.

- **Hero — "KYIV'S BRIDGES BURN":** Russian ballistic missiles struck
  Kyiv's North and South bridges over the Dnipro overnight, cutting
  power and water across the capital.
- **UK pledges 1,000+ drones for Kyiv** — a £260 million package.
- **Taiwan stocks plunge 2,200 points** — intraday, breaking below
  37,000.
- **Trump pardons Pete Rose** — a posthumous pardon for the baseball
  legend.
- **In brief:** Houthi missile hits Riyadh's tallest tower • US
  sanctions Comancheros & 'Ndrangheta • 13,000 protest in Tokyo
  against the Takaichi government.

## Images

All four photographs are photorealistic AI-generated images, stored in
`assets/` and composed with `compose.py` (Python + PIL). Nothing is
drawn as flat vector art: the cover is built from the photographs
themselves, and the program only copies the finished page.

## Files

| File | What it is |
| --- | --- |
| `entry.png` | The finished 1024×1024 cover (337,212 bytes) |
| `main.py` | Harness entrypoint: copies `entry.png` byte-for-byte to `/output/entry.png` |
| `compose.py` | Builds `entry.png` from the photos in `assets/` |
| `assets/` | The four photorealistic source photographs |

## Run

```sh
python3 compose.py   # rebuild entry.png from assets/
python3 main.py      # copy entry.png to /output/entry.png
```

Two runs of `main.py` write byte-identical output (verified by SHA-256).

## Entry details

- Competition: `news-image-20261120` — "Sum up 20 November's world news
  in one image"
- Handle: **ajx** · GitHub: **Wahyupurnomoaji21** · Payout wallet (Solana):
  `BQLypNdAeKhFvji7iRWi2Dq22B9MxQp8StWYKe38geW9`
- License: MIT
