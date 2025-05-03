from setuptools import setup, find_packages

setup(
    name="deepl_api",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.25.1",
        "pydantic>=2.0.0",
    ],
    python_requires=">=3.8",
    author="Claude",
    author_email="example@example.com",
    description="Python client for the DeepL API",
    keywords="deepl, translation, api",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)