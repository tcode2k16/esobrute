from setuptools import setup

setup(
    name='esobrute',
    version='0.1',
    description='An esoteric programming languages brute forcer powered by tio.run',
    # long_description=long_description,
    # long_description_content_type='text/markdown',
    author='Alan Chang',
    author_email='tcode2k16@gmail.com',
    python_requires='>=2.7, <3',
    url='https://github.com/tcode2k16/esobrute',
    packages=['esobrute'],
    scripts=['scripts/esobrute'],
    install_requires=['requests>=2.20.1', 'termcolor>=1.1.0', 'Click>=7.0'],
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Topic :: Security',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers'
    ]
)