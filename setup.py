from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()
setup(
    name="psycossh",
    version="0.0.1",
    packages=["psycossh"],
    url="https://github.com/mpca-adau/psycossh",
    license="LGPL-3.0",
    author="Daniel Sullivan",
    author_email="daniel.sullivan@state.mn.us",
    description="A ConnectionFactory for use by psycopg2 to enable SSH Tunneling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["sshtunnel", "psycopg2", "sqlalchemy"],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
    ],
)
