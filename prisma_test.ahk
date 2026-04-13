#Requires AutoHotkey v2.0
#SingleInstance Force

waitTime := 4000
url := A_Args[1]

; Activate browser
Sleep(waitTime)
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
Sleep(waitTime * 1.5)

; Copy entire page
A_Clipboard := ""
Send("^a")
Sleep(500)
Send("^c")

if !ClipWait(2) {
    result := "ERROR"
} else {
    pageText := A_Clipboard

    if pageText == "" {
        result := "TRUE" ; Assume BLOCKED because it didn't load
    }
    else {
        ; Truncate for performance
        pageText := SubStr(pageText, 1, 2000)

        if InStr(pageText, "Restricted website") {
            result := "TRUE"     ; RESTRICTED
        } 
        else if InStr(pageText, "Malicious website") {
            result := "TRUE"      ; MALICIOUS
        }
        else if InStr(pageText, "Performing security verification") {
            result := "FALSE"      ; SECURITY VERIFICATION
        }
        else if InStr(pageText, "DNS_PROBE_FINISHED_NXDOMAIN") {
            result := "TRUE"    ; UNAVAILABLE
        }
        else if InStr(pageText, "403 Forbidden") {
            result := "TRUE"      ; FORBIDDEN
        }
        else if (InStr(StrLower(pageText), "for sale") AND InStr(StrLower(pageText), "domain")) {
            result := "TRUE"        ; FOR SALE
        }
        else {
            result := "FALSE"          ; ALLOWED
        }
    }
}

; Close tab after we're done with it
Send("^w")

Sleep(1000)

; Output
FileDelete(A_Temp "./ahk_output.txt")
FileAppend(result, A_Temp "./ahk_output.txt")

ExitApp()
