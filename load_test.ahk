#Requires AutoHotkey v2.0
#SingleInstance Force

waitTime := 4000

; Activate browser
Sleep(waitTime)
WinActivate("Noisestorm - Crab Rave [Monstercat Release] - YouTube - Prisma Browser")
WinWaitActive("Noisestorm - Crab Rave [Monstercat Release] - YouTube - Prisma Browser", , 3)

; New tab
Send("^t")
Sleep(200)

; Navigate
Send("^l")
Sleep(100)
Send("^a")
Sleep(50)
Send("https://www.youtube.com/watch?v=LDU_Txk06tM") ; Infinite crab rave baby
Sleep(50)
Send("{Enter}")

; Wait for load
Sleep(waitTime * 1.5)

ExitApp()