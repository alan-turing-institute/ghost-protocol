#lang racket/base
(require "spatial.rkt")


;; TODO: Lead both cameras from `cameras.scm`

;; Uncalibrated cameras
;; Just left of the screen and just right of the screen
(define uncalibrated-camera-L (camera -0.3 0.1 1.39
                                      0.0 0.0 0.0
                                      640 480 2665.0))

(define uncalibrated-camera-R (camera (+ 3.68 0.3) 0.1 1.39
                                      0.0 0.0 0.0
                                      640 480 2665.0))

