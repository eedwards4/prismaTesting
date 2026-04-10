#Requires AutoHotkey v2.0
#SingleInstance Force

DllCall("AttachConsole", "int", -1)

waitTime := 4000
url := A_Args[1]

; Activate browser
WinActivate("New Tab - Prisma Browser")
WinWaitActive("New Tab - Prisma Browser", , 3)

; New tab
Send("^t")
Sleep(200)

; Navigate
Send("^l")
Sleep(100)
Send("^a")
Sleep(50)
Send(url)
Sleep(50)
Send("{Enter}")

; Wait for load
Sleep(waitTime)

; Copy entire page
A_Clipboard := ""
Send("^a")
Sleep(100)
Send("^c")

if !ClipWait(2) {
    result := "ERROR"
} else {
    pageText := A_Clipboard

    ; Optional: truncate for performance
    pageText := SubStr(pageText, 1, 2000)

    if InStr(pageText, "Restricted website") {
        result := "TRUE"    ; BLOCKED
    } else {
        result := "FALSE"   ; ALLOWED
    }
}

; Output to stdout
FileAppend(result, "*")

ExitApp()
