from setuptools import setup, find_packages

setup(
    name="ace-python",
    version="0.1.0",
    packages=find_packages(exclude=["tests", "examples"]),
    install_requires=[
        "pandas",
        "numpy",
    ],
    author="Arjun Puri",
    author_email="arjunpur2@gmail.com",
    description="A Python package for processing ACE (Adaptive Cognitive Evaluation) data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/arjunpur/ace-python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
