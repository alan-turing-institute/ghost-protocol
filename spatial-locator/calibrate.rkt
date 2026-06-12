#lang racket/base

(require racket/class)
(require racket/gui/base)

(require (only-in racket/math pi))

(require net/rfc6455
         net/url
         json)

(require "config.rkt"
         "spatial.rkt"
         "camera-config.rkt"
         "reference-datum.rkt")

;; width : width of the window, in metres
(struct state (lcam rcam width) #:mutable #:transparent)
(define *state* (state camera/left camera/right 8))

;; ----------------------------------------------------------------------

;; drawing-context? state? 
(define (draw-the-scene dc st)
  ;; Draw in world x-y coordinates, in metres. Set up location so that
  ;; the centre of the screen is in the middle of the display and 0.5m
  ;; up from the bottom edge
  (define-values (wd ht) (send dc get-size))
  (define scale-factor (/ wd (state-width st)))

  (send dc set-origin
           (* 0.5 scale-factor (- (state-width st) SCREEN_WIDTH))
           (- ht (* 0.5 scale-factor 0.4)))
  (send dc set-scale scale-factor (- scale-factor))
  
  ;; All draw- draw in metres, relative to the world origin at
  ;; bottom-left of the screen
  (draw-camera dc (state-lcam st))
  (draw-camera dc (state-rcam st))
  (draw-screen dc)
  (draw-reception-desk dc)
  (draw-bar dc)
  (draw-floor-mark dc)
  (draw-camera dc (state-lcam st))
  ;; (draw-camera dc (state-rcam st))
  )

(define no-pen (new pen% [style 'transparent]))
(define no-brush (new brush% [style 'transparent]))
(define col1 (send the-color-database find-color "pale green"))
(define camera-view-colour (make-color (send col1 red) (send col1 green) (send col1 blue) 0.3))

(define (draw-screen dc)
  (send dc set-pen no-pen)
  (send dc set-brush "dark blue" 'solid)
  (send dc draw-rectangle 0 -0.05 SCREEN_WIDTH 0.1))

(define (draw-reception-desk dc)
  (define x (:x RECEPTION))
  (define y (:y RECEPTION))
  (send dc set-brush no-brush)
  (send dc set-pen "dark blue" 0.05 'solid)
  (send dc draw-lines
        (list (cons x (+ y 0.3))
              (cons x y)
              (cons (- x 0.3) y))))

(define (draw-bar dc)
  (define x (:x BAR))
  (define y (:y BAR))
  (send dc set-brush no-brush)
  (send dc set-pen "dark blue" 0.05 'solid)
  (send dc draw-lines
        (list (cons x (+ y 0.6))
              (cons x y)
              (cons (+ x 0.6) y))))

(define (draw-floor-mark dc)
  (define x (:x FLOOR_MARK))
  (define y (:y FLOOR_MARK))
  (send dc set-brush no-brush)
  (send dc set-pen "sienna" 0.05 'solid)
  (send dc draw-line (- x 0.05) (- y 0.05) (+ x 0.05) (+ y 0.05) )
  (send dc draw-line (- x 0.05) (+ y 0.05) (+ x 0.05) (- y 0.05)))

(define (draw-camera dc cam)

  (define x (:x (camera-pos cam)))
  (define y (:y (camera-pos cam)))

  ;; Orientation of the camera
  (define us (list (camera-u cam) (camera-n cam) (camera-v cam)))
  (define α (car (rotation-matrix->euler (unit-vectors->rotation-matrix us))) )

  ;; Aspect ratio of camera
  (define aspect (/ (camera-wd cam) (camera-f cam)))
  (define far 8.0)
  
  (define view (new dc-path%))
  (send view move-to 0 0)
  (send view lines
        (list (cons (* 0.5 far aspect) far)
              (cons (- (* 0.5 far aspect)) far)))
  (send view close)
  (send view rotate (- α))

  (send dc set-pen no-pen)
  (send dc set-brush camera-view-colour 'solid)
  (send dc draw-path view x y)

  (send dc set-brush "dark green" 'solid)
  (send dc draw-ellipse (+ x -0.1) (+ y -0.1) 0.2 0.2)
  )




;; ----------------------------------------------------------------------

(module+ main

  (define *frame* (new frame%
                       [label "Camera image"]
                       [width 480]
                       [height 640]))

  (new canvas%
       [parent *frame*]
       [style '(border)]
       [paint-callback
        (λ (_ dc)
          (draw-the-scene dc *state*))])

  (send *frame* show #t)
  
  )

