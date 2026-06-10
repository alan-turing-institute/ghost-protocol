#lang racket/base

(require racket/class)
(require racket/gui/base)

(require "spatial.rkt")

;; (require (only-in "reference-lines.rkt"
;;                   [points *ref-points*] ; A vector of (x y z) tuples 
;;                   [lines *ref-lines*])) ; A list of (pt1 pt2) pairs

(module+ main
  (define *frame* (new frame%
                       [label "Camera image"]
                       [width 600]
                       [height 400]))
  (new canvas% [parent *frame*] [style '(border)]
       [paint-callback
        (λ (canvas dc)
          (send dc set-scale 3 3)
          (send dc set-text-foreground "blue")
          (send dc draw-text "Don't Panic!" 0 0))])

  (send *frame* show #t)
  
  )

