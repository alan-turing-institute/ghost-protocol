#lang racket/base

(provide ws-server-url)

;; Configuration data

;; Websocket server

;; (define ws-server-url "ws://10.10.100.91:9000/")
(define ws-server-url "ws://localhost:9000/")

;; Camera is connected to 10.10.100.86:9991 and 10.10.100.154:9991
;; Make a socket connection (TCP)
;; Read four bytes, big endian, make 32 bits.
;; Read that many bytes, that's the JPEG.


