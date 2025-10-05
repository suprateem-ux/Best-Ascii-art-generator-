import yaml
import pyfiglet
from rich.console import Console
from rich.text import Text
from PIL import Image
import random

console = Console()

with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

with open("enter.txt", "r", encoding="utf-8") as f:
    input_text = f.read().strip()

def apply_gradient(text, gradient_name):
    gradient_dict = config.get("gradients", {})
    colors = gradient_dict.get(gradient_name)

    if not colors or gradient_name.lower() == "none":
        # fallback to static color
        return Text(text, style=config.get("text_color", "white"))

    t = Text()
    n = len(colors)
    for i, char in enumerate(text):
        if char == "\n":
            t.append("\n")
            continue
        color = colors[i % n]
        t.append(char, style=color)
    return t


def generate_ascii_text():
    font = config.get("font", "slant")
    if config.get("random_font", False):
        font = random.choice(pyfiglet.getFonts())

    fig = pyfiglet.Figlet(
        font=font,
        width=config.get("width", 100),
        justify=config.get("justify", "center"),
    )
    ascii_art = fig.renderText(input_text)

    gradient_name = config.get("text_gradient", "none")
    styled_text = apply_gradient(ascii_art, gradient_name)
    console.print(styled_text)
    return ascii_art


def image_to_ascii(path="sample.png"):
    width = config.get("image_width", 80)
    charset = config.get("image_charset", "@#S%?*+;:,. ")
    invert = config.get("image_invert", False)

    try:
        img = Image.open(path)
    except FileNotFoundError:
        console.print("[red]Image file not found! Skipping image...[/red]")
        return ""

    aspect_ratio = img.height / img.width
    new_height = int(aspect_ratio * width * 0.55)
    img = img.resize((width, new_height))
    img = img.convert("L")  # grayscale

    ascii_str = ""
    for y in range(img.height):
        for x in range(img.width):
            brightness = img.getpixel((x, y))
            if invert:
                brightness = 255 - brightness
            index = int(brightness / 255 * (len(charset) - 1))
            ascii_str += charset[index]
        ascii_str += "\n"

    # Apply gradient or static color
    gradient_name = config.get("image_gradient", "none")
    if gradient_name.lower() != "none":
        styled_text = apply_gradient(ascii_str, gradient_name)
        console.print(styled_text)
    else:
        console.print(Text(ascii_str, style=config.get("image_color", "yellow")))

    return ascii_str


if __name__ == "__main__":
    if config.get("show_rules", True):
        console.rule(style=config.get("rule_color", "cyan"))

    ascii_text = generate_ascii_text()
    ascii_image = image_to_ascii("sample.png")  # Replace with your image

    if config.get("show_rules", True):
        console.rule(style=config.get("rule_color", "cyan"))

    # Save to file if enabled
    if config.get("save_to_file", False):
        with open(config.get("output_file", "output.txt"), "w", encoding="utf-8") as f:
            f.write(ascii_text + "\n" + ascii_image)
        console.print(f"[green]Saved output to {config.get('output_file')}[/green]")
