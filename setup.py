import setuptools

setuptools.setup(
        name='pykulon912',
        version='0.1',
        author="Krystian Dużyński",
        author_email="krystian.duzynski@gmail.com",
        description="Kulon 912 connector",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        install_requires=[
            'requests>=2',
            'lxml>=4',
        ],
)
