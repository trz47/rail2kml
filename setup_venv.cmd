@echo off

echo ���z�����쐬���Ă��܂��B
echo:
py -3 -m venv venv

if %errorlevel% neq 0 (
  echo:
  echo �쐬���s���܂����B
  echo Python3���C���X�g�[������Ă��邩�m�F���Ă��������B
  
  echo:
  pause

  exit
)

echo:
echo �ˑ��p�b�P�[�W���C���X�g�[�����Ă��܂��B
echo:
venv\Scripts\python.exe -m pip install -r requirements.txt

if %errorlevel% neq 0 (
  echo:
  echo �C���X�g�[���Ɏ��s���܂����B
  
  echo:
  pause

  exit
)

echo:
echo �������܂����B

echo:
pause

exit
