# file: algorithms/setup.py
# 功能: 智能排课算法系统安装配置

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="intelligent-course-scheduling",
    version="1.0.0",
    author="Course Management System Team",
    author_email="team@example.com",
    description="智能排课算法系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/course-management-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
    ],
    extras_require={
        "export": ["openpyxl>=3.0.9", "reportlab>=3.6.0"],
        "parallel": ["multiprocessing-logging>=0.3.4"],
        "dev": ["pytest>=6.2.0", "pytest-cov>=2.12.0"],
    },
    entry_points={
        "console_scripts": [
            "course-scheduling-demo=demo:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
