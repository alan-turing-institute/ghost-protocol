#lang racket/base

(require (only-in "spatial.rkt"
                  vec+ 
                  x+ y+ z+))

(provide SCREEN_BL SCREEN_BR SCREEN_TR SCREEN_TL
         RECEPTION
         BAR
         FIRST_AID
         CCTV
         FLOOR_MARK
         ENTRANCE)


;; Coordinates in 3d of a set of reference lines indicating the positions
;; of points in the room

(define SCREEN_WIDTH 3.68)
(define SCREEN_HEIGHT 2.06)

(define SCREEN_BL  '(0.00 0.00 0.27))
(define SCREEN_BR  (x+ SCREEN_BL SCREEN_WIDTH))
(define SCREEN_TR  (z+ SCREEN_BR SCREEN_HEIGHT))
(define SCREEN_TL  (z+ SCREEN_BL SCREEN_HEIGHT))
(define RECEPTION  '(-0.32 7.26 1.10))
(define BAR        '(3.17 7.10 1.10))
(define FIRST_AID  '(2.06 9.12 1.61))
(define CCTV       '(1.14 3.66 2.48))
(define FLOOR_MARK '(1.84 3.71 0.0))
(define ENTRANCE   '(1.77 2.22 0.0))


