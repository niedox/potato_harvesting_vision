;; Auto-generated. Do not edit!


(when (boundp 'gbh_test::Test)
  (if (not (find-package "GBH_TEST"))
    (make-package "GBH_TEST"))
  (shadow 'Test (find-package "GBH_TEST")))
(unless (find-package "GBH_TEST::TEST")
  (make-package "GBH_TEST::TEST"))

(in-package "ROS")
;;//! \htmlinclude Test.msg.html


(defclass gbh_test::Test
  :super ros::object
  :slots (_CameraReady _bool_detection _angle ))

(defmethod gbh_test::Test
  (:init
   (&key
    ((:CameraReady __CameraReady) 0)
    ((:bool_detection __bool_detection) 0)
    ((:angle __angle) 0.0)
    )
   (send-super :init)
   (setq _CameraReady (round __CameraReady))
   (setq _bool_detection (round __bool_detection))
   (setq _angle (float __angle))
   self)
  (:CameraReady
   (&optional __CameraReady)
   (if __CameraReady (setq _CameraReady __CameraReady)) _CameraReady)
  (:bool_detection
   (&optional __bool_detection)
   (if __bool_detection (setq _bool_detection __bool_detection)) _bool_detection)
  (:angle
   (&optional __angle)
   (if __angle (setq _angle __angle)) _angle)
  (:serialization-length
   ()
   (+
    ;; uint32 _CameraReady
    4
    ;; uint32 _bool_detection
    4
    ;; float32 _angle
    4
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; uint32 _CameraReady
       (write-long _CameraReady s)
     ;; uint32 _bool_detection
       (write-long _bool_detection s)
     ;; float32 _angle
       (sys::poke _angle (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; uint32 _CameraReady
     (setq _CameraReady (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;; uint32 _bool_detection
     (setq _bool_detection (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;; float32 _angle
     (setq _angle (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;;
   self)
  )

(setf (get gbh_test::Test :md5sum-) "f641958e6cc2e90ce9803fca42afaf8b")
(setf (get gbh_test::Test :datatype-) "gbh_test/Test")
(setf (get gbh_test::Test :definition-)
      "uint32 CameraReady
uint32 bool_detection

float32 angle


")



(provide :gbh_test/Test "f641958e6cc2e90ce9803fca42afaf8b")


