import setuptools
import pathlib

PKG_NAME = "streamshape"
VERSION = "0.1.2"

# Core dependencies (minimal install)
CORE_REQUIRES = [
    "pydantic>=2.7.0",
    "requests>=2.32.0",
    "python-dotenv>=1.0.1",
    "litellm>=1.45.0",
]

# Provider-specific dependencies
EXTRAS = {
    "openai": ["openai>=1.52.0"],
    "anthropic": ["anthropic>=0.34.0"],
    "google": ["google-genai>=0.6.0"],
    "test": ["pytest>=8.3.0", "pytest-cov>=4.1.0", "pytest-asyncio>=0.21.0", "hypothesis>=6.0.0"],
}

# Convenience bundles
EXTRAS["all"] = (
    EXTRAS["openai"] + 
    EXTRAS["anthropic"] + 
    EXTRAS["google"]
)

setuptools.setup(
    name=PKG_NAME,
    version=VERSION,
    author="Saikethan",
    description='A unified LLM response parser with streaming support for multiple providers',
    url="https://github.com/saikethan27/StreamShape",
    long_description=pathlib.Path('README.md').read_text(encoding='utf-8'),
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    package_data={'streamshape': ['../docs/*.md']},
    install_requires=CORE_REQUIRES,
    extras_require=EXTRAS,
    include_package_data=True,
    python_requires='>=3.8',
    license="MIT",
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
)