@echo off

if exist venv\Scripts\python.exe (
    start venv\Scripts\pythonw.exe app.py
) else (
    echo ���s����ɂ́A���z�����쐬���Ă��������B
    echo ���z�����쐬����ɂ́A"setup_venv.cmd"�����s���Ă��������B

    echo:
    pause
)

exit
