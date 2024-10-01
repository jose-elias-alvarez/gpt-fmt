from setuptools import setup  # pyright: ignore[reportUnknownVariableType]

setup(
    name="gpt-fmt",
    version="0.0.1",
    install_requires=["openai>=1.41.0"],
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "gpt-fmt=gpt_fmt.main:main",
        ],
    },
)
