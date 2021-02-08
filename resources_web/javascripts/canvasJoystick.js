const canvasJoystick = document.getElementById("cnvsJoy");
const ctxJoy = canvasJoystick.getContext("2d");
const rectJoy = canvasJoystick.getBoundingClientRect();

let color_fill_style = 'orange'
let controllers = {};
let debug = false;
let draw_interval = '';
let fps = 20              // we use requestAnimationFrame in updateStatus
let mdown = false;
let mOut = false;
let mUp_globally = true;


// --- canvas and gamepad init
let haveEvents = 'GamepadEvent' in window;
let factor_x = rangeToFactor(rectJoy.width);
let factor_y = rangeToFactor(rectJoy.height);
let posJoy = setCenter(rectJoy);
setVelStart();

// -- ps3 object for gamepad handling
let ps3_controller_connected = false;
let ps3_factor_x = rangeToFactor(1) / 2;
let ps3_factor_y = rangeToFactor(1) / 2;
let ps3_axis_id_x = 3;
let ps3_axis_id_y = 4;
let ps3_axis_pos_x = 0;
let ps3_axis_pos_y = 0;

if (debug){
  console.log('Start canvas Joystick')
}

// -------------- Start -------------------------------------
ctxJoy.lineWidth = 1;

canvasJoystick.addEventListener("mousedown", inputStart, false);
canvasJoystick.addEventListener('mousemove', inputMove, false);
canvasJoystick.addEventListener("mouseout", inputOutside, false);
if (mUp_globally){
  window.addEventListener('mouseup',inputEnd, false);
  canvasJoystick.addEventListener("mouseup", inputEnd, false);
}else {
  canvasJoystick.addEventListener("mouseup", inputEnd, false);
}
canvasJoystick.addEventListener("touchstart", inputStart, false);
canvasJoystick.addEventListener("touchend", inputEnd, false);
canvasJoystick.addEventListener("touchmove", inputMove, false);

function drawJoyField() {
  ctxJoy.clearRect(0, 0, rectJoy.width, rectJoy.height);
  ctxJoy.beginPath();
  ctxJoy.arc(rectJoy.width/2,rectJoy.height/2,25,0,2*Math.PI);
  ctxJoy.stroke();
  ctxJoy.beginPath();
  ctxJoy.arc(rectJoy.width/2,rectJoy.height/2,40,0,2*Math.PI);
  ctxJoy.stroke();
  if(mdown === false){
    ctxJoy.beginPath();
    ctxJoy.arc(rectJoy.width/2,rectJoy.height/2,10,0,2*Math.PI);
    ctxJoy.globalAlpha=0.5;
    ctxJoy.fillStyle = color_fill_style;
    ctxJoy.fill();
    ctxJoy.stroke();
  }else{
    ctxJoy.beginPath();
    ctxJoy.arc(posJoy.cx, posJoy.cy, 10, 0, 2 * Math.PI, false);
    ctxJoy.globalAlpha=1.0;
    ctxJoy.fillStyle = color_fill_style;
    ctxJoy.fill();
    ctxJoy.stroke();
  }
}

function inputStart() {
  mdown = true;
}

function inputEnd() {
  posJoy = setCenter(rectJoy);
  inputMove({ clientX: posJoy.cx, clientY: posJoy.cy});
  mdown = false;
  canvasJoystick.linearX = 0.0;
  canvasJoystick.linearY = 0.0;
  drawJoyField();
  sendPos();
}

function inputMove(e) {
  if(mdown) {
    getMousePos(e);
    getVel();
    sendPos();
  }
  drawJoyField();
}

function inputOutside() {
  if (debug) {
    console.log('out at ' + posJoy.cx + ' ' + posJoy.cy);
  }
  if (mOut) {
    inputEnd();
  }
}


function getMousePos(evt) {
  posJoy.cx =  Math.round(evt.clientX - rectJoy.left);
  posJoy.cy = Math.round(evt.clientY - rectJoy.top);
}

function getVel() {
  if (posJoy.cx < rectJoy.width / 2){
    canvasJoystick.linearX = Math.round(rectJoy.width / 2 - posJoy.cx);
    canvasJoystick.linearX = 0 - canvasJoystick.linearX;
  }else {
    canvasJoystick.linearX = Math.round(posJoy.cx - rectJoy.width / 2);
  }
  if (posJoy.cy < rectJoy.height / 2){
    canvasJoystick.linearY = Math.round(posJoy.cy - rectJoy.height / 2);
    canvasJoystick.linearY = 0 - canvasJoystick.linearY;
  }else {
    canvasJoystick.linearY = Math.round(rectJoy.height / 2 -posJoy.cy);
  }
  if (canvasJoystick.linearX > rectJoy.width){ canvasJoystick.linearX = rectJoy.width / 2}
  if (canvasJoystick.linearY > rectJoy.height){ canvasJoystick.linearY = rectJoy.height / 2}
  canvasJoystick.linearX = canvasJoystick.linearX * factor_x;
  canvasJoystick.linearY = canvasJoystick.linearY * factor_y;
}

/**
  * we always want to be between 0 and 100.
  * so we return a factor to calculate a number within the range 0 - 1
  * examples
  * 50 -> 2
  * 100 -> 1
  * 200 -> 0.5
  * 1 -> 100
  */
function rangeToFactor(max_value){
  let factor = 100;
  if(max_value > 1){
      factor = factor / max_value;
  }
  return factor;
}

function setCenter(rectJoy){
  let new_center = {
    cx: Math.round(rectJoy.height/2),
    cy: Math.round(rectJoy.width/2)
  };
  return new_center;
}

function setVelStart(){
  canvasJoystick.linearX = posJoy.cx; 
  canvasJoystick.linearY = posJoy.cy;
}

function sendPos() {
  // here we would call an api or anything which should know the result
  // console.log('ps3 x:' + ps3_axis_pos_x + ' ps3 y:' + ps3_axis_pos_y);
  // console.log('j cx:' + posJoy.cx + "j cy:" + posJoy.cy)
  if (debug){
    console.log("v x:" + canvasJoystick.linearX + ",v Y:" + canvasJoystick.linearY);
  }
  showValues();
  /* Example for sending Joystick Position over Websocket
  try { 
    ws.send(JSON.stringify (vel)); 
  } catch (e){
    if (debug){
      console.log(e.message);
    }
  }
  */
}

// -- ps3 -------------------------------------------------------------------------------------
function ps3_connected(){
  inputEnd();
  mdown = true;
}

function ps3_disconnect(){
  inputEnd();
  mdown = false;
}

// -- ps3 handlers ------------------------------
function connectHandler(e) {
  if(e.gamepad.id.includes('GamePad')){
    console.log("A gamepad connected:");
    console.log(e.gamepad);
    ps3_connected();
    addGamepad(e.gamepad);
  } else {
    console.log('unknown gamepad connected')
  }
}
function disconnectHandler(e) {
  if(e.gamepad.id.includes('GamePad')){
    console.log("A gamepad disconnected:");
    console.log(e.gamepad);
    clearInterval(draw_interval);
    ps3_disconnect();
    removeGamepad(e.gamepad);
  }
}
function addGamepad(gamepad) {
    controllers[gamepad.index] = gamepad;
    ps3_controller_connected = true;
    requestAnimationFrame(updateStatus);
}
function removeGamepad(gamepad) {
  ps3_controller_connected = false;
  delete controllers[gamepad.index];
}

function updateStatus() {
  scanGamepads();
  for (j in controllers) {
    let controller = controllers[j];
    for (let i=0; i<controller.buttons.length; i++) {
      let val = controller.buttons[i];
      let pressed = val == 1.0;
      if (typeof(val) == "object") {
        pressed = val.pressed;
        val = val.value;
      }
      if (pressed) {
        console.log("button" + [i] + " pressed " + val);
      }
    }
    for (let i=0; i<controller.axes.length; i++) {
      if (controller.axes[i] != 0.0) {
        if(i === ps3_axis_id_x){
          ps3_axis_pos_x = controller.axes[i].toFixed(2);
          ps3_axis_pos_x = Math.round(ps3_axis_pos_x * ps3_factor_x);
          if (ps3_factor_x > rectJoy.width){ ps3_axis_pos_x = rectJoy.width / 2}

        }
        if(i === ps3_axis_id_y){
          ps3_axis_pos_y = controller.axes[i].toFixed(2);
          ps3_axis_pos_y = Math.round(ps3_axis_pos_y * ps3_factor_y);
          if (ps3_axis_pos_y > rectJoy.height){ ps3_axis_pos_y = rectJoy.height / 2}
          posJoy.cy = ps3_factor_y;
        }
      }
    }
  }
  if(ps3_controller_connected === true){
    posJoy.cx = center.cx + ps3_axis_pos_x;
    posJoy.cy = center.cy + ps3_axis_pos_y;
    getVel();
    sendPos();
    requestAnimationFrame(drawJoyField);
    requestAnimationFrame(updateStatus);
  }
}

function scanGamepads() {
  let gamepads = navigator.getGamepads ? navigator.getGamepads() : (navigator.webkitGetGamepads ? navigator.webkitGetGamepads() : []);
  for (let i = 0; i < gamepads.length; i++) {
    if (gamepads[i]) {
      if (!(gamepads[i].index in controllers)) {
        addGamepad(gamepads[i]);
      } else {
        controllers[gamepads[i].index] = gamepads[i];
      }
    }
  }
}

let center = setCenter(rectJoy);

if (haveEvents) {
  window.addEventListener("gamepadconnected", connectHandler);
  window.addEventListener("gamepaddisconnected", disconnectHandler);
}

// start
inputEnd();