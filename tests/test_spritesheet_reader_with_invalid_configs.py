import pytest
from stylesheet2python import SpriteSheetConfiguration, SpriteSheet, RGB, InfoLineParseResult
from PIL import Image  #type: ignore

from stylesheet2python.spritesheet_reader import InfoLineParseError  #type: ignore

BLACK = RGB(0, 0, 0)
WHITE = RGB(255, 255, 255)

def int_to_x_pattern(value: int) -> str:
    result = ""
    for _ in range(8):
        result = ("x" if value & 1 else "_") + result
        value >>= 1

    return result

def create_image_from_x_pattern(pattern: list[str]) -> Image.Image:
    height = len(pattern)
    width = len(pattern[0])

    image = Image.new("RGB", (width, height))
    for y in range(height):
        for x in range(width):
            image.putpixel((x, y), (WHITE if pattern[y][x] == "x" else BLACK))

    return image

def generate_start_pattern_error_data() -> tuple[list[tuple[Image.Image, bool]], list[str]]:
    images_and_valid_starts = []
    names = []

    for n in range(256):
        start_pattern = int_to_x_pattern(n)
        valid_start = start_pattern == "x_xx_x_x"
        image_data = [start_pattern, "________", "________"]

        image = create_image_from_x_pattern(image_data)

        images_and_valid_starts.append((image, valid_start))
        names.append(start_pattern + ("_valid" if valid_start else ""))

    return images_and_valid_starts, names

def generate_stop_pattern_error_data() -> tuple[list[tuple[Image.Image, bool]], list[str]]:
    images_and_valid_stops = []
    names = []

    for n in range(256):
        stop_pattern = int_to_x_pattern(n)[::-1]
        valid_stop = stop_pattern == "x_x_xx_x"
        image_data = ["x_xx_x_x", "________", "________", stop_pattern]

        image = create_image_from_x_pattern(image_data)

        images_and_valid_stops.append((image, valid_stop))
        names.append(stop_pattern + ("_valid" if valid_stop else ""))

    return images_and_valid_stops, names

IMAGES_AND_VALID_STARTS, START_NAMES = generate_start_pattern_error_data()
IMAGES_AND_VALID_STOPS, STOPS_NAMES = generate_stop_pattern_error_data()

@pytest.mark.parametrize(("rgb_image", "valid"), IMAGES_AND_VALID_STARTS, ids=START_NAMES)
def test_start_pattern(rgb_image, valid):
    try:
        result = SpriteSheet(rgb_image)
    except InfoLineParseError as e:
        assert (
            (e.args[0] == InfoLineParseResult.STOP_PATTERN_NOT_FOUND and valid) or
            (e.args[0] == InfoLineParseResult.START_PATTERN_NOT_FOUND and not valid)
        )

@pytest.mark.parametrize(("rgb_image", "valid"), IMAGES_AND_VALID_STOPS, ids=STOPS_NAMES)
def test_stop_pattern(rgb_image, valid):
    try:
        result = SpriteSheet(rgb_image)
        assert valid
    except:
        assert not valid
