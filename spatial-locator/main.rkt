#lang racket/base

(require racket/gui/base
         racket/class)

(require (only-in racket/format ~r))

(require net/rfc6455
         net/url
         json)

(require
 "spatial.rkt"
 "camera-config.rkt" ; for camera/left and camera/right
 "config.rkt"        ; for ws-server-url
 )


;; -------------------------------------------------------------------------------
;; Representation of a head location, as returned from the socket server

;; left-eye, right-eye: (x y) locations in image-coordinates (origin is top-left)
;; bbox   : (x y w h)
;; wd, ht : width and height of the image
;; t      : a timestamp
(struct head (left-eye right-eye bbox wd ht t) #:transparent)

;; -------------------------------------------------------------------------------
;; Global state

;; (state number? number? head? head?)
(struct state (last-timestamp δt lft rgt) #:mutable #:transparent)

;; A global, mutable variable with the current head locations
;; Used for updating the canvas
(define *global-state*
  (state (current-milliseconds) 0.1
         (head '(0 0) '(0 0) '(0 0 0 0) 4000 3000 0)
         (head '(0 0) '(0 0) '(0 0 0 0) 4000 3000 0)))

(module+ main

  ;; Initialise connection to websocket server
  ;; -----------------------------------------

  (display (format "Connecting to websocket-server on ~a ... " ws-server-url))
  (define the-server (ws-connect (string->url ws-server-url)))

  (displayln "connected.\n")

  ;; Initialise canvas for left camera
  ;; ---------------------------------

  (define *frame*
    (new frame%
         [label "Left camera"]
         [width 600]
         [height 400]))
  
  (define *canvas*
    (new canvas%
         [parent *frame*]
         [paint-callback
          (λ (cv dc)
            (draw-the-view dc *global-state*))]))

  (send *frame* show #t)

  (define *es* (current-eventspace))
  
  ;; The main loop
  ;; -------------

  ;; The main loop runs in a separate thread to avoid blocking
  
  ;; Repeatedly:
  ;; - waits for a message from the websocket server
  ;; - drops the message unless it is camera data
  ;; - converts the camera data to a three-dimensional location
  ;; - rebroadcasts the three-dimensional location

  (thread
   (λ ()
     (dynamic-wind ;; Ensure clean disconnection in case of ctrl-C
       void ; no pre-thunk needed
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
                 [(hash-has-key? msg 'faceResult)
                  (queue-callback
                   (λ ()
                     (define-values (lft rgt)
                       (parse-message (hash-ref msg 'faceResult)))

                     ;; Update moving-average time between frames
                     (define new-ts (head-t lft))
                     (define new-δt (+ (* 0.25 (- new-ts (state-last-timestamp *global-state*)))
                                       (* 0.75 (state-δt *global-state*))))

                     ;; Update global state
                     (set-state-last-timestamp! *global-state* new-ts)
                     (set-state-δt! *global-state* new-δt)
                     (set-state-lft! *global-state* lft)
                     (set-state-rgt! *global-state* rgt)
                     
                     ; (displayln (format "left : ~a\nright: ~a\n" lft rgt))
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
  

;; ----------------------------------------------------------------------
;; Canvas drawing


(define (draw-the-view dc st)
  (send dc set-scale 1.0 1.0)
  (send dc set-text-foreground "blue")
  (send dc draw-text (format "fps: ~a" (~r (/ 1000 (state-δt *global-state*)) #:precision 2)) 0 0)

  (define-values (wd _) (send dc get-size))
  
  ;; Left head
  (send dc set-pen "red" 2 'solid)
  (send dc set-brush "red" 'solid)
   (draw-face dc (state-lft *global-state*) wd)

  ;; Right head
  (send dc set-pen "green" 2 'solid)
  (send dc set-brush "green" 'solid)
  (draw-face dc (state-rgt *global-state*) wd)

  )

(define (draw-face dc face wd)
  (let ([left-eye  (head-left-eye face)]
        [right-eye (head-right-eye face)]
        [bbox      (head-bbox face)]
        [scale (/ wd (head-wd face))])
    (send dc set-scale scale scale)
    (send dc draw-ellipse (car left-eye) (cadr left-eye) 16 16)
    (send dc draw-ellipse (car right-eye) (cadr right-eye) 16 16)
    (send dc set-brush (new brush% [style 'transparent]))
    (send dc draw-rectangle (car bbox) (cadr bbox) (caddr bbox) (cadddr bbox))))
    




;; ----------------------------------------------------------------------
;; Socket server reading and writing utilities

;; Reading camera space heads
;; --------------------------

;; jsexpr? -> head?
;; JSON should be of the form:
;; 

;; Parse a valid jsexpre? into a left head and right head
;; -> [values head? head?]
(define (parse-message msg)
  (let ([lft (hash-ref msg 'camera_0 #f)]
        [rgt (hash-ref msg 'camera_1 #f)])
    (values
     (and (not (eq? lft 'null))
          (get-head-location lft))
     (and (not (eq? rgt 'null))
          (get-head-location rgt)))))

(define (get-head-location js)
  (head (hash-ref js 'left_eye)
        (hash-ref js 'right_eye)
        (hash-ref js 'bbox)
        (hash-ref js 'frame_width)
        (hash-ref js 'frame_height)
        (hash-ref js 'timestamp_ms)))


;; Sending world-space position
;; ----------------------------

;; Standard message format:
;; 
(define (make-json-payload pos t)
  (jsexpr->string
   (hash 'headLocation
         (hash 'location
               pos
               'timestamp
               t))))

(define (broadcast-position! pos t server)
  (ws-send! server
            (make-json-payload pos t))
  

  )
