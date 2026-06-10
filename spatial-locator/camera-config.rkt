#lang racket/base

(require "spatial.rkt")

(provide camera/left
         camera/right)

;; These are uncalibrated cameras
(define camera/left
  (make-camera '(-0.3 0.1 1.39)
               '(0.0 0.0 0.0)
                3326.0
                4000 3000))

(define camera/right
  (make-camera (list (+ 3.68 0.3) 0.1 1.39)
               '(0.0 0.0 0.0)
                3326.0
                4000 3000))


