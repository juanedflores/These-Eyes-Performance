let capture;

function setup() {
  capture = createCapture(VIDEO);
  capture.size(320, 240);
  capture.center();
  capture.parent("cam");

  interact_button = createButton("Interact!");
  interact_button.parent("interact");
  // interact_button.id("button");
  // capture.hide();
}

function draw() {
  // image(capture, 0, 0, width, (width * capture.height) / capture.width);
  // filter(INVERT);
}
