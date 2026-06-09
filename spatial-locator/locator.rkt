#lang racket/base
(require racket/math)
(require math/matrix)

;; Locate a position in 3-space given its location on each of two
;; camera images, plus camera calibration data

;; The position (x, y, z), Euler angles (α, β, γ), and focal length, f
(struct camera (x y z α β γ f) #:transparent)

;; Compute the 3x3 rotation matrix from Euler angles
;; -> Array?
(define (euler->rotation-matrix α β γ)
  (let ([cα (cos α)]
        [sα (sin α)]
        [cβ (cos β)]
        [sβ (sin β)]
        [cγ (cos γ)]
        [sγ (sin γ)])
    (matrix [[(- (* cα cγ) (* sα sβ sγ)) (- (* sα cβ)) (+ (* cα sγ) (* sα sβ cγ))]
             [(+ (* sα cγ) (* cα sβ sγ)) (* cα cβ)     (- (* sα sγ) (* cα sβ cγ))]
             [(- (* cβ sγ)) sβ (* cβ cγ)]])))

(define (atan2 y x)
  (cond
    [(> x 0) (atan (/ y x))]
    [(< x 0) (if (>= y 0)
                 (+ (atan (/ y x)) pi)
                 (- (atan (/ y x)) pi))]
    [else
     (cond
       [(> y 0) (/ pi 2)]
       [(< y 0) (- (/ pi 2))]
       [else +nan.0])]))

(define (rotation-matrix->euler R)
  (let ([β (asin (matrix-ref R 2 1))]
        [α (atan2 (- (matrix-ref R 0 1)) (matrix-ref R 1 1))]
        [γ (atan2 (- (matrix-ref R 2 0)) (matrix-ref R 2 2))])
    (list α β γ)))

;; What we are calling u, n, and v 
(define (rotation-matrix->units R)
  (matrix-cols R))



;; TODO: Lead both cameras from `cameras.scm`


