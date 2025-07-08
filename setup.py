"""
Setup script for Web Scraper PDF Generator
"""

from setuptools import setup, find_packages
import os

# README dosyasını oku
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Requirements dosyasını oku
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="webscraper-pdf-generator",
    version="1.0.0",
    author="WebScraper Team",
    author_email="info@webscraper.com",
    description="Web sitelerinden keyword araması yaparak PDF raporu oluşturan uygulama",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ichrasit/webscrapertopdf",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "webscraper=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
