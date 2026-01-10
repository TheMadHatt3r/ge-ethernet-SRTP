from setuptools import setup, find_packages

setup(
    name='ge_ethernet_srtp',
    version='0.1',
    packages=['ge_ethernet_srtp'],
    package_dir={'ge_ethernet_srtp': 'lib'},
    author='TheMadHatt3r',
    description='A description of your library',
    long_description='A longer description of your library',
    long_description_content_type='text/markdown',
    url='https://github.com/DSchana/ge-ethernet-SRTP',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='Emerson GE PLC Libarary',
    project_urls={
        'Source': 'https://github.com/DSchana/ge-ethernet-SRTP',
        'Bug Reports': 'https://github.com/TheMadHatt3r/ge-ethernet-SRTP/issues',
    },
)
