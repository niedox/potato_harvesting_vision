// Auto-generated. Do not edit!

// (in-package gbh_test.msg)


"use strict";

const _serializer = _ros_msg_utils.Serialize;
const _arraySerializer = _serializer.Array;
const _deserializer = _ros_msg_utils.Deserialize;
const _arrayDeserializer = _deserializer.Array;
const _finder = _ros_msg_utils.Find;
const _getByteLength = _ros_msg_utils.getByteLength;

//-----------------------------------------------------------

class test {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.CameraReady = null;
      this.bool_detection = null;
      this.angle = null;
    }
    else {
      if (initObj.hasOwnProperty('CameraReady')) {
        this.CameraReady = initObj.CameraReady
      }
      else {
        this.CameraReady = 0;
      }
      if (initObj.hasOwnProperty('bool_detection')) {
        this.bool_detection = initObj.bool_detection
      }
      else {
        this.bool_detection = 0;
      }
      if (initObj.hasOwnProperty('angle')) {
        this.angle = initObj.angle
      }
      else {
        this.angle = 0.0;
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type test
    // Serialize message field [CameraReady]
    bufferOffset = _serializer.uint32(obj.CameraReady, buffer, bufferOffset);
    // Serialize message field [bool_detection]
    bufferOffset = _serializer.uint32(obj.bool_detection, buffer, bufferOffset);
    // Serialize message field [angle]
    bufferOffset = _serializer.float32(obj.angle, buffer, bufferOffset);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type test
    let len;
    let data = new test(null);
    // Deserialize message field [CameraReady]
    data.CameraReady = _deserializer.uint32(buffer, bufferOffset);
    // Deserialize message field [bool_detection]
    data.bool_detection = _deserializer.uint32(buffer, bufferOffset);
    // Deserialize message field [angle]
    data.angle = _deserializer.float32(buffer, bufferOffset);
    return data;
  }

  static getMessageSize(object) {
    return 12;
  }

  static datatype() {
    // Returns string type for a message object
    return 'gbh_test/test';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return 'f641958e6cc2e90ce9803fca42afaf8b';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    uint32 CameraReady
    uint32 bool_detection
    
    float32 angle
    
    
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new test(null);
    if (msg.CameraReady !== undefined) {
      resolved.CameraReady = msg.CameraReady;
    }
    else {
      resolved.CameraReady = 0
    }

    if (msg.bool_detection !== undefined) {
      resolved.bool_detection = msg.bool_detection;
    }
    else {
      resolved.bool_detection = 0
    }

    if (msg.angle !== undefined) {
      resolved.angle = msg.angle;
    }
    else {
      resolved.angle = 0.0
    }

    return resolved;
    }
};

module.exports = test;
