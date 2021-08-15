@echo off

echo 仮想環境を作成しています。
echo:
py -3 -m venv venv

if %errorlevel% neq 0 (
  echo:
  echo 作成失敗しました。
  echo Python3がインストールされているか確認してください。
  
  echo:
  pause

  exit
)

echo:
echo 依存パッケージをインストールしています。
echo:
venv\Scripts\python.exe -m pip install -r requirements.txt

if %errorlevel% neq 0 (
  echo:
  echo インストールに失敗しました。
  
  echo:
  pause

  exit
)

echo:
echo 完了しました。

echo:
pause

exit
