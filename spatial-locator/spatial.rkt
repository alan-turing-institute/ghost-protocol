#lang racket/base
(require racket/math)
(require math/matrix)

(provide (struct-out camera)
         make-camera
         camera/xy->uv
         camera/uv->xy
         
         ;; Conversion from camera frame to world frame
         world->camera
         camera->world
         ray-intersect
         
         ;; Utilities for rotations
         euler->rotation-matrix
         rotation-matrix->euler
         rotation-matrix->unit-vectors
         unit-vectors->rotation-matrix

         ;; Utilities for 3d
         vec+ vec- :x :y :z x+ y+ z+
         dot smul ex ey ez)

;; 3d utilities

;; All points are (x y z) triples

(define :x car)
(define :y cadr)
(define :z caddr)

(define :u car)
(define :v cadr)

;; All these work for 2d and 3d vectors

(define (vec+ . ps)
  (apply map + ps))

(define (vec- p1 p2)
  (map - p1 p2))

(define (smul a p)
  (map (λ (c) (* a c)) p))

(define (dot v1 v2)
  (apply + (map * v1 v2)))

(define ex '(1 0 0))
(define ey '(0 1 0))
(define ez '(0 0 1))

;; These only work for 3d

(define (x+ p dx)
  (vec+ p (list dx 0 0)))

(define (y+ p dy)
  (vec+ p (list 0 dy 0)))

(define (z+ p dz)
  (vec+ p (list 0 0 dz)))


;; Functions for conversion betwen camera image locations and three-dimensional locations

;; ----------------------------------------------------------------------

;; The position (x, y, z), Unit directions (u, n, v) and focal length, f.
;; The order u, n, v means that this triple is right-handed
;;
(struct camera (pos u n v f wd ht) #:transparent)

;; make-camera : loc orient f
;; - location, (x y z)
;; - Euler angles, (α β γ)
;; - focal length, f
(define (make-camera loc orient f wd ht)
  (let* ([R (euler->rotation-matrix (car orient) (cadr orient) (caddr orient))]
         [units (rotation-matrix->unit-vectors R)])
    (camera loc
            (car units) (cadr units) (caddr units)
            f
            wd
            ht)))

;; Convert from image-centred to top-left origin
(define (camera/uv->xy uv cam)
  (list (+ (/ (camera-wd cam) 2.0) (car uv))
        (- (/ (camera-ht cam) 2.0) (cadr uv))))

;; Convert from top-left origin to image-centred
(define (camera/xy->uv xy cam)
  (list (- (car xy) (/ (camera-wd cam) 2.0))
        (- (/ (camera-ht cam) 2.0) (cadr xy))))

;; For a given location in space (x, y, z) produce a pair (x y) of the images location on the camera
(define (world->camera p cam)
  (let* ([xvec (vec- p (camera-pos cam))]
         [scale (/ (camera-f cam)
                   (dot (camera-n cam) xvec))]
         [u (* scale (dot xvec (camera-u cam)))]
         [v (* scale (dot xvec (camera-v cam)))])
    ;; Convert to "camera image coordinates", which have origin at the top-left, y-coordinate downwards
    (camera/uv->xy (list u v) cam)))

;; Convert a location on the image to a ray in space A ray is a pair of two vectors, (p r) where p is
;; a point on the ray and r is a (not necessarily unit) direction
(define (camera->world xy cam)
  (define uv (camera/xy->uv xy cam))
  (list
   (camera-pos cam)
   (vec+ (camera-n cam)
         (smul (/ (:u uv) (camera-f cam))
               (camera-u cam))
         (smul (/ (:v uv) (camera-f cam))
               (camera-v cam)))))


;; Find the best intersection point of two rays: the point midway on
;; the line of closest approach
(define (ray-intersect ray1 ray2)
  (let ([p1 (car ray1)]
        [r1 (cadr ray1)]
        [p2 (car ray2)]
        [r2 (cadr ray2)])
    (let ([r (vec- p1 p2)])
      (let ([a (dot r1 r1)]
            [b (dot r1 r2)]
            [c (dot r2 r2)]
            [d (dot r1 r)]
            [e (dot r2 r)])
        (let ([f (- (* a c) (* b b))]) ; This is (r1 x r2)^2, and is < 0.01 if the rays are less than 10 degrees apart
          (and (> f 0.01)
               (let ([t (/ (- (* b e) (* c d))
                           f)]
                     [s (/ (- (* a e) (* b d))
                           f)])
                 (smul 0.5
                       (vec+ p1 (smul t r1) p2 (smul s r2))))))))))


;; ----------------------------------------------------------------------
;; Rotational utilities

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
(define (rotation-matrix->unit-vectors R)
  (map matrix->list (matrix-cols R)))

;; In the order u,n, v
;; The unit vectors are the columns of the rotation matrix
(define (unit-vectors->rotation-matrix vs)
  (matrix-augment (map ->col-matrix vs)))

;; 



