
gui, font, s9, Arial
Gui, Add, Text, cBlack, F4 - включить бота (выточить ящик)`nF5 - остановить работу (перезапустить скрипт)
Gui, Add, Text, cBlue, YouTube Морская Пехота Rust <3
Gui, Show, xCenter yCenter w350 h100
return

F5:: Reload
#CommentFlag //
WinActivate Rage Multiplayer

f4::
Send {e}
cnt = 0
Loop {
	if ErrorLevel = 1
		cnt += 1
	if cnt > 50	
		break
	//Sleep, 1
	ImageSearch, x, y, 0, 0, 1920, 1080, *10 %A_ScriptDir%\i3.png
	xf :=x+20
	yf :=y+62
	MouseMove,%xf%,%yf%,0
	//MouseClick, left, %xf%, %yf%

}
Return




