from setuptools import setup, find_packages

setup(
    name="ipynb_autograde",
    version="0.0.79",
    packages=find_packages(),
    license="GNU Lesser General Public License v3.0",
    description="Autograde for ipynb",
    author="Alex Lopes Pereira",
    author_email="alexlopespereira@gmail.com",
    url="https://github.com/alexlopespereira/ipynb-autograde",
    download_url="https://github.com/alexlopespereira/ipynb-autograde/archive/v0.0.79.tar.gz",
    keywords=['ipynb', 'notebook', 'autograde', 'colab', 'jupyter'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Intended Audience :: Education',
        'Topic :: Education :: Computer Aided Instruction (CAI)',
        'Topic :: Education :: Testing',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    install_requires=[
        'setuptools>=57.0.0',
        'requests>=2.25.1',
        'numpy>=1.19.5',
        'pandas>=1.1.5'
    ],
    package_data={
        'ipynb_autograde': ["autograde/*.py"],
    },
    include_package_data=True,
)
