# Biomedical Image Processing Labs

This repository contains lab exercises for biomedical image processing using Python, NumPy, pydicom, and PyOpenGL. Each lab script renders or processes DICOM images and can be run as a standalone script with configurable input paths.

## Requirements

- Python 3.8+
- `pydicom`
- `numpy`
- `PyOpenGL` and `PyOpenGL_accelerate`

Install dependencies with:

```bash
pip install pydicom numpy PyOpenGL PyOpenGL_accelerate
```

## Data

Sample DICOM files live under the `Images/` directory:

- `Images/ImageForLab1/`
- `Images/ImageForLab2-6/`
- `Images/ImagesForLab7/`
- `Images/ImagesForLab8/`

Each lab defaults to these repo-relative paths, but you can override them with CLI flags.

## Usage

Run a lab script directly with Python. Examples:

```bash
python Lab1/03_Lab1.py --image Images/ImageForLab1/DICOM_Image_for_Lab_2.dcm
python Lab2/03_Lab2.py --image Images/ImageForLab2-6/DICOM_Image_16b.dcm
python Lab3/03_Lab3.py --image Images/ImageForLab1/DICOM_Image_for_Lab_2.dcm
python Lab4/03_Lab4.py --image Images/ImageForLab2-6/DICOM_Image_16b.dcm
python Lab5/03_Lab5.py --image Images/ImageForLab2-6/DICOM_Image_16b.dcm
python Lab6/03_Lab6.py --image Images/ImageForLab2-6/DICOM_Image_16b.dcm
```

Lab 7 uses a directory of slices and allows the slice count to be configured:

```bash
python Lab7/03_Lab7.py --image-dir Images/ImagesForLab7 --slices 20
```

Lab 8 uses CT + MRI inputs:

```bash
python Lab8/03_Lab8.py --ct-image Images/ImagesForLab8/2-ct.dcm --mri-image Images/ImagesForLab8/2-mri.dcm
```

## Controls

Each lab listens for keyboard input. Refer to the inline `keyboard()` handlers in each lab file for the exact key bindings.

## Testing

This repo does not include automated tests. To run a quick syntax check of the lab scripts:

```bash
python -m compileall Lab1 Lab2 Lab3 Lab4 Lab5 Lab6 Lab7 Lab8
```
