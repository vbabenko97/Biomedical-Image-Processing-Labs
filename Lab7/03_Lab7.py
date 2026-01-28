# Copyright © 2020. All rights reserved.
# Authors: Vitalii Babenko
# Contacts: vbabenko2191@gmail.com

import argparse
from pathlib import Path
import sys
from math import radians, cos, sin

import numpy as np
import pydicom
from OpenGL.GL import *
from OpenGL.GLUT import *

DEFAULT_IMAGE_DIR = Path(__file__).resolve().parents[1] / "Images" / "ImagesForLab7"


def zagruzka_texturi():
    glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, visota, shirina, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, image_pixels[t1])
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glEnable(GL_TEXTURE_2D)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex3f(0, 0, t1 * (slice_thickness + space_between_slices) / visota)
    glTexCoord2f(1, 0)
    glVertex3f(1, 0, t1 * (slice_thickness + space_between_slices) / visota)
    glTexCoord2f(1, 1)
    glVertex3f(1, 1, t1 * (slice_thickness + space_between_slices) / visota)
    glTexCoord2f(0, 1)
    glVertex3f(0, 1, t1 * (slice_thickness + space_between_slices) / visota)
    glEnd()
    glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, visota, 32, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, sag_pixels[t2])
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex3f(t2 / visota, 0, 0)
    glTexCoord2f(1, 0)
    glVertex3f(t2 / visota, 1, 0)
    glTexCoord2f(1, n / 32)
    glVertex3f(t2 / visota, 1, n * (slice_thickness + space_between_slices) / visota)
    glTexCoord2f(0, n / 32)
    glVertex3f(t2 / visota, 0, n * (slice_thickness + space_between_slices) / visota)
    glEnd()
    glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, shirina, 32, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, front_pixels[t3])
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex3f(0, t3 / visota, 0)
    glTexCoord2f(1, 0)
    glVertex3f(1, t3 / visota, 0)
    glTexCoord2f(1, n / 32)
    glVertex3f(1, t3 / visota, n * (slice_thickness + space_between_slices) / visota)
    glTexCoord2f(0, n / 32)
    glVertex3f(0, t3 / visota, n * (slice_thickness + space_between_slices) / visota)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    glFlush()


def inicializaci9():
    glClearColor(0, 0, 0, 0.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)
    glRotatef(-60, 1, 0, 0)
    glRotatef(45, 0, 0, 1)


def text(x, y, z, font, text):
    glColor3f(1, 1, 1)
    glRasterPos3f(x, y, z)
    for c in text:
        glutBitmapCharacter(font, ctypes.c_int(ord(c)))


def osi():
    glColor3f(1, 1, 1)
    glBegin(GL_LINES)
    glVertex3f(-2.0, 0.0, 0.0)
    glVertex3f(2.0, 0.0, 0.0)
    glVertex3f(0.0, -2.0, 0.0)
    glVertex3f(0.0, 2.0, 0.0)
    glVertex3f(0.0, 0.0, -2.0)
    glVertex3f(0.0, 0.0, 2.0)
    glEnd()
    text(1.2, 0, 0, GLUT_BITMAP_HELVETICA_18, "x")
    text(0, 1.2, 0, GLUT_BITMAP_HELVETICA_18, "y")
    text(0, 0, 0.9, GLUT_BITMAP_HELVETICA_18, "z")


def otobrajeni3():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    osi()
    zagruzka_texturi()
    glutSwapBuffers()


def normalizaci9(pixeli):
    min = np.min(pixeli)
    max = np.max(pixeli)
    noviy_min = 0
    noviy_max = 255
    norm = (pixeli - min) / (max - min) * (noviy_max - noviy_min) + noviy_min
    return norm.astype(int)


def transformaciya(ugol):
    R = np.array([[cos(radians(ugol)), 0, sin(radians(ugol)), 0], [0, 1, 0, 0],
                  [-sin(radians(ugol)), 0, cos(radians(ugol)), 0], [0, 0, 0, 1]], dtype=float).transpose()
    return R


def najati3(key, x, y):
    global t1, t2, t3, ugol
    if key == chr(27).encode():
        sys.exit(0)
    if key == b't':
        ugol = int(input("Angle (deg): "))
        M = transformaciya(ugol)
        glMultMatrixf(M)
    if key == b'r':
        M = transformaciya(-ugol)
        glMultMatrixf(M)
    elif key == b'w' and t1 < n - 1:
        t1 += 1
    elif key == b's' and t1 > 0:
        t1 -= 1
    elif key == b'd' and t2 < shirina - 1:
        t2 += 1
    elif key == b'a' and t2 > 0:
        t2 -= 1
    elif key == b'z' and t3 < visota - 1:
        t3 += 1
    elif key == b'c' and t3 > 0:
        t3 -= 1
    otobrajeni3()


def glavnaya_funkci9():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(shirina * 2, visota * 2)
    glutInitWindowPosition(255, 255)
    glutCreateWindow('Babenko_lab7')
    inicializaci9()
    glutDisplayFunc(otobrajeni3)
    glutKeyboardFunc(najati3)
    glutMainLoop()


def parse_args():
    parser = argparse.ArgumentParser(description="Run Lab 7 volume renderer.")
    parser.add_argument(
        "--image-dir",
        type=Path,
        default=DEFAULT_IMAGE_DIR,
        help="Directory containing brain_###.dcm images.",
    )
    parser.add_argument(
        "--slices",
        type=int,
        default=20,
        help="Number of slices to load.",
    )
    return parser.parse_args()


def main():
    global n, shirina, visota
    global image_pixels, front_pixels, sag_pixels
    global slice_thickness, space_between_slices
    global t1, t2, t3

    args = parse_args()
    n = args.slices
    shirina, visota = 256, 256
    image_pixels = np.zeros((n, visota, shirina))
    front_pixels = np.zeros((visota, n + 12, shirina))
    sag_pixels = np.zeros((shirina, n + 12, visota))

    for i in range(n):
        filename = args.image_dir / f"brain_{i + 1:03d}.dcm"
        dcm = pydicom.read_file(str(filename))
        slice_thickness = dcm['0018', '0050'].value
        space_between_slices = dcm['0018', '0088'].value
        image_pixels[i] = normalizaci9(dcm.pixel_array)

    for i in range(visota):
        for j in range(n):
            for k in range(shirina):
                front_pixels[i][j][k] = image_pixels[j][i][k]

    for i in range(shirina):
        for j in range(n):
            for k in range(visota):
                sag_pixels[i][j][k] = image_pixels[j][k][i]

    t1, t2, t3 = 0, 0, 0
    glavnaya_funkci9()


if __name__ == "__main__":
    main()
