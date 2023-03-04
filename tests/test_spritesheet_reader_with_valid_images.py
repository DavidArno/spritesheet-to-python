import pytest
from stylesheet2python import SpriteSheetConfiguration, SpriteSheet, RGB
from PIL import Image  #type: ignore

BLACK = RGB(0, 0, 0)
CONTROL = RGB(211, 115, 17)
ROW_BLANK = RGB(31, 171, 97)
SPRITE_BLANK = RGB(111, 71, 113)

IMAGE_WIDTHS = [8, 17, 35, 50]
IMAGE_HEIGHT = 12
SPRITE_WIDTHS = [None, 1, 2, 5, 8, 11, 15]
SPRITE_HEIGHTS = [None, 1, 3, 7, 10, 19, 31, 48, 60]
CONTROL_BITS = [None, CONTROL]
ROW_BLANK_BITS = [None, ROW_BLANK]
SPRITE_BLANK_BITS = [None, SPRITE_BLANK]

def create_image(
        image_width: int,
        image_height: int,
        sprite_width: int|None,
        sprite_height: int|None,
        control_bit: RGB|None,
        row_blank: RGB|None,
        sprite_blank: RGB|None) -> Image.Image:

    def next_colour(r: int, g: int, b: int) -> tuple[int, int, int]:
        if b >= 246 and g >= 246:
            return (r + 10, 0, 0)
        elif b >= 246:
            return (r, g + 10, 0)
        else:
            return (r, g, b + 10)

    def set_pixel_get_next_colour(image: Image.Image, x: int, y: int, r: int, g: int, b: int) -> tuple[int, int, int]:
        image.putpixel((x, y), (r, g, b))
        return next_colour(r, g, b)

    def update_xy(x: int, y: int) -> tuple[int, int]:
        x += 1
        if x >= image_width:
            x = x - image_width
            y += 1

        return (x, y)

    def draw_width_or_height_get_new_xy_and_rgb(
            image: Image.Image,
            x: int, y: int,
            r: int, g: int, b: int,
            size: int|None
    ) -> tuple[tuple[int, int], tuple[int, int, int]]:

        if size is None:
            x, y = update_xy(x, y)
        else:
            for i in range(size):
                (r, g, b) = set_pixel_get_next_colour(image, x, y, r, g, b)
                x, y = update_xy(x, y)

        x, y = update_xy(x, y)
        return ((x, y), (r, g, b))

    def draw_pixel_get_new_xy_and_rgb(
            image: Image.Image,
            x: int, y: int,
            pixel: RGB|None
    ) -> tuple[int, int]:

        if pixel is not None:
            image.putpixel((x, y), (pixel.r, pixel.g, pixel.b))

        x, y = update_xy(x + 1, y)

        return (x, y)

    image:Image.Image = Image.new("RGB", (image_width, image_height))

    (r, g, b) = set_pixel_get_next_colour(image, 0, 0, 2, 2, 2)
    (r, g, b) = set_pixel_get_next_colour(image, 2, 0, r, g, b)
    (r, g, b) = set_pixel_get_next_colour(image, 3, 0, r, g, b)
    (r, g, b) = set_pixel_get_next_colour(image, 5, 0, r, g, b)
    (r, g, b) = set_pixel_get_next_colour(image, 7, 0, r, g, b)

    x, y = update_xy(8, 0)

    ((x, y), (r, g, b)) = draw_width_or_height_get_new_xy_and_rgb(image, x, y, r, g, b, sprite_height)
    ((x, y), (r, g, b)) = draw_width_or_height_get_new_xy_and_rgb(image, x, y, r, g, b, sprite_width)
    (x, y) = draw_pixel_get_new_xy_and_rgb(image, x, y, sprite_blank)
    (x, y) = draw_pixel_get_new_xy_and_rgb(image, x, y, row_blank)
    (x, y) = draw_pixel_get_new_xy_and_rgb(image, x, y, control_bit)

    if x + 7 >= image_width:
        y += 1

    x = image_width - 8
    (r, g, b) = set_pixel_get_next_colour(image, x + 7, y, r, g, b)
    (r, g, b) = set_pixel_get_next_colour(image, x + 5, y, r, g, b)
    (r, g, b) = set_pixel_get_next_colour(image, x + 4, y, r, g, b)
    (r, g, b) = set_pixel_get_next_colour(image, x + 2, y, r, g, b)
    (r, g, b) = set_pixel_get_next_colour(image, x, y, r, g, b)

    return image

def create_configuration(
        sprite_width: int|None,
        sprite_height: int|None,
        control_bit: RGB|None,
        row_blank: RGB|None,
        sprite_blank: RGB|None) -> SpriteSheetConfiguration:

    return SpriteSheetConfiguration(
        sprite_height,
        sprite_width,
        sprite_blank is not None,
        row_blank is not None,
        control_bit is not None,
        control_bit)

def create_test_name(
        image_width: int,
        image_height: int,
        sprite_width: int|None,
        sprite_height: int|None,
        control_bit: RGB|None,
        row_blank: RGB|None,
        sprite_blank: RGB|None) -> str:

    def format_size(value: int|None) -> str|int:
        if value is None:
            return "<d>"
        else:
            return value

    def format_blank(value: RGB|None) -> str:
        if value is None:
            return "n"
        else:
            return "<y>"

    def format_control(value: RGB|None) -> str:
        if value is None:
            return "n"
        else:
            return "<s>"

    return (
        f"i:{image_width}x{image_height}_s{format_size(sprite_width)}x{format_size(sprite_height)}_"
        f"c:{format_control(control_bit)}_rb:{format_blank(row_blank)}_sb:{format_blank(sprite_blank)}"
    )

def create_image_config_and_name(
        image_width: int,
        image_height: int,
        sprite_width: int|None,
        sprite_height: int|None,
        control_bit: RGB|None,
        row_blank: RGB|None,
        sprite_blank: RGB|None) -> tuple[Image.Image, SpriteSheetConfiguration, str]:

    image = create_image(
        image_width,
        image_height,
        sprite_width,
        sprite_height,
        control_bit,
        row_blank,
        sprite_blank
    )

    config = create_configuration(
        sprite_width,
        sprite_height,
        control_bit,
        row_blank,
        sprite_blank
    )

    name = create_test_name(
        image_width,
        image_height,
        sprite_width,
        sprite_height,
        control_bit,
        row_blank,
        sprite_blank
    )

    return image, config, name

def generate_test_data_and_names() -> tuple[list[tuple[Image.Image, SpriteSheetConfiguration]], list[str]]:
    images_and_configurations = []
    names = []

    for image_width in IMAGE_WIDTHS:
        for sprite_width in SPRITE_WIDTHS:
            if sprite_width is not None and sprite_width > image_width:
                continue

            for sprite_height in SPRITE_HEIGHTS:
                for control_bit in CONTROL_BITS:
                    for row_blank in ROW_BLANK_BITS:
                        for sprite_blank in SPRITE_BLANK_BITS:
                            image, config, name = create_image_config_and_name(
                                image_width,
                                IMAGE_HEIGHT,
                                sprite_width,
                                sprite_height,
                                control_bit,
                                row_blank,
                                sprite_blank
                            )

                            images_and_configurations.append((image, config))
                            names.append(name)

    return images_and_configurations, names

IMAGES_AND_CONFIGURATIONS, NAMES = generate_test_data_and_names()

@pytest.mark.parametrize(("rgb_image", "expected_config"), IMAGES_AND_CONFIGURATIONS, ids=NAMES)
def test_sprite_config(rgb_image, expected_config):
    spritesheet = SpriteSheet(rgb_image)
    actual_config = spritesheet.configuration
    assert expected_config == actual_config
