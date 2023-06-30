from setuptools import setup, find_packages

setup(
    name='rdp',
    version='0.1.0',
    author='hctilg',
    packages=find_packages(),
    install_requires=[
        'pyTelegramBotAPI',
        'screen_brightness_control',
        'opencv-python',
        'pyautogui',
        'requests',
        'pyautogui',
        'pulsectl',
        'psutil',
        'GPUtil',
    ],
    description='Remote Desktop Protocol (OsRemoter)',
    url='https://github.com/hctilg/rdp.git',
)