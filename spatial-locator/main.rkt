#lang racket/base

(require racket/gui/base
         racket/class)

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
;; bbox   : (x1 y1 x2 y2)
;; wd, ht : width and height of the image
;; t      : a timestamp
(struct head (left-eye right-eye bbox wd ht t) #:transparent)

;; A global, mutable variable with the current head locations
(define *the-left-head*  (head '(0 0) '(0 0) '(0 0 0 0) 4000 3000 0))
(define *the-right-head* (head '(0 0) '(0 0) '(0 0 0 0) 4000 3000 0))


(module+ main

  (display (format "Connecting to websocket-server on ~a ... " ws-server-url))
  (define the-server (ws-connect (string->url ws-server-url)))

  (displayln "connected.\n")

  ;; For testing: Send a single position message
 ;  (broadcast-position! '(2.0 5.0 1.65) (current-milliseconds) the-server)
  
  ;; The main loop
  ;; Repeatedly:
  ;; - waits for a message from the websocket server
  ;; - drops the message unless it is camera data
  ;; - converts the camera data to a three-dimensional location
  ;; - rebroadcasts the three-dimensional location

  (dynamic-wind ;; Ensure clean disconnection in case of ctrl-C
    void ; no pre-thunk needed
    (λ ()
      (let loop ()
        (unless (ws-conn-closed? the-server)
          (let* ([msg      (sync (ws-recv-evt the-server))]
                 [msg/js   (and msg (parse-message msg 'faceResult))]
                 [left/js  (and msg/js (hash-ref msg/js 'camera_0 #f))]
                 [right/js (and msg/js (hash-ref msg/js 'camera_1 #f))]
                 [head/lft (and left/js
                                (not (eq? left/js 'null))
                                (get-head-location left/js))]
                 [head/rgt (and right/js
                                (not (eq? right/js 'null))
                                (get-head-location right/js))])
            ;; (displayln (format "msg: ~a" msg))
            ;; (displayln (format  "msg/js: ~a" msg/js))
            ;; (displayln (format "left/js: ~a" left/js))
            (displayln (format "left : ~a\nright: ~a\n" head/lft head/rgt))
            (loop)))))
    (λ () ;; Close the connection cleanly
      (displayln "Closing down...")
      (ws-close! the-server #:status 1001 #:reason "Client shutting down.")
      ; (exit)
      )
    )

  (unless (ws-conn-closed? the-server) (ws-close! the-server))
  
  )


;; ----------------------------------------------------------------------
;; Socket server reading and writing utilities

;; jsexpr? -> head?
;; JSON should be of the form:
;; 
(define (get-head-location js)
  (head (hash-ref js 'left_eye)
        (hash-ref js 'right_eye)
        (hash-ref js 'bbox)
        (hash-ref js 'frame_width)
        (hash-ref js 'frame_height)
        (hash-ref js 'timestamp_ms)))


;; Convert a string to jsexpr? or return #f
(define (parse-any-message msg)
  (let ([js (with-handlers ([exn:fail:read (λ (_) #f)])
              (string->jsexpr msg))])
    js))

;; Convert a string to jsexpr?, assume it is a hash, and extract the
;; value corresponding to the key required-message-type. Return #f if
;; any of these steps fail.
(define (parse-message msg required-message-type)
  (let ([msg/json (parse-any-message msg)])
    (and msg/json
         (hash? msg/json)
         (hash-ref msg/json required-message-type #f))))

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
