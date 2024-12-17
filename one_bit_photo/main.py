import sys

import pygame
import pygame.camera
from pygame.locals import *


SCREEN_WIDTH = 600
SCREEN_HEIGHT = 1000

IMAGE_HEIGHT = SCREEN_HEIGHT // 4

PREFERRED_CAMERAS = [
    "HP 320 FHD Webcam",
    "FaceTime HD Camera",
]


CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720


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
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        vsync=1
    )
    pygame.camera.init()
    camera = find_camera()

    camera.start()
    images = capture_loop(camera, display_surface)
    camera.stop()
    printing_animation_loop(images, display_surface)

def capture_loop(camera, display_surface):
    captured_images = []
    while len(captured_images) != 4:
        # Handle special events and keep event queue alive
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    take_camera_shot(camera, captured_images, display_surface)
                continue

        display_surface.fill(pygame.Color(0, 0, 0))
        live_frame = capture_camera_image(camera)
        images_to_display = [*captured_images, live_frame]
        blit_images_vertical(display_surface, images_to_display)
    return captured_images


def blit_images_vertical(dest_surface: pygame.Surface, images_to_display: list[pygame.Surface]):
    """Display images in a vertical column in the middle of the display"""
    for image_no, image in enumerate(images_to_display):
        dest_rect = image.get_rect()
        dest_rect.top = image_no * IMAGE_HEIGHT
        display_rect = dest_surface.get_rect()
        dest_rect.centerx = display_rect.centerx
        dest_surface.blit(image, dest=dest_rect)
    pygame.display.flip()


def take_camera_shot(camera, captured_images, display_surface):
    """Take a camera shot with flash"""
    display_surface.fill(pygame.Color(255, 255, 255))
    pygame.display.flip()
    pygame.time.wait(100)
    captured_images.append(capture_camera_image(camera))


def capture_camera_image(camera):
    # Get a frame from camera and crop the middle
    camera_image = camera.get_image()
    square_crop = crop_middle_square(camera_image)
    # Scale to target resolution
    scaled = pygame.transform.smoothscale(
        square_crop, size=(IMAGE_HEIGHT, IMAGE_HEIGHT)
    )
    return scaled


def crop_middle_square(camera_image):
    left = max((camera_image.get_width() - camera_image.get_height()) / 2, 0)
    top = max((camera_image.get_height() - camera_image.get_width()) / 2, 0)
    min_dim = min(camera_image.get_width(), camera_image.get_height())
    square_crop = camera_image.subsurface(Rect(left, top, min_dim, min_dim))
    return square_crop


def printing_animation_loop(
    captured_images: list[pygame.Surface], display_surface: pygame.Surface
):
    TOTAL_ANIM_TIME = 2000
    PIXEL_PER_MS = SCREEN_HEIGHT / TOTAL_ANIM_TIME
    images_surface = pygame.Surface((display_surface.get_width(), display_surface.get_height()))

    blit_images_vertical(images_surface, captured_images)
    top_offset = 0.0
    clock = pygame.time.Clock()
    while top_offset < SCREEN_HEIGHT + 1:
        pygame.event.pump()  # keep the event queue alive
        dest_rect = display_surface.get_rect()
        dest_rect.top += round(top_offset)
        display_surface.fill(pygame.Color(0, 0, 0))
        display_surface.blit(images_surface, dest=dest_rect)
        millis = clock.tick()
        top_offset += millis * PIXEL_PER_MS
        pygame.display.flip()



if __name__ == "__main__":
    main()
