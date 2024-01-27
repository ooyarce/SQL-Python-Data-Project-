from setuptools import setup, find_packages

setup(
    name='pyseestko',  # Elige un nombre único para tu paquete
    version='1.0.0',  # Sigue el versionado semántico (https://semver.org/lang/es/)
    author='Omar Ignacio Oyarce Acharan',
    author_email='oioyarce@miuandes.cl',
    description='A integral package that makes an analysis of results with OpenSees, STKO, MySQL and Python.',
    long_description=open('README.md').read(),  
    long_description_content_type='text/markdown',  
    url='https://github.com/ooyarce/Thesis-Project-Simulation-Data-Analysis',
    packages=find_packages(),  # Encuentra automáticamente todos los paquetes
    install_requires=[
    'pandas>=1.0.0',     
    'numpy>=1.18.0',
    'mysql-connector-python>=8.0.0', 
    'matplotlib>=3.1.0',
    'xlsxwriter>=1.2.8',
                    ],
    classifiers=[
        # Clasificadores que describen el estado y la audiencia de tu paquete
        'Development Status :: 3 - Alpha',  
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.11',  
    include_package_data=True, 
)
