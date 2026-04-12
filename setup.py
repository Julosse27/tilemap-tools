from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='tilemap-tools',
    version='1.5.0',
    license= "MIT License",

    author='Julosse',
    author_email="julosse27110@gmail.com",
    
    description='Outils pour créer et manipuler des tilemaps',
    long_description=long_description,
    long_description_content_type="text/markdown",

    packages=find_packages(),
    include_package_data=True,

    python_requires='>=3.8',

    install_requires=[
        'pillow>=9.0.0',
        'pyxel>=1.9.0',
    ],

    entry_points={
        'console_scripts': [
            'tilemap=tilemap_tools.cli:main',
        ],
    },

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Games/Entertainment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    
    keywords='tilemap game-dev pixel-art pyxel',
    
    project_urls={
        'Source': 'https://github.com/Julosse27/tilemap-tools',
    },
)