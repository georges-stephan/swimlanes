from setuptools import setup, find_packages

setup(
    name='PySwimlanes',
    python_requires='>3.11.4',
    version='3.5',
    license='Apache 2.0',
    author='Georges Stephan',
    author_email='georges.stephan@icloud.com',
    packages=find_packages(exclude='*_test.py'),
    url='https://github.com/georges-stephan/swimlanes',
    install_requires=['Pillow>=10.1.0','PyYAML>=6.0'],
    entry_points={
        'gui_scripts': ['swimlanes=ui.MainUI:main']
    }
)
