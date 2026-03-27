from __future__ import annotations

from pathlib import Path

from PIL import Image


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    source_path = repo_root / "images" / "logo.png"
    output_path = repo_root / "images" / "logo.ico"

    image = Image.open(source_path).convert("RGBA")
    canvas_size = max(image.size)
    square = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    offset = ((canvas_size - image.width) // 2, (canvas_size - image.height) // 2)
    square.paste(image, offset, image)

    square.save(
        output_path,
        format="ICO",
        sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)],
    )
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
