#TO-DO's for Editor
##_Functionalities_
####Now
* Bug Fixes
####Later
* Add a section to chose auto complete brackets options in Settings Window.
* Control Icons on menuBar for fullscreen mode
##_Bugs_

_Not Discovered yet!_

 ##Recent Activities
 **_Feature Added_** : Disabled textArea with some information when no file is open.
 **_Bug Fixed_** : Text does not clear when closing a file.
 **_Bug Fixed_** : Output Window Doubling height when closing after opening using ctrl+r fixed.
 **_Bug Fixed_** : AutoComplete brackets now working.  
 **_Feature Added_** : Auto Indent on ENTER inside empty brackets.  
 **_Feature Added_** : Key Bindings on Find/Replace Entry(Enter,Down arrow, Up arrow)  
 **_Feature Added_** : Replace,ReplaceAll  
 **_Feature Added_** : FindNext,FindPrevious,FindAll  


# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['editor.py'],
             pathex=['G:\\anish\\Editor\\Editor'],
             binaries=[],
             datas=[('py1.ico','.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='editor',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='py1.ico')
