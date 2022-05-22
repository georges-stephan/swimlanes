from setuptools import setup, find_packages

setup(
    name='PySwimlanes',
    python_requires='>3.10.0',
    version='3.0',
    license='Apache 2.0',
    author='Georges Stephan',
    author_email='georges.stephan@icloud.com',
    packages=find_packages(exclude='*_test.py'),
    url='https://github.com/georges-stephan/swimlanes',
    install_requires=['Pillow>=9.0','pyaml'],
    entry_points={
        'gui_scripts': ['swimlanes=ui.MainUI:main']
    }
)
