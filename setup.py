from setuptools import setup, find_packages

setup(
    name='highlevel-python',
    version='0.1.0',  # Update this version as needed
    description='A Python package to interface with HighLevel API.',
    author='Justin Farmer',
    author_email='justinlf@gmail.com',
    url='https://github.com/godzilla74/highlevel-python',
    packages=find_packages(),  # Automatically find your packages
    install_requires=[],       # Add external dependencies if needed
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Or any other license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Specify minimum Python version
)
