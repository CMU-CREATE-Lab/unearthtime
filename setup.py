import setuptools

setuptools.setup(
    name='unearthtime',
    version='0.1.7-alpha',
    packages=setuptools.find_packages(),
    url='https://github.com/CMU-CREATE-Lab/unearthtime',
    author='hjhawkinsiv',
    author_email='harry@createlab.org',
    description='EarthTime Automation Framework',
    data_files=[('', ['LICENSE'])],
    install_requires=[
        'numpy=1.19.1',
        'imutils',
        'opencv-python',
        'Pillow',
        'scikit-image',
        'selenium',
        'validators'
    ]
)
