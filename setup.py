import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sbroccoli",
    version="0.0.1",
    author="Modamod",
    author_email="modhaffer.rahmani@gmail.com",
    description="An invoke based package to do day to day",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/modamod/special-broccoli",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['invoke'],
    entry_points={
        'console_scripts': ['uinv = sbroccoli.main:program.run']
    }
)