pushd N:\[iTest]\iData
rd /s /q build
rd /s /q dist
rd /s /q iLog.egg-info
echo C:\Python27\python setup.py install 


C:\Python27\python setup.py bdist_egg


xcopy /y dist\iData-0.1-py2.7.egg D:\site\trac\plugins

pause

