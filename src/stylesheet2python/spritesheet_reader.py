from itertools import islice
from PIL import Image  # type: ignore#
from dataclasses import dataclass
from typing import Generator, NamedTuple, cast
from enum import Enum

RGB = NamedTuple('RGB', [('r', int), ('g', int), ('b', int)])

_BLACK: RGB = RGB(0, 0, 0)


class InfoLineParseResult(Enum):
    START_PATTERN_NOT_FOUND = 1
    EXPECTED_BLACK_UPTO_STOP_PATTERN = 2
    STOP_PATTERN_NOT_FOUND = 3
    IMAGE_FILE_TOO_SMALL = 4


@dataclass
class SpriteSheetConfiguration:
    sprite_height: int|None
    sprite_width: int|None
    blanks_between_sprites: bool
    blanks_between_rows: bool
    strict_mode: bool
    control_pixel_colour: RGB|None

class ImageIsNotRgbError(Exception):
    "Raised when a non-rgb format image is used to initialise a SpriteSheet"
    pass

class SpriteSheet:
    def __init__(self, image:Image) -> None:
        if (image.mode, image.format) != ("RGB", None):
            raise ImageIsNotRgbError()

        if not isinstance(raw_config := self._try_parse_info_line(image), SpriteSheetConfiguration):
            raise Exception()

        #config = cast(SpriteSheetConfiguration, raw_config)



    def _try_parse_info_line(self, image: Image) -> SpriteSheetConfiguration|InfoLineParseResult:
        width, _ = image.size

        if width < 8:
            return InfoLineParseResult.IMAGE_FILE_TOO_SMALL

        if not self._start_pattern_found(image, width):
            return InfoLineParseResult.START_PATTERN_NOT_FOUND

        height = self._get_width_or_height(image, 9)
        width_x = 10 + height if isinstance(height, int) else 1
        width = self._get_width_or_height(image, width_x)
        options_x = 12 + width if isinstance(width, int) else 1
        sprite_blanks, row_blanks, strict, control_colour = self._get_options(image, options_x)

        x, y = self._normalise_x_y(options_x + 6, 0, width)

        found, stop_y = self._stop_pattern_found(image, width, x, y)

        if not found:
            return InfoLineParseResult.STOP_PATTERN_NOT_FOUND

#        if strict and not self._all_black_between_options_and_stop(image, x, y, stop_y):
#            return InfoLineParseResult.EXPECTED_BLACK_UPTO_STOP_PATTERN

        return SpriteSheetConfiguration(
            sprite_height=height,
            sprite_width=width,
            blanks_between_sprites=sprite_blanks,
            blanks_between_rows=row_blanks,
            strict_mode=strict,
            control_pixel_colour=control_colour
        )

    def _start_pattern_found(self, image: Image, width: int) -> bool:
        return self._start_or_stop_pattern_found(image, is_start=True, width=width, y=0)

    def _stop_pattern_found(self, image: Image, width: int, x:int, y:int) -> tuple[bool, int]:
        stop_y = y if width - x > 8 else y + 1
        return self._start_or_stop_pattern_found(image, is_start=False, width=width, y=stop_y), stop_y

    def _start_or_stop_pattern_found(
            self,
            image: Image,
            *,
            is_start: bool,
            width: int,
            y: int) -> bool:

        offset = 0 if is_start else width - 1

        def index(position: int) -> int:
            return abs(offset - position)

        return (
            self._get_pixel_rgb(image, index(0), y) != _BLACK and
            self._get_pixel_rgb(image, index(1), y) == _BLACK and
            self._get_pixel_rgb(image, index(2), y) != _BLACK and
            self._get_pixel_rgb(image, index(3), y) != _BLACK and
            self._get_pixel_rgb(image, index(4), y) == _BLACK and
            self._get_pixel_rgb(image, index(5), y) != _BLACK and
            self._get_pixel_rgb(image, index(6), y) == _BLACK and
            self._get_pixel_rgb(image, index(7), y) != _BLACK
        )

    def _get_width_or_height(self, image: Image, start_x: int) -> int|None:
        count = 0
        for pixel in self._image_as_rgb_stream(image, start_x, 0):
            if pixel == _BLACK:
                break

        return None if count == 0 else count

    def _get_options(self, image: Image, start_x: int) -> tuple[bool, bool, bool, RGB|None]:
        sprite_blank_rgb, row_blank_rgb, strict_rgb = islice(self._image_as_rgb_stream(image, start_x, 0), 0, 6, 2)
        return (
            sprite_blank_rgb != _BLACK,
            row_blank_rgb != _BLACK,
            strict := strict_rgb != _BLACK,
            strict_rgb if strict else None
        )

    def _image_as_rgb_stream(self, image, start_x: int, start_y: int) -> Generator[RGB, None, None]:
        width, height = image.size
        x, y = self._normalise_x_y(start_x, start_y, width)

        while True:
            if x >= width:
                x = 0
                y += 1

            if y >= height:
                return

            yield self._get_pixel_rgb(image, x, y)

    def _get_pixel_rgb(self, image: Image, x: int, y: int) -> RGB:
        return cast(RGB, image.get_pixel((x, y)))  # type: ignore

    def _normalise_x_y(this, x: int, y: int, width: int) -> tuple[int, int]:
        while x >= width:
            x -= width
            y += 1

        return x, y