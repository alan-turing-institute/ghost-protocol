#lang racket/base

(require net/rfc6455
         net/url
         json)

(require (only-in "config.rkt"
                  ws-server-url))

(module+ main

  (display (format "Connecting to websocket-server on ~a ... " ws-server-url))
  (define the-server (ws-connect (string->url ws-server-url)))

  (displayln "connected.\n")

  ;; For testing: Send a single position message
  (broadcast-position '(2.0 5.0 1.65) (current-milliseconds) the-server)
  
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
          (let ([msg (sync (ws-recv-evt the-server))])
            (displayln msg)
            (loop)))))
    (λ () ;; Close the connection cleanly
      (displayln "Closing down...")
      (ws-close! the-server #:status 1001 #:reason "Client shutting down.")
      (exit))
    )

  (unless (ws-conn-closed? the-server) (ws-close! the-server))
  
  )
  
;; (unless (ws-conn-closed? the-server)
;;   (ws-close! the-server)))

(define (read-any-message msg)
  (let ([js (with-handlers ([exn:fail:read (λ (_) #f)])
              (string->jsexpr msg))])
    msg))

;; Returns either
;; #f if this message isn't for us or isn't readable; or
;; jsexpr?
;;
;; msg should be jsexpr? of the following format:
;; 
(define (read-message msg)
  (let ([js (with-handlers ([exn:fail:read (λ (_) #f)])
              (string->jsexpr msg))])
    (and msg
         (hash? msg)
         (hash-has-key? 'faceResult)
         (hash-ref msg 'faceResult))))

;; Standard message format:
;; 
(define (make-json-payload pos t)
  (jsexpr->string
   (hash 'headLocation
         (hash 'location
               pos
               'timestamp
               t))))

(define (broadcast-position pos t server)
  (ws-send! server
            (make-json-payload pos t))
  

  )
