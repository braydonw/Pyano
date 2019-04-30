@echo off
echo "hello,world"
if exist config7_back.txt (goto exit)else (copy config.txt config7_back.txt)

:exit 
copy config-7-1024x600.txt config.txt
pause