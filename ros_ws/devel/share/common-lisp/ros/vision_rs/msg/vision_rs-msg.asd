
(cl:in-package :asdf)

(defsystem "vision_rs-msg"
  :depends-on (:roslisp-msg-protocol :roslisp-utils )
  :components ((:file "_package")
    (:file "Vision" :depends-on ("_package_Vision"))
    (:file "_package_Vision" :depends-on ("_package"))
  ))