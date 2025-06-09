# build-web.spec
# Run with: poetry run pyinstaller build-web.spec

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os
import sys
import nicegui
import site
from pathlib import Path

project_dir = os.path.abspath(".")
#settings_file = os.path.join(project_dir, "syncapp", "webui", "settings.json")

# Get NiceGUI package directory and static files
nicegui_dir = os.path.dirname(nicegui.__file__)
nicegui_static = os.path.join(nicegui_dir, 'static')

# Collect all necessary data files
datas = [
#   (settings_file, 'syncapp/webui'),
#   (os.path.join(project_dir, '.secret_key'), '.'),
    (nicegui_static, 'nicegui/static'),
]

# Add any additional data files from dependencies
datas.extend(collect_data_files('nicegui'))
datas.extend(collect_data_files('selenium'))
datas.extend(collect_data_files('bs4'))
datas.extend(collect_data_files('platformdirs'))

# Collect all necessary submodules
hiddenimports = [
    *collect_submodules('nicegui'),
    *collect_submodules('selenium'),
    *collect_submodules('bs4'),
    *collect_submodules('platformdirs'),
    'typer',
    'cryptography',
    'requests',
    'webdriver_manager',
    'uvicorn',
    'fastapi',
    'starlette',
    'pydantic',
    'email_validator',
    'python-multipart',
    'websockets',
    'aiofiles',
    'jinja2',
    'markupsafe',
    'click',
    'rich',
    'shellingham',
]

a = Analysis(
    ['syncapp/webui/appv4.py'],
    pathex=[project_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['bs4.tests'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='sync-ui-web',
    debug=False,
    strip=False,
    upx=True,
    console=True,
    icon=None,
    bootloader_ignore_signals=False,
    onefile=True,
)