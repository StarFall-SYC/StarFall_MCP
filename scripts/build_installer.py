import sys
from PyInstaller.__main__ import run

if __name__ == '__main__':
    opts = {
    'version_file': 'version.txt',
        'name': 'install',
        'icon': 'app.ico',
        'script': 'gui_installer.py',
        'onefile': True,
        'noconsole': True,
        'add-data': 'app.ico;.'
    }
    
    args = [
        '--name=%s' % opts['name'],
        '--icon=%s' % opts['icon'],
        '--onefile',
        '--noconsole',
        '--add-data=%s' % opts['add-data'],
        opts['script']
    ]
    
    run(args)