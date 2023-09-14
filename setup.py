from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    readme = fh.read()


setup(
    name='os-downloader',
    version='v1.0.0,
    url='https://github.com/stefanomartins/os-downloader',
    license='MIT License',
    author='Stefano Martins',
    long_description=readme,
    long_description_content_type="text/markdown",
    description='OS Downloader is a CLI tool for downloading subtitles from opensubtitles.com',
    packages=find_packages(),
    install_requires=[
        'requests',
        'argparse'
    ],
    entry_points={
        'console_scripts': [
            'os-downloader = os_downloader.main:main'
        ]
    }
)
