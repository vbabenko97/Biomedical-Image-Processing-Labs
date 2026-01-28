# Copyright © 2020. All rights reserved.
# Authors: Vitalii Babenko
# Contacts: vbabenko2191@gmail.com

import argparse
from pathlib import Path
import sys

import numpy as np
import pydicom
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays.numpymodule import ARRAY_TO_GL_TYPE_MAPPING

DEFAULT_IMAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "Images"
    / "ImageForLab1"
    / "DICOM_Image_for_Lab_2.dcm"
)


def load_texture(pixels, type):
    gl_type = ARRAY_TO_GL_TYPE_MAPPING.get(pixels.dtype)
    glBindTexture(GL_TEXTURE_2D, glGenTextures(1))
    glTexImage2D(GL_TEXTURE_2D, 0, type, width, height, 0, type, gl_type, pixels)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)


def transform_color_channel(pixels):
    global height, width
    rgb = np.zeros((height, width, 3), 'uint8')
    rgb[..., 0] = pixels
    rgb[..., 1] = 0
    rgb[..., 2] = 0
    return rgb


def transform_gradient(pixels):
    gradient = {}
    color = 255
    for key in range(np.amin(pixels), (np.amax(pixels) // 2)):
        gradient[key] = color
        color -= 2
    gradient[np.amax(pixels) // 2] = 0
    color = 255
    for key in range(np.amax(pixels), (np.amax(pixels) // 2) + 1, -1):
        gradient[key] = color
        color -= 2
    gradient[(np.amax(pixels) // 2) + 1] = 0
    output = []
    for pixel_list in pixels:
        output_inner = []
        for pixel in pixel_list:
            output_inner.append(gradient[pixel])
        output.append(output_inner)
    return np.array(output)


def transform_background(pixels):
    result = []
    bit_map = bit_mask(pixels)
    for i, row in enumerate(pixels):
        new_row = []
        for j, pixel in enumerate(row):
            new_row.append(bit_map[i][j] & pixel)
        result.append(new_row)
    return np.array(result, np.uint8)


def bit_mask(pixels):
    bit_map = []
    for i, row in enumerate(pixels):
        new_row = []
        for j, pixel in enumerate(row):
            bit_map_value = 0
            if i < width / 2:
                bit_map_value = 255
            new_row.append(bit_map_value)
        bit_map.append(new_row)
    return bit_map


def keyboard(key, x, y):
    global image
    if key == chr(27).encode():
        sys.exit(0)
    elif key == b'b':
        new_pixels = transform_background(np.array(image.pixel_array))
        load_texture(new_pixels, GL_LUMINANCE)
        display()
    elif key == b'c':
        new_pixels = transform_color_channel(transform_gradient(np.array(image.pixel_array)))
        load_texture(new_pixels, GL_RGB)
        display()
    elif key == b'r':
        load_texture(image.pixel_array, GL_LUMINANCE)
        display()


def reshape(w, h):
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluOrtho2D(0.0, w, 0.0, h)


def display():
    global width, height
    glClear(GL_COLOR_BUFFER_BIT)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex2f(0.0, 0.0)
    glTexCoord2f(0.0, 1.0)
    glVertex2f(0.0, width)
    glTexCoord2f(1.0, 1.0)
    glVertex2f(height, width)
    glTexCoord2f(1.0, 0.0)
    glVertex2f(height, 0.0)
    glEnd()
    glFlush()


def init():
    global image
    load_texture(image.pixel_array, GL_LUMINANCE)
    glEnable(GL_TEXTURE_2D)
    glClearColor(0.0, 0.0, 0.0, 0.0)


def load_image(filename):
    global width, height, image
    image = pydicom.read_file(filename)
    width = image['0028', '0011'].value
    height = image['0028', '0010'].value


def main(filename):
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    load_image(filename)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow('Babenko_Lab_1')
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMainLoop()


def parse_args():
    parser = argparse.ArgumentParser(description="Run Lab 1 DICOM viewer.")
    parser.add_argument(
        "--image",
        type=Path,
        default=DEFAULT_IMAGE_PATH,
        help="Path to the DICOM image.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(str(args.image))
