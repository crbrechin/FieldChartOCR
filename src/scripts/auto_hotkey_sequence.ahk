; AutoHotkey v2 script for key sequence automation
; Press F1 to execute the sequence

F1:: {
    ; Press CTRL+SHIFT+E
    Send("^+e")
    Sleep(100)
    
    ; Press ENTER
    Send("{Enter}")
    Sleep(100)
    
    ; Press ENTER again
    Send("{Enter}")
    Sleep(1000)

    ; Press ENTER again
    Send("{Enter}")
}

; Alternative: Use a different hotkey (uncomment to use)
; ^j:: {  ; CTRL+J to trigger
;     Send("^+e")
;     Sleep(100)
;     Send("{Enter}")
;     Sleep(1000)
;     Send("{Enter}")
      Sleep(1500)
;     Send("{Enter}")
; }
