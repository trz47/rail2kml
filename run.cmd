@echo off

if exist venv\Scripts\python.exe (
    start venv\Scripts\pythonw.exe app.py
) else (
    echo 実行するには、仮想環境を作成してください。
    echo 仮想環境を作成するには、"setup_venv.cmd"を実行してください。

    echo:
    pause
)

exit
