;; Auto-generated. Do not edit!


(when (boundp 'vision_rs::Vision)
  (if (not (find-package "VISION_RS"))
    (make-package "VISION_RS"))
  (shadow 'Vision (find-package "VISION_RS")))
(unless (find-package "VISION_RS::VISION")
  (make-package "VISION_RS::VISION"))

(in-package "ROS")
;;//! \htmlinclude Vision.msg.html


(defclass vision_rs::Vision
  :super ros::object
  :slots (_bool_detection _bool_depth _x _y _z _height _width _angle ))

(defmethod vision_rs::Vision
  (:init
   (&key
    ((:bool_detection __bool_detection) 0)
    ((:bool_depth __bool_depth) 0)
    ((:x __x) 0.0)
    ((:y __y) 0.0)
    ((:z __z) 0.0)
    ((:height __height) 0.0)
    ((:width __width) 0.0)
    ((:angle __angle) 0.0)
    )
   (send-super :init)
   (setq _bool_detection (round __bool_detection))
   (setq _bool_depth (round __bool_depth))
   (setq _x (float __x))
   (setq _y (float __y))
   (setq _z (float __z))
   (setq _height (float __height))
   (setq _width (float __width))
   (setq _angle (float __angle))
   self)
  (:bool_detection
   (&optional __bool_detection)
   (if __bool_detection (setq _bool_detection __bool_detection)) _bool_detection)
  (:bool_depth
   (&optional __bool_depth)
   (if __bool_depth (setq _bool_depth __bool_depth)) _bool_depth)
  (:x
   (&optional __x)
   (if __x (setq _x __x)) _x)
  (:y
   (&optional __y)
   (if __y (setq _y __y)) _y)
  (:z
   (&optional __z)
   (if __z (setq _z __z)) _z)
  (:height
   (&optional __height)
   (if __height (setq _height __height)) _height)
  (:width
   (&optional __width)
   (if __width (setq _width __width)) _width)
  (:angle
   (&optional __angle)
   (if __angle (setq _angle __angle)) _angle)
  (:serialization-length
   ()
   (+
    ;; uint32 _bool_detection
    4
    ;; uint32 _bool_depth
    4
    ;; float32 _x
    4
    ;; float32 _y
    4
    ;; float32 _z
    4
    ;; float32 _height
    4
    ;; float32 _width
    4
    ;; float32 _angle
    4
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; uint32 _bool_detection
       (write-long _bool_detection s)
     ;; uint32 _bool_depth
       (write-long _bool_depth s)
     ;; float32 _x
       (sys::poke _x (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;; float32 _y
       (sys::poke _y (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;; float32 _z
       (sys::poke _z (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;; float32 _height
       (sys::poke _height (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;; float32 _width
       (sys::poke _width (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;; float32 _angle
       (sys::poke _angle (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; uint32 _bool_detection
     (setq _bool_detection (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;; uint32 _bool_depth
     (setq _bool_depth (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;; float32 _x
     (setq _x (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;; float32 _y
     (setq _y (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;; float32 _z
     (setq _z (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;; float32 _height
     (setq _height (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;; float32 _width
     (setq _width (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;; float32 _angle
     (setq _angle (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;;
   self)
  )

(setf (get vision_rs::Vision :md5sum-) "3530597fb0acf79ac5d9f35a155d9e4a")
(setf (get vision_rs::Vision :datatype-) "vision_rs/Vision")
(setf (get vision_rs::Vision :definition-)
      "uint32 bool_detection
uint32 bool_depth

float32 x
float32 y
float32 z

float32 height
float32 width

float32 angle

")



(provide :vision_rs/Vision "3530597fb0acf79ac5d9f35a155d9e4a")


