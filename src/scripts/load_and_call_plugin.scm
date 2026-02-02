; Scheme script to load Python plug-in and call it
; This script attempts to explicitly load the Python plug-in

(define (load-python-plugin plugin-path)
  ; Try to load the Python plug-in explicitly
  ; Note: This may not work in batch mode, but we'll try
  (let* ((result (gimp-plug-in-run plugin-path)))
    result))

; The actual call - try to invoke the registered function
; If the plug-in was auto-loaded, this should work
(define (call-distort-images input-folder suffix)
  (python-fu-distort-images RUN-NONINTERACTIVE input-folder suffix))
