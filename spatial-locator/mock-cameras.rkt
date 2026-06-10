#lang racket/base

(require racket/math)

(require net/rfc6455
         net/url
         json)

(require "spatial.rkt"
         "camera-config.rkt"
         "config.rkt")

;; Send dummy faceResult data to the socket server Person moves
;; sinusoidally, left to right, with a period of 10 seconds and an
;; amplitude of 2m

(define *pd* 0.064) ; pupillary distance
(define *hw* 0.2)   ; head width
(define *hh* 0.4)   ; head height

(define *eye-z* 1.8)
(define *eye-y* 5.0)
(define *eye-x* (/ (+ (car (camera-pos camera/left))
                      (car (camera-pos camera/right)))
                   2.0))

(define *amplitude* 2.0)
(define *period* 10.0) ; in seconds
(define *nticks* 10) ; number of updates per period


(define *tick* (/ *period* *nticks*)) ; time for which to sleep between updates

(module+ main

  (display (format "Connecting to websocket-server on ~a ... " ws-server-url))
  (define the-server (ws-connect (string->url ws-server-url)))

  (displayln "connected.\n")

  (dynamic-wind ;; Ensure clean disconnection in case of ctrl-C
    void ; no pre-thunk needed
    (λ ()
      (let loop ([tick 0])
        (let ([x (+ *eye-x*
                    (* *amplitude* (sin (/ (* 2 pi tick) *nticks*))))])
          (let ([le-lc (world->camera (list (- x (/ *pd* 2)) *eye-y* *eye-z*) camera/left)]
                [re-lc (world->camera (list (+ x (/ *pd* 2)) *eye-y* *eye-z*) camera/left)]
                [le-rc (world->camera (list (- x (/ *pd* 2)) *eye-y* *eye-z*) camera/right)]
                [re-rc (world->camera (list (+ x (/ *pd* 2)) *eye-y* *eye-z*) camera/right)])
            (display ".")
            (ws-send! the-server
                      (head-location/json x *eye-y* *eye-z*))
            ;; (faces/json le-lc re-lc le-rc re-rc camera/left camera/right)))
            (sleep *tick*)
            (loop (modulo (+ tick 1) *nticks*))))))
    (λ () ;; Close the connection cleanly
      (displayln "Closing down...")
      (ws-close! the-server #:status 1001 #:reason "Client shutting down.")))
      )
        

(define (faces/json le-lc re-lc le-rc re-rc caml camr)
  (jsexpr->string
   (hash 'faceResult
         (hash
          'camera_0 (hash 'left_eye le-lc
                          'right_eye re-lc
                          'bbox (make-bbox le-lc re-lc)
                          'frame_width (camera-wd caml)
                          'frame_height (camera-ht caml)
                          'timestamp_ms (current-milliseconds))
          'camera_1 (hash 'left_eye le-rc
                          'right_eye re-rc
                          'bbox (make-bbox le-rc re-rc)
                          'frame_width (camera-wd camr)
                          'frame_height (camera-ht camr)
                          'timestamp_ms (current-milliseconds))))))

(define (make-bbox le re)
  (let ([xl (car le)]
        [yl (cadr le)]
        [xr (car re)]
        (yr (cadr re)))
    (let ([dx (- xr xl)]
          [yy (/ (+ yl yr) 2.0)])
      (list (- xl (/ dx 2.0))
            (- yy dx)
            (* 2.0 dx)
            (* 3.0 dx)))))

(define (head-location/json x y z)
  (jsexpr->string
   (hash 'headLocation
         (hash 'location (list x y z)
               'timestamp (current-milliseconds)))))
