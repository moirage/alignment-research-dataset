import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='align_data',
    version='0.0.1',
    description="A framework for constructing a dataset for alignment research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=[
        "bs4==0.0.1",
        "python-dateutil==2.8.2",
        "feedparser==6.0.8",
        "jsonlines==3.0.0",
        "requests==2.27.1",
        "wheel",
        "GitPython",
        "gdown",
        "pypandoc",
    ]
)
