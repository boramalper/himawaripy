Dim path
set oShell = CreateObject("WScript.Shell")
set fso = CreateObject("Scripting.FileSystemObject")
path = fso.GetAbsolutePathName("./auto.bat")
' msgbox path
oShell.run path, 0, ture
