(function () {
  var width = 1080;
  var height = 0;

  var streaming = false;

  var video = null;
  var canvas = null;
  var photo = null;
  var showcambutton = null;
  var takepicturebutton = null;
  var submitbutton = null;

  const API_URL = "/api/handleImages";

  function startup() {
    video = document.getElementById("video");
    canvas = document.getElementById("canvas");
    photo = document.getElementById("photo");
    showcambutton = document.getElementById("showcambutton");
    takepicturebutton = document.getElementById("takepicturebutton");
    submitbutton = document.getElementById("submitbutton");

    video.addEventListener(
      "canplay",
      function (ev) {
        if (!streaming) {
          height = video.videoHeight / (video.videoWidth / width);

          // Firefox currently has a bug where the height can't be read from
          // the video, so we will make assumptions if this happens.
          if (isNaN(height)) {
            height = width / (4 / 3);
          }

          video.setAttribute("width", width);
          video.setAttribute("height", height);
          canvas.setAttribute("width", width);
          canvas.setAttribute("height", height);
          streaming = true;
        }
        takepicturebutton.style.display = "block";
      },
      false
    );

    showcambutton.addEventListener("click", function () {
      navigator.mediaDevices
        .getUserMedia({ video: true, audio: false })
        .then(function (stream) {
          video.srcObject = stream;
          video.play();
        })
        .catch(function (err) {
          console.log("An error occurred: " + err);
        });
      showcambutton.style.display = "none";
    });

    takepicturebutton.addEventListener(
      "click",
      function (ev) {
        takepicture();
        ev.preventDefault();
        video.pause();
        // styling
        submitbutton.style.display = "block";
        takepicturebutton.style.right = "20px";
      },
      false
    );

    submitbutton.addEventListener(
      "click",
      function (ev) {
        // takepicture();

        // set a limit to how many pictures the user can submit.
        setTimeout(function () {}, 5000);
      },
      false
    );
    // clearphoto();
  }

  // Fill the photo with an indication that none has been
  // captured.

  // function clearphoto() {
  // var context = canvas.getContext("2d");
  // context.fillStyle = "#AAA";
  // context.fillRect(0, 0, canvas.width, canvas.height);

  // var data = canvas.toDataURL("image/png");
  // photo.setAttribute("src", data);
  // }

  // Capture a photo by fetching the current contents of the video
  // and drawing it into a canvas, then converting that to a PNG
  // format data URL. By drawing it on an offscreen canvas and then
  // drawing that to the screen, we can change its size and/or apply
  // other changes before drawing it.

  function takepicture() {
    var context = canvas.getContext("2d");
    if (width && height) {
      canvas.width = width;
      canvas.height = height;
      context.drawImage(video, 0, 0, width, height);

      // This is where we turn the image to a png.
      var data = canvas.toDataURL("image/png");
      image = data.replace("data:image/png;base64,", "");
      // TODO: send the png to server to be processed.
      // newdata = JSON.stringify({ image: data });
      sendPhotoToServer(image);

      // photo.setAttribute("src", data);
    } else {
      // clearphoto();
    }
  }

  function sendPhotoToServer(photo) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/handleImages", true);
    xhr.setRequestHeader("Content-Type", "image/png");
    xhr.onreadystatechange = function () {
      // Call a function when the state changes.

      if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
        // Request finished. Do processing here.
      }
    };
    xhr.send(photo);
  }

  // Set up our event listener to run the startup process
  // once loading is complete.
  window.addEventListener("load", startup, false);
})();
