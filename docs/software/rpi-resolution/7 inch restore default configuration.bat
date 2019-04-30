@echo off
echo "hello,world"
if exist config7_back.txt (goto exit)else (goto exit1)

:exit 
copy config7_back.txt config.txt
:exit1

pause