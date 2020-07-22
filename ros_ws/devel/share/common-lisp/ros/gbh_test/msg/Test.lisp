; Auto-generated. Do not edit!


(cl:in-package gbh_test-msg)


;//! \htmlinclude Test.msg.html

(cl:defclass <Test> (roslisp-msg-protocol:ros-message)
  ((CameraReady
    :reader CameraReady
    :initarg :CameraReady
    :type cl:integer
    :initform 0)
   (bool_detection
    :reader bool_detection
    :initarg :bool_detection
    :type cl:integer
    :initform 0)
   (angle
    :reader angle
    :initarg :angle
    :type cl:float
    :initform 0.0))
)

(cl:defclass Test (<Test>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <Test>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'Test)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name gbh_test-msg:<Test> is deprecated: use gbh_test-msg:Test instead.")))

(cl:ensure-generic-function 'CameraReady-val :lambda-list '(m))
(cl:defmethod CameraReady-val ((m <Test>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader gbh_test-msg:CameraReady-val is deprecated.  Use gbh_test-msg:CameraReady instead.")
  (CameraReady m))

(cl:ensure-generic-function 'bool_detection-val :lambda-list '(m))
(cl:defmethod bool_detection-val ((m <Test>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader gbh_test-msg:bool_detection-val is deprecated.  Use gbh_test-msg:bool_detection instead.")
  (bool_detection m))

(cl:ensure-generic-function 'angle-val :lambda-list '(m))
(cl:defmethod angle-val ((m <Test>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader gbh_test-msg:angle-val is deprecated.  Use gbh_test-msg:angle instead.")
  (angle m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <Test>) ostream)
  "Serializes a message object of type '<Test>"
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'CameraReady)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 8) (cl:slot-value msg 'CameraReady)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 16) (cl:slot-value msg 'CameraReady)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 24) (cl:slot-value msg 'CameraReady)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'bool_detection)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 8) (cl:slot-value msg 'bool_detection)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 16) (cl:slot-value msg 'bool_detection)) ostream)
  (cl:write-byte (cl:ldb (cl:byte 8 24) (cl:slot-value msg 'bool_detection)) ostream)
  (cl:let ((bits (roslisp-utils:encode-single-float-bits (cl:slot-value msg 'angle))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <Test>) istream)
  "Deserializes a message object of type '<Test>"
    (cl:setf (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'CameraReady)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 8) (cl:slot-value msg 'CameraReady)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 16) (cl:slot-value msg 'CameraReady)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 24) (cl:slot-value msg 'CameraReady)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'bool_detection)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 8) (cl:slot-value msg 'bool_detection)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 16) (cl:slot-value msg 'bool_detection)) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 24) (cl:slot-value msg 'bool_detection)) (cl:read-byte istream))
    (cl:let ((bits 0))
      (cl:setf (cl:ldb (cl:byte 8 0) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) bits) (cl:read-byte istream))
    (cl:setf (cl:slot-value msg 'angle) (roslisp-utils:decode-single-float-bits bits)))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<Test>)))
  "Returns string type for a message object of type '<Test>"
  "gbh_test/Test")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'Test)))
  "Returns string type for a message object of type 'Test"
  "gbh_test/Test")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<Test>)))
  "Returns md5sum for a message object of type '<Test>"
  "f641958e6cc2e90ce9803fca42afaf8b")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'Test)))
  "Returns md5sum for a message object of type 'Test"
  "f641958e6cc2e90ce9803fca42afaf8b")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<Test>)))
  "Returns full string definition for message of type '<Test>"
  (cl:format cl:nil "uint32 CameraReady~%uint32 bool_detection~%~%float32 angle~%~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'Test)))
  "Returns full string definition for message of type 'Test"
  (cl:format cl:nil "uint32 CameraReady~%uint32 bool_detection~%~%float32 angle~%~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <Test>))
  (cl:+ 0
     4
     4
     4
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <Test>))
  "Converts a ROS message object to a list"
  (cl:list 'Test
    (cl:cons ':CameraReady (CameraReady msg))
    (cl:cons ':bool_detection (bool_detection msg))
    (cl:cons ':angle (angle msg))
))
