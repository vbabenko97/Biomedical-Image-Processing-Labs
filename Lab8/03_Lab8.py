# Copyright © 2020. All rights reserved.
# Authors: Vitalii Babenko
# Contacts: vbabenko2191@gmail.com

import argparse
from pathlib import Path
import sys

import pydicom
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *

DEFAULT_CT_IMAGE_PATH = Path(__file__).resolve().parents[1] / "Images" / "ImagesForLab8" / "2-ct.dcm"
DEFAULT_MRI_IMAGE_PATH = Path(__file__).resolve().parents[1] / "Images" / "ImagesForLab8" / "2-mri.dcm"


def get_image1():
    return get_colored_image(image1)


def get_image2():
    return get_colored_image(image2)


def get_multi_image():
    pixels = []
    for i, row in enumerate(get_pixels(image1)):
        new_row = []
        for j, value in enumerate(row):
            new_row.append([0, get_pixel(image1, i, j), get_pixel(image2, i, j)])
        pixels.append(new_row)
    return pixels


def get_half_multi_image():
    pixels = []
    half = get_width(image2) / 1.75
    for i, row in enumerate(get_pixels(image1)):
        new_row = []
        for j, value in enumerate(row):
            if i <= half:
                pixel = get_pixel(image1, i, j)
                new_row.append([pixel, pixel, pixel])
            else:
                new_row.append([0, get_pixel(image1, i, j), get_pixel(image2, i, j)])
        pixels.append(new_row)
    return pixels


def get_width(image):
    return image['0028', '0011'].value


def get_height(image):
    return image['0028', '0010'].value


def get_pixels(image):
    return image.pixel_array


def get_pixel(image, x, y):
    return image.pixel_array[x][y]


def get_colored_image(image, color=None):
    pixels = []
    for row in get_pixels(image):
        new_row = []
        for value in row:
            if 'r' == color:
                new_row.append([value, 0, 0])
            elif 'g' == color:
                new_row.append([0, value, 0])
            elif 'b' == color:
                new_row.append([0, 0, value])
            else:
                new_row.append([value, value, value])
        pixels.append(new_row)
    return pixels


def load_image(filename1, filename2):
    global image1, image2
    image1 = pydicom.read_file(filename1)
    image2 = pydicom.read_file(filename2)


def init():
    glBindTexture(GL_TEXTURE_2D, glGenTextures(1))
    gl_tex_image_2d()
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glEnable(GL_TEXTURE_2D)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glMatrixMode(GL_MODELVIEW)


def display():
    glClearColor(0.0, 0.0, 0.0, 0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glBegin(GL_QUADS)
    width = get_width(image2)
    height = get_height(image2)
    glTexCoord(1.0, 1.0)
    glVertex(-width / 2, -height / 2)
    glTexCoord(0.0, 1.0)
    glVertex(width / 2, -height / 2)
    glTexCoord(0.0, 0.0)
    glVertex(width / 2, height / 2)
    glTexCoord(1.0, 0.0)
    glVertex(-width / 2, height / 2)
    glEnd()
    glFlush()


def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    width = get_width(image2)
    height = get_height(image2)
    gluOrtho2D(-width / 2, width / 2, -height / 2, height / 2)


def gl_tex_image_2d():
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, get_width(image1), get_height(image1), 0, GL_RGB, GL_UNSIGNED_BYTE, pixels)


def keyboard(key, x, y):
    global pixels
    if key == chr(27).encode():
        sys.exit(0)
    if key == b'1':
        pixels = get_image1()
    if key == b'2':
        pixels = get_image2()
    if key == b'3':
        pixels = get_multi_image()
    if key == b'4':
        pixels = get_half_multi_image()
    gl_tex_image_2d()
    display()


def parse_args():
    parser = argparse.ArgumentParser(description="Run Lab 8 multi-modal image viewer.")
    parser.add_argument(
        "--ct-image",
        type=Path,
        default=DEFAULT_CT_IMAGE_PATH,
        help="Path to the CT DICOM image.",
    )
    parser.add_argument(
        "--mri-image",
        type=Path,
        default=DEFAULT_MRI_IMAGE_PATH,
        help="Path to the MRI DICOM image.",
    )
    return parser.parse_args()


def main():
    global pixels
    args = parse_args()
    pixels = []
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    load_image(str(args.ct_image), str(args.mri_image))
    glutInitWindowSize(get_width(image2), get_height(image2))
    glutInitWindowPosition(255, 255)
    glutCreateWindow('Babenko_lab8')
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMainLoop()


if __name__ == "__main__":
    main()
