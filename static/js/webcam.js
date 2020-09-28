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

          video.setAttribute("width", width / 3);
          video.setAttribute("height", height / 3);
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
      video.style.display = "block";
    });

    takepicturebutton.addEventListener(
      "click",
      function (ev) {
        let image = takepicture();
        sendPhotoToServer(image, "/api/detectEyes", false);

        ev.preventDefault();
        // styling
        canvas.style.display = "block";
      },
      false
    );

    submitbutton.addEventListener(
      "click",
      function (ev) {
        var imageURI = canvas.toDataURL("image/png");
        image = imageURI.replace("data:image/png;base64,", "");

        sendPhotoToServer(image, "/api/insertEyes", true);
        // Remove the eyes.
        document.getElementById("eyeimgs").innerHTML = "";
        // Clear Canvas.
        var context = canvas.getContext("2d");
        context.fillStyle = "#AAA";
        context.fillRect(0, 0, canvas.width, canvas.height);
        // styling
        submitbutton.style.display = "none";
        document.getElementById("eyenum").innerHTML = "Submitted!";
        // set a limit to how many pictures the user can submit.

        takepicturebutton.setAttribute("disabled", "disabled");
        setTimeout(function () {
          takepicturebutton.removeAttribute("disabled");
        }, 5000);
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

      return image;
    } else {
      // clearphoto();
      return "null";
    }
  }

  function sendPhotoToServer(photo, url, submitting) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "image/png");
    xhr.onreadystatechange = function () {
      // Call a function when the state changes.
      if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
        // Request finished. Do processing here.

        if (!submitting) {
          obj = JSON.parse(this.response);

          document.getElementById("eyenum").innerHTML =
            "<p>Detected <em style='color:red'>" +
            " " +
            obj.num[0] +
            " " +
            "</em>eyes.</p>";
          if (obj.img !== "[]") {
            // Get response which is a dictionary and turn it into an array.
            responseimg = obj.img;
            base64img = responseimg.substring(1, responseimg.length - 1);
            base64img = responseimg.split(",");
            // Iterate through the array.
            if (base64img.length >= 1) {
              submitbutton.style.display = "block";
            }
            submitbutton.style.display = "block";
            for (let i = 0; i < base64img.length; i++) {
              img_64 = base64img[i]
                .substring(3, base64img[i].length - 1)
                .replace("'", "");
              // console.log(img_64);
              let image = new Image();
              image.src = "data:image/jpg;base64," + img_64;
              var context = canvas.getContext("2d");
              if (width && height) {
                console.log("drawing image..");
                imgElement = document.createElement("img");
                imgElement.src = "data:image/jpg;base64," + img_64;

                document.getElementById("eyeimgs").appendChild(imgElement);
              }
            }
          }
        }
      }
    };
    xhr.send(photo);
  }

  // Set up our event listener to run the startup process
  // once loading is complete.
  window.addEventListener("load", startup, false);
})();
