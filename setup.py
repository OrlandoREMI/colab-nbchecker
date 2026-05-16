from setuptools import setup, find_packages

setup(
    name="colab-nbchecker",
    version="0.1.0",
    description="Verificador automático de ejercicios de Pandas para Google Colab",
    author="OrlandoREMI",
    url="https://github.com/OrlandoREMI/colab-nbchecker",
    packages=find_packages(),
    install_requires=["pandas>=1.3", "numpy>=1.21"],
    python_requires=">=3.7",
)
