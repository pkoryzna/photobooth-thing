from typing import Literal

import PIL.Image
import pygame
import pygame.camera
from PIL import Image, ImageEnhance
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


def capture_camera_image(
    camera: pygame.camera.Camera, target_resolution: int
) -> pygame.Surface:
    # Get a frame from camera and crop the middle
    camera_image = camera.get_image()
    square_crop = crop_middle_square(camera_image)

    image_pil = surface_to_image(square_crop)

    return image_to_surface(image_pil)


def enhance_for_print(image: Image, brightness_factor: float = 1.0, contrast_factor: float = 1.0):
    contr =  ImageEnhance.Contrast(image).enhance(contrast_factor)
    bright = ImageEnhance.Brightness(contr).enhance(brightness_factor)
    return bright
