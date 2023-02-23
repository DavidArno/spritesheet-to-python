import pytest
from stylesheet2python import SpriteSheetConfiguration, SpriteSheet, RGB
#from PIL.Image import Image  #type: ignore
from PIL import Image  #type: ignore

# need to do some tests. Parametized is the way to go I think. Can loop through combinations of dynamic/1+ values
# for height and width, all combos of options and various widths that force stop pattern to be on lines 1-3
# (4+? - probably not. If works for 2-3, will work for n)

#@pytest.mark.parametrize("in_data, out_data", [(3, 5), (3, 4)])
#def test_answer(in_data: int, out_data: int):
#    assert func(in_data) == out_data

# image widths 9, 17, 35, 50
# sprite widths 1, 2, 5, 8, (11, 15)
# sprite heights 1, 3, 7, 10, 19, 31, 48, 60
# control black/colour
# blanks_between_rows black/colour
# blanks_between_sprites black/colour
#
# So 4 x 6 x 8 x 2 x 2 x 2 = 1500ish tests
BLACK = RGB(0, 0, 0)
CONTROL = RGB(11, 15, 17)
ROW_BLANK = RGB(31, 71, 97)
SPRITE_BLANK = RGB(111, 171, 13)

IMAGE_WIDTHS = [9, 17, 35, 50]
IMAGE_HEIGHT = 10
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
        if b >= 254 and g >= 254:
            return (r + 2, 0, 0)
        elif b >= 254:
            return (r, g + 2, 0)
        else:
            return (r, g, b +2)

    def set_pixel_get_next_colour(image: Image.Image, x: int, y: int, r: int, g: int, b: int) -> tuple[int, int, int]:
        image.putpixel((x, y), (r, g, b))
        return next_colour(r, g, b)

    def update_xy(x: int, y: int) -> tuple[int, int]:
        x += 1
        if x >= image_width:
            x = 0
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

    if x + 8 >= image_width:
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

def file_based_test_data() -> list[tuple[Image.Image, SpriteSheetConfiguration]]:
    test_data = []

    for image_width in IMAGE_WIDTHS:
        for sprite_width in SPRITE_WIDTHS:
            if sprite_width is not None and sprite_width > image_width:
                continue

            for sprite_height in SPRITE_HEIGHTS:
                for control_bit in CONTROL_BITS:
                    for row_blank in ROW_BLANK_BITS:
                        for sprite_blank in SPRITE_BLANK_BITS:
                            image, config = create_image_and_config(
                                image_width,
                                IMAGE_HEIGHT,
                                sprite_width,
                                sprite_height,
                                control_bit,
                                row_blank,
                                sprite_blank
                            )

                            test_data.append((image, config))

    return test_data

def test_0():
    rgb_image = create_image(9, 5, None, 12, None, RGB(155, 1, 221), RGB(155, 1, 221))
    spritesheet = SpriteSheet(rgb_image)
    actual_config = spritesheet.configuration
    expected_config = create_configuration(None, 12, None, RGB(155, 1, 221), RGB(155, 1, 221))
    assert expected_config == actual_config

def test_1():
    image = Image.open("C:\\PersonalDev\\spritesheet-to-python\\tests\\images\\valid_40_h1_w8_s156-0-220.png")
    rgb_image = image.convert('RGB')
    spritesheet = SpriteSheet(rgb_image)
    config = spritesheet.configuration
    assert config.sprite_height == 1
    assert config.sprite_width == 8
    assert config.control_pixel_colour == RGB(156, 0, 220)
    assert config.strict_mode
    assert config.blanks_between_rows
    assert config.blanks_between_sprites

def test_2():
    image = Image.open("C:\\PersonalDev\\spritesheet-to-python\\tests\\images\\valid_30x2_h10_w9_s255-255-255.png")
    rgb_image = image.convert('RGB')
    spritesheet = SpriteSheet(rgb_image)
    config = spritesheet.configuration
    assert config.sprite_height == 10
    assert config.sprite_width == 9
    assert config.control_pixel_colour == RGB(255, 255, 255)
    assert config.strict_mode
    assert not config.blanks_between_rows
    assert not config.blanks_between_sprites

def test_3():
    image = Image.open("C:\\PersonalDev\\spritesheet-to-python\\tests\\images\\valid_40_no-h_no-w_no-s.png")
    rgb_image = image.convert('RGB')
    spritesheet = SpriteSheet(rgb_image)
    config = spritesheet.configuration
    assert config.sprite_height is None
    assert config.sprite_width is None
    assert config.control_pixel_colour is None
    assert not config.strict_mode
    assert not config.blanks_between_rows
    assert not config.blanks_between_sprites