from setuptools import setup, find_packages

setup(
    name="GazeTracking",
    version="0.1",
    packages=find_packages(),
    install_requires=["opencv-python", "dlib", "numpy"],
)