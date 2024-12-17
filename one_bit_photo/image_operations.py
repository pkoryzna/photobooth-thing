from typing import Literal

import PIL.Image
from PIL import Image
from pygame import Surface
import pygame.image
from pygame.locals import Rect

PIXEL_FORMAT: Literal["RGB"] = "RGB"


def surface_to_image(surface: Surface) -> Image:
    surface_bytes = pygame.image.tobytes(surface, PIXEL_FORMAT)
    return Image.frombytes(
        PIXEL_FORMAT,
        (
            surface.get_width(),
            surface.get_height(),
        ),
        surface_bytes,
    )


def image_to_surface(image: Image) -> Surface:
    image_bytes = image.tobytes()
    return pygame.image.frombuffer(
        image_bytes, (image.width, image.height), PIXEL_FORMAT
    )


def convert_to_1bit(image: Image) -> Image:
    return image.convert("1", None, PIL.Image.Dither.FLOYDSTEINBERG).convert("RGB")


def crop_middle_square(camera_image: pygame.Surface) -> pygame.Surface:
    left = max((camera_image.get_width() - camera_image.get_height()) / 2, 0)
    top = max((camera_image.get_height() - camera_image.get_width()) / 2, 0)
    min_dim = min(camera_image.get_width(), camera_image.get_height())
    square_crop = camera_image.subsurface(Rect(left, top, min_dim, min_dim))
    return square_crop
