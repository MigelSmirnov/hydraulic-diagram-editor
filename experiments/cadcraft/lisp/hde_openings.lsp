;;; hde_openings.lsp — doors and windows that belong to walls (CADCraft AutoLISP).
;;;
;;; An opening is a block reference whose name matches *hde-opening-blocks*. It belongs to a
;;; wall face (LINE or LWPOLYLINE on a layer matching *hde-wall-layers*) when its insertion
;;; point lies on the face and its rotation is parallel to that face segment. CADCraft's LISP
;;; has no attribute or xdata access, so this geometric incidence is the link: the commands
;;; below keep it intact instead of storing it.
;;;
;;; Block convention (experiments/cadcraft/capabilities/INDEX.md): local X along the wall,
;;; local +Y across it from the base face to the other face, base at a corner on the base face.
;;;
;;; Commands:   HDE-OPENING     place an opening on a wall face
;;;             HDE-WALLMOVE    move wall faces together with their openings
;;;             HDE-WALLROTATE  rotate wall faces together with their openings
;;;             HDE-CHECK       select and list openings that sit on no wall face
;;; Functions (for agents, via the MCP `lisp` tool): hde-place, hde-wall-move,
;;; hde-wall-rotate, hde-orphans.

(setq *hde-wall-layers* "WALL*,EXTERIOR*,PARTITION*,P0*_JUNCTION*")
(setq *hde-opening-blocks* "DOOR_*,WIN_*")
(setq *hde-tol* 0.5)          ; mm: how far a base point may be from its face
(setq *hde-ang-tol* 1e-4)     ; rad
(setq *hde-pi* (* 4.0 (atan 1.0)))

;;; ---------- geometry ----------

(defun hde-xy (p) (list (float (car p)) (float (cadr p))))

(defun hde-sub (a b) (list (- (car a) (car b)) (- (cadr a) (cadr b))))

(defun hde-cross (u v) (- (* (car u) (cadr v)) (* (cadr u) (car v))))

(defun hde-dot (u v) (+ (* (car u) (car v)) (* (cadr u) (cadr v))))

;; (distance projection) from point p to segment a-b.
(defun hde-seg-near (p a b / ab len2 tt q)
  (setq ab (hde-sub b a)
        len2 (hde-dot ab ab))
  (if (< len2 1e-12)
    (list (distance p a) a)
    (progn
      (setq tt (/ (hde-dot (hde-sub p a) ab) len2))
      (setq tt (max 0.0 (min 1.0 tt)))
      (setq q (list (+ (car a) (* tt (car ab))) (+ (cadr a) (* tt (cadr ab)))))
      (list (distance p q) q))))

;; Segments of a wall face as ((a b) ...); nil for other objects.
(defun hde-segments (en / ed typ pts segs)
  (setq ed (entget en)
        typ (cdr (assoc 0 ed)))
  (cond
    ((= typ "LINE")
     (list (list (hde-xy (cdr (assoc 10 ed))) (hde-xy (cdr (assoc 11 ed))))))
    ((= typ "LWPOLYLINE")
     (foreach g ed
       (if (= (car g) 10) (setq pts (cons (hde-xy (cdr g)) pts))))
     (setq pts (reverse pts))
     (if (= 1 (logand 1 (cdr (assoc 70 ed))))
       (setq pts (append pts (list (car pts)))))
     (while (cadr pts)
       (setq segs (cons (list (car pts) (cadr pts)) segs)
             pts (cdr pts)))
     (reverse segs))))

;; Nearest segment of face en to p: (distance projection a b), or nil.
(defun hde-face-near (en p / best r)
  (foreach s (hde-segments en)
    (setq r (hde-seg-near p (car s) (cadr s)))
    (if (or (null best) (< (car r) (car best)))
      (setq best (list (car r) (cadr r) (car s) (cadr s)))))
  best)

(defun hde-wall-p (en / ed)
  (setq ed (entget en))
  (and (member (cdr (assoc 0 ed)) '("LINE" "LWPOLYLINE"))
       (wcmatch (strcase (cdr (assoc 8 ed))) (strcase *hde-wall-layers*))))

(defun hde-opening-p (en / ed)
  (setq ed (entget en))
  (and (= (cdr (assoc 0 ed)) "INSERT")
       (wcmatch (strcase (cdr (assoc 2 ed))) (strcase *hde-opening-blocks*))))

(defun hde-ss->list (ss / i out)
  (setq i 0)
  (if ss
    (while (< i (sslength ss))
      (setq out (cons (ssname ss i) out)
            i (1+ i))))
  (reverse out))

(defun hde-all-walls ()
  (vl-remove-if-not 'hde-wall-p (hde-ss->list (ssget "X" (list (cons 0 "LINE,LWPOLYLINE"))))))

(defun hde-all-openings ()
  (vl-remove-if-not 'hde-opening-p (hde-ss->list (ssget "X" (list (cons 0 "INSERT"))))))

;; The wall face nearest to p among all wall faces: (en distance projection a b), or nil.
(defun hde-face-at (p / best r)
  (foreach en (hde-all-walls)
    (setq r (hde-face-near en p))
    (if (and r (or (null best) (< (car r) (cadr best))))
      (setq best (cons en r))))
  best)

;; Same direction modulo pi.
(defun hde-parallel-p (a1 a2 / d)
  (setq d (rem (abs (- a1 a2)) *hde-pi*))
  (or (< d *hde-ang-tol*) (> d (- *hde-pi* *hde-ang-tol*))))

;; Does opening op sit on one of the faces?
(defun hde-on-faces-p (op faces / ed p rot hit r)
  (setq ed (entget op)
        p (hde-xy (cdr (assoc 10 ed)))
        rot (cdr (assoc 50 ed)))
  (foreach f faces
    (foreach s (hde-segments f)
      (setq r (hde-seg-near p (car s) (cadr s)))
      (if (and (< (car r) *hde-tol*) (hde-parallel-p rot (angle (car s) (cadr s))))
        (setq hit T))))
  hit)

(defun hde-openings-on (faces)
  (vl-remove-if-not '(lambda (op) (hde-on-faces-p op faces)) (hde-all-openings)))

(defun hde-list->ss (ens / ss)
  (setq ss (ssadd))
  (foreach e ens (ssadd e ss))
  ss)

;;; ---------- functions for agents ----------

;; Place block blk with its base on the wall face nearest to p (projected onto it) and local +Y
;; toward side. Returns the new insert, or nil when no wall face is within reach.
(defun hde-place (blk p side / hit q a b ang attreq)
  (setq p (hde-xy p)
        hit (hde-face-at p))
  (if (null hit)
    (progn (princ "\nHDE: no wall face found.") nil)
    (progn
      (setq q (nth 2 hit) a (nth 3 hit) b (nth 4 hit)
            ang (angle a b))
      ;; Local +Y is the left normal of local X: flip when side is on the right of a->b.
      (if (< (hde-cross (hde-sub b a) (hde-sub (hde-xy side) q)) 0.0)
        (setq ang (+ ang *hde-pi*)))
      (setq ang (rem ang (* 2.0 *hde-pi*)))
      (setq attreq (getvar "ATTREQ"))
      (if attreq (setvar "ATTREQ" 0))
      (command "-insert" blk q 1 1 (* ang (/ 180.0 *hde-pi*)))
      (if attreq (setvar "ATTREQ" attreq))
      (entlast))))

;; Move the wall faces in ens and the openings sitting on them by from->to.
;; Returns the number of openings carried.
(defun hde-wall-move (ens from to / ops)
  (setq ops (hde-openings-on ens))
  (command "move" (hde-list->ss (append ens ops)) "" from to)
  (length ops))

;; Rotate the wall faces in ens and their openings about base by deg degrees.
(defun hde-wall-rotate (ens base deg / ops)
  (setq ops (hde-openings-on ens))
  (command "rotate" (hde-list->ss (append ens ops)) "" base deg)
  (length ops))

;; Openings that sit on no wall face, as a list of handles.
(defun hde-orphans (/ walls out)
  (setq walls (hde-all-walls))
  (foreach op (hde-all-openings)
    (if (not (hde-on-faces-p op walls))
      (setq out (cons (cdr (assoc 5 (entget op))) out))))
  (reverse out))

;;; ---------- commands ----------

(setq *hde-block* "WIN_900_W200_OPAQUE")

(defun c:HDE-OPENING (/ blk p side)
  (setq blk (getstring (strcat "\nOpening block <" *hde-block* ">: ")))
  (if (and blk (/= blk "")) (setq *hde-block* blk))
  (if (not (tblsearch "BLOCK" *hde-block*))
    (princ (strcat "\nHDE: block " *hde-block* " is not defined; insert it from the library first."))
    (if (and (setq p (getpoint "\nStart of the opening on a wall face: "))
             (setq side (getpoint p "\nPoint on the wall side (local +Y): ")))
      (hde-place *hde-block* p side)))
  (princ))

(defun hde-select-walls (/ ss)
  (princ "\nSelect wall faces: ")
  (setq ss (ssget))
  (vl-remove-if-not 'hde-wall-p (hde-ss->list ss)))

(defun c:HDE-WALLMOVE (/ ens from to n)
  (if (and (setq ens (hde-select-walls))
           (setq from (getpoint "\nBase point: "))
           (setq to (getpoint from "\nSecond point: ")))
    (progn
      (setq n (hde-wall-move ens from to))
      (princ (strcat "\nHDE: moved " (itoa (length ens)) " wall face(s) with " (itoa n) " opening(s).")))
    (princ "\nHDE: nothing moved."))
  (princ))

(defun c:HDE-WALLROTATE (/ ens base deg n)
  (if (and (setq ens (hde-select-walls))
           (setq base (getpoint "\nBase point: "))
           (setq deg (getreal "\nRotation angle (degrees): ")))
    (progn
      (setq n (hde-wall-rotate ens base deg))
      (princ (strcat "\nHDE: rotated " (itoa (length ens)) " wall face(s) with " (itoa n) " opening(s).")))
    (princ "\nHDE: nothing rotated."))
  (princ))

(defun c:HDE-CHECK (/ orphans ss)
  (setq orphans (hde-orphans))
  (if orphans
    (progn
      (setq ss (ssadd))
      (foreach h orphans (ssadd (handent h) ss))
      (sssetfirst nil ss)
      (princ (strcat "\nHDE: " (itoa (length orphans)) " opening(s) on no wall face (selected): "))
      (foreach h orphans (princ (strcat h " "))))
    (princ "\nHDE: every opening sits on a wall face."))
  (princ))

(princ "\nHDE openings loaded: HDE-OPENING, HDE-WALLMOVE, HDE-WALLROTATE, HDE-CHECK.")
(princ)
