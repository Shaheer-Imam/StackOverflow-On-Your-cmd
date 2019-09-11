try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from codecs import open
import sys

if sys.version_info[:3] < (3, 0, 0):
    print("Requires Python 3 to run.")
    sys.exit(1)

with open("README.md", encoding="utf-8") as file:
    readme = file.read()

setup(
    name="rebound-cli",
    version="2.0.0",
    description="Command-line tool that automatically fetches Stack Overflow results after compiler errors",
    #long_description=readme,
    #long_description_content_type="text/markdown",
    url="https://github.com/Shaheer-Imam/StackOverflow-On-Your-cmd",
    author="Shaheer Ghani Imam",
    author_email="shaheerghaniimam@gmail.com",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Topic :: Software Development :: Debuggers",
        "Natural Language :: English",
        "Programming Language :: Python"
    ],
    keywords="stackoverflow stack overflow debug debugging error-handling compile errors error message cli search commandline",
    include_package_data=True,
    packages=["rebound"],
    entry_points={"console_scripts": ["rebound = rebound.rebound:main"]},
    install_requires=["BeautifulSoup4", "requests", "urllib3", "urwid"],
    requires=["BeautifulSoup4", "requests", "urllib3", "urwid"],
    python_requires=">=3",
    license="MIT"
)
