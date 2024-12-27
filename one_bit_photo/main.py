import sys

import pygame
import pygame.camera

from one_bit_photo.image_operations import (
    capture_camera_image,
    surface_to_image,
    enhance_for_print,
    convert_to_1bit,
    image_to_surface,
)
from one_bit_photo.printer import print_image, discover_printer

PHOTOS_TO_TAKE = 4

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 1600

IMAGE_DISPLAY_HEIGHT = SCREEN_HEIGHT // PHOTOS_TO_TAKE

PREFERRED_CAMERAS = [
    "HP 320 FHD Webcam",
    "FaceTime HD Camera",
]


CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# 62 mm endless label width px
PRINT_WIDTH_PX = 696

FPS = 60

COUNTDOWN_TIMER_EVENT_TYPE = pygame.event.custom_type()


def _find_camera_name() -> str | int:
    cameras = pygame.camera.list_cameras()
    if not cameras:
        raise RuntimeError("No cameras found")
    for preferred_cam in set(PREFERRED_CAMERAS):
        if preferred_cam in cameras:
            return preferred_cam
    return cameras[0]


def find_camera():
    camera_name = _find_camera_name()
    print(f"Using camera: {camera_name}", file=sys.stderr)
    return pygame.camera.Camera(camera_name, (CAMERA_WIDTH, CAMERA_HEIGHT))


def main():
    pygame.init()
    display_surface = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN, vsync=1
    )
    pygame.camera.init()
    camera = find_camera()
    printer = discover_printer()
    while True:
        camera.start()
        images = capture_loop(camera, display_surface)
        camera.stop()
        printing_animation_loop(images, display_surface)

        printout_surface = pygame.Surface(
            (PRINT_WIDTH_PX, PRINT_WIDTH_PX * len(images))
        )
        blit_images_vertical(printout_surface, images)

        printout_image = convert_to_1bit(
            enhance_for_print(
                surface_to_image(printout_surface),
                brightness_factor=1.5,
            )
        )

        print_image([printout_image], label_type="62", printer_instance=printer)


def capture_loop(camera, display_surface):
    captured_images = []
    capturing = False
    countdown_beeps = 0
    while len(captured_images) != PHOTOS_TO_TAKE:
        # Handle events and keep event queue alive
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    return
                case pygame.MOUSEBUTTONUP:
                    pygame.time.set_timer(COUNTDOWN_TIMER_EVENT_TYPE, 1000)
                    capturing = True
                case pygame.KEYDOWN if event.key == pygame.K_SPACE and not capturing:
                    pygame.time.set_timer(COUNTDOWN_TIMER_EVENT_TYPE, 1000)
                    capturing = True
                case pygame.KEYDOWN if event.key == pygame.K_RETURN:
                    take_camera_shot(camera, captured_images, display_surface)
                case b if b == COUNTDOWN_TIMER_EVENT_TYPE and capturing:
                    countdown_beeps += 1
                    if countdown_beeps % 4 == 0:
                        take_camera_shot(camera, captured_images, display_surface)
                    else:
                        display_surface.fill(pygame.color.Color(200, 0, 0))
                        pygame.display.flip()
                        pygame.time.wait(100)

        display_surface.fill(pygame.Color(0, 0, 0))
        live_frame = capture_camera_image(camera, PRINT_WIDTH_PX)
        images_to_display = [dither_surface(s) for s in [*captured_images, live_frame]]
        blit_images_vertical(display_surface, images_to_display, PHOTOS_TO_TAKE)
    return captured_images


def dither_surface(surf):
    return image_to_surface(convert_to_1bit(surface_to_image(surf)))


def blit_images_vertical(
    dest_surface: pygame.Surface,
    images_to_display: list[pygame.Surface],
    total_images_count: int | None = None,
):
    """Display images in a vertical column in the middle of the dest_surface"""
    if total_images_count is None:
        total_images_count = len(images_to_display)

    new_height = dest_surface.get_height() // total_images_count
    for image_no, image in enumerate(images_to_display):
        new_width = image.get_width() * new_height // image.get_height()
        scaled = pygame.transform.smoothscale(image, (new_width, new_height))
        dest_rect = scaled.get_rect()
        dest_rect.top = image_no * new_height
        display_rect = dest_surface.get_rect()
        dest_rect.centerx = display_rect.centerx
        dest_surface.blit(scaled, dest=dest_rect)
    pygame.display.flip()


def take_camera_shot(camera, captured_images, display_surface):
    """Take a camera shot with flash"""
    display_surface.fill(pygame.Color(255, 255, 255))
    pygame.display.flip()
    pygame.time.wait(100)
    captured_images.append(capture_camera_image(camera, PRINT_WIDTH_PX))


def ease_in_out_cubic(x):
    if x < 0.5:
        return 4 * x * x * x
    else:
        return 1 - (-2 * x + 2) ** 3 / 2


def printing_animation_loop(
    captured_images: list[pygame.Surface], display_surface: pygame.Surface
):
    TOTAL_ANIM_TIME = 1000

    images_surface = pygame.Surface(
        (display_surface.get_width(), display_surface.get_height())
    )

    blit_images_vertical(images_surface, captured_images)
    top_offset = 0.0
    clock = pygame.time.Clock()
    total_ms_progress = 0
    while top_offset <= SCREEN_HEIGHT:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        total_ms_progress += clock.tick(FPS)
        top_offset = (
            ease_in_out_cubic(total_ms_progress / TOTAL_ANIM_TIME) * 2 * SCREEN_HEIGHT
        )

        dest_rect = display_surface.get_rect()
        dest_rect.top += round(top_offset)
        display_surface.fill(pygame.Color(0, 0, 0))
        display_surface.blit(images_surface, dest=dest_rect)

        pygame.display.flip()

    pygame.time.wait(1000)


if __name__ == "__main__":
    main()
