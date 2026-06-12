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
;; pos : position of the head
;; ts : moving-average timestamp
(struct state (lcam rcam width pos ts) #:mutable #:transparent)
(define *state* (state camera/left camera/right 8 '(2 4 1.8) 0))

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
  (draw-head dc (state-pos st))
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

(define head-radius 0.15)
(define (draw-head dc pos)
  (define x (:x pos))
  (define y (:y pos))
  (send dc set-pen "dark red" 0.01 'solid)
  (send dc set-brush "red" 'solid)
  (send dc draw-ellipse (- x head-radius) (- y head-radius) (* 2 head-radius) (* 2 head-radius)))



;; ----------------------------------------------------------------------

(module+ main

  (define *frame* (new frame%
                       [label "Camera image"]
                       [width 480]
                       [height 640]))

  (define *canvas*
    (new canvas%
         [parent *frame*]
         [paint-callback
          (λ (_ dc)
            (draw-the-scene dc *state*))]))

  (send *frame* show #t)

  (define *es* (current-eventspace))
  
  ;; Web-socket-y stuff

  (display (format "Connecting to websocket-server on ~a ... " ws-server-url))
  (define the-server (ws-connect (string->url ws-server-url)))

  (displayln "connected.\n")
  
  ;; Main loop
  
  (thread
   (λ ()
     (dynamic-wind ;; Ensure clean disconnection in case of ctrl-C
       void ; no pre-thunk neededm
       ;; Main loop
       (λ ()
         (let loop ()
           (unless (ws-conn-closed? the-server)
             ;; Wait until message available
             (define msg
               (string->jsexpr (sync (ws-recv-evt the-server))))
             (parameterize ([current-eventspace *es*])
               ;; Despatch on message type
               ;; Much imperative
               (cond
                 [(not (hash? msg)) (void)]
                 [(hash-has-key? msg 'headLocation) ; Received head location data
                  ;; (displayln (hash-ref msg 'faceResult))
                  (define-values (the-head ts)
                    (parse-message (hash-ref msg 'headLocation)))
                  
                  ;; Update moving-average time between frames
                  ;; (define new-δt (+ (* 0.25 (- new-ts (state-last-timestamp *global-state*)))
                  ;;                   (* 0.75 (state-δt *global-state*))))


                  (queue-callback
                   (λ ()
                     (set-state-pos! *state* the-head)
                     (send *canvas* refresh)))]))
             (loop)))
         )
       ;; Close the connection cleanly
       (λ () 
         (displayln "Closing down...")
         (ws-close! the-server #:status 1001 #:reason "Client shutting down.")
         (exit)
         ))))
  
  )

(define (parse-message msg)
  (values (hash-ref msg 'location)
          (hash-ref msg 'timestamp))
  )
