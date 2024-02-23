var toSubmit = false; // Flag to track if the form is ready to be submitted
var activeUploads = 0; // Number of active uploads

// Set a random project name with an adjective and an animal
let projectInput = document.getElementById("projectName");
projectInput.placeholder = "Loading...";
fetch("https://random-word-form.herokuapp.com/random/adjective")
  .then((response) => response.json())
  .then((adjective) => {
    fetch("https://random-word-form.herokuapp.com/random/animal")
      .then((response) => response.json())
      .then((noun) => {
        var newName = adjective[0] + " " + noun[0];
        // Convert to title case
        newName = newName.replace(/\b\w/g, (l) => l.toUpperCase());

        // Set the project name and the title bar
        document.title = "Fuse | " + newName;
        projectInput.placeholder = newName;
      });
  });

// Change the title bar every time the project is renamed
projectInput.addEventListener("change", function () {
  document.title = "Fuse | " + projectInput.value;
  if (projectInput.value == "") {
    document.title = "Fuse | " + projectInput.placeholder;
  }

  previewProject();
});

// Change the search icon color when the input is focused for all the search boxes
let searchInput = document.getElementsByClassName("searchbutton");
let searchIcon = document.getElementsByClassName("mglass");

for (var i = 0; i < searchInput.length; i++) {
  searchInput[i].addEventListener("focus", function () {
    this.nextElementSibling.style.color = "#3f3351";
  });

  searchInput[i].addEventListener("blur", function () {
    this.nextElementSibling.style.color = "black";
  });
}

// Drag and drop support
let dropZone = document.getElementById("drop-zone");
let fileInput = document.getElementById("docpicker");
let fileList = document.getElementById("image-list");

dropZone.addEventListener("dragover", function () {
  dropZone.style.border = "2px dashed #3f3351";
});

dropZone.addEventListener("dragleave", function () {
  dropZone.style.border = "";
});

dropZone.addEventListener("drop", function (e) {
  dropZone.style.border = "";
  e.preventDefault();

  var files = e.dataTransfer.files;
  displayFiles(files);
});

fileInput.addEventListener("change", function (e) {
  var files = e.target.files;
  displayFiles(files);
});

// Click event to trigger file input
dropZone.addEventListener("click", function () {
  fileInput.click();
});

// Sorting images and audio in their respective boxes
function displayFiles(files) {
  for (var i = 0; i < files.length; i++) {
    var file = files[i];

    // Check the file type and add it to the appropriate place
    if (file.type.startsWith("image/")) {
      // Create a new image grid
      var grid = document.createElement("div");
      grid.classList.add("image-grid");
      // Create a new image element
      var img = document.createElement("img");
      // Set the image source and alt attributes
      img.src = URL.createObjectURL(file);
      img.style.width = "100%";

      img.alt = file.name;

      ((img, file) => {
        let timelineImageContainer;
        img.addEventListener("click", function () {
          img.classList.toggle("selected");

          if (img.classList.contains("selected")) {
            timelineImageContainer = document.createElement("div");
            timelineImageContainer.classList.add("img-item");
            timelineImageContainer.classList.add("prevent-select");
            // Set the width of the image such that it matches with the timeline and is 5s long
            let duration = 5;
            let imageWidth = duration * 5;
            timelineImageContainer.style.width = imageWidth + "vw";
            timelineImageContainer.style.backgroundImage = `url(${URL.createObjectURL(
              file
            )})`;

            timelineImageContainer.innerHTML = `
              <form id="${file.name.replace(
                /\s/g,
                "_"
              )}_form" class="timeline-image-modifiers">
                  <button type="button" class="leftArrow">
                    <i class="fa-solid fa-arrow-left"></i>
                  </button>
                  <input
                    type="number"
                    name="imgDuration"
                    placeholder="5s"
                  />
                  <input
                    type="text"
                    name="imgTransition"
                    value="fade"
                    hidden
                  />
                  <button type="button" class="rightArrow">
                    <i class="fa-solid fa-arrow-right"></i>
                  </button>
                </form>`;
            // add a click event listener to the image element which toggles the active class
            timelineImageContainer.addEventListener("click", function (e) {
              if (
                e.target.tagName !== "INPUT" &&
                e.target.tagName !== "BUTTON" &&
                e.target.tagName !== "I"
              ) {
                for (let i = 0; i < imageContent.children.length; i++) {
                  if (imageContent.children[i] !== timelineImageContainer)
                    imageContent.children[i].classList.remove("active");
                }
                timelineImageContainer.classList.toggle("active");

                // if no image is active or the activated image is removed from timeline. hide the transition list content id div
                if (!timelineImageContainer.classList.contains("active")) {
                  document.getElementById(
                    "transition-list-content"
                  ).style.display = "none";
                  document.getElementById(
                    "transition-list-placeholder"
                  ).style.display = "flex";
                } else {
                  document.getElementById(
                    "transition-list-content"
                  ).style.display = "flex";
                  document.getElementById(
                    "transition-list-content"
                  ).style.justifyContent = "center";
                  document.getElementById(
                    "transition-list-content"
                  ).style.alignItems = "center";
                  document.getElementById(
                    "transition-list-placeholder"
                  ).style.display = "none";

                  // Set the transition list element to active
                  let activeImage = document.querySelector(".img-item.active");
                  if (activeImage) {
                    // Getting transition id from the form
                    let transitionName = activeImage.querySelector(
                      "input[name=imgTransition]"
                    ).value;
                    for (let j = 0; j < transitionList.children.length; j++) {
                      if (transitionList.children[j].id === transitionName) {
                        transitionList.children[j].classList.add("active");
                      } else {
                        transitionList.children[j].classList.remove("active");
                      }
                    }
                  }
                }
              }
            });

            // add a duration change event listener
            let imgDuration = timelineImageContainer.querySelector(
              "input[name=imgDuration]"
            );
            imgDuration.addEventListener("change", function () {
              let duration = imgDuration.value;
              if (duration === "") {
                duration = 5;
                imgDuration.value = 5;
              }
              if (duration < 1) {
                duration = 1;
                imgDuration.value = 1;
              }
              let imageWidth = duration * 5;
              timelineImageContainer.style.width = imageWidth + "vw";
              // make it so that the text input is no longer selected
              imgDuration.blur();
              previewProject();
            });

            // add a left arrow click event listener, which exchanges the image element with the one before it
            let leftArrow = timelineImageContainer.querySelector(".leftArrow");
            leftArrow.addEventListener("click", function () {
              let previous = timelineImageContainer.previousElementSibling;
              if (previous) {
                timelineImageContainer.parentNode.insertBefore(
                  timelineImageContainer,
                  previous
                );
                previewProject();
              }
            });

            // add a right arrow click event listener, which exchanges the image element with the one after it
            let rightArrow =
              timelineImageContainer.querySelector(".rightArrow");
            rightArrow.addEventListener("click", function () {
              let next = timelineImageContainer.nextElementSibling;
              if (next) {
                timelineImageContainer.parentNode.insertBefore(
                  next,
                  timelineImageContainer
                );
                previewProject();
              }
            });

            var imageContent = document.getElementById("imgContent");
            imageContent.appendChild(timelineImageContainer);
          } else {
            if (timelineImageContainer && timelineImageContainer.parentNode) {
              timelineImageContainer.parentNode.removeChild(
                timelineImageContainer
              );
            }

            for (let i = 0; i < imageContent.children.length; i++) {
              imageContent.children[i].style.display = "flex";
            }
          }

          previewProject();
        });
      })(img, file);

      // Append the image to the grid
      grid.appendChild(img);
      document.getElementById("image-grid-container").appendChild(grid);
    } else if (file.type.startsWith("audio/")) {
      // Get the audio list container
      audioListContainer = document.getElementById("audio-list-container");
      var audioItem = document.createElement("div");
      audioItem.classList.add("audio-item", "prevent-select");

      var checkBox = document.createElement("input");
      checkBox.type = "checkbox";
      checkBox.classList.add("audio-checkbox");
      audioItem.append(checkBox);

      var audio = document.createElement("audio");
      audio.src = URL.createObjectURL(file);
      audio.alt = file.name;

      // Show the file name beside the audio
      var audioName = document.createElement("p");
      // set the text of the p element to the file name after replacing _ with space
      audioName.textContent = file.name.replace(/\_/g, " ");
      audioItem.appendChild(audioName);

      // Custom audio controls
      var audioControls = document.createElement("div");
      audioControls.classList.add("audio-controls");
      var playButton = document.createElement("button");
      playButton.type = "button";
      playButton.classList.add("play-button");
      playButton.innerHTML =
        '<i class="fas fa-play" style="color: white;"></i>';

      ((audio, playButton) => {
        playButton.addEventListener("click", function () {
          if (audio.paused) {
            audio.play();
            // Change it into play button
            playButton.innerHTML =
              '<i class="fas fa-pause" style="color: white;"></i>';
          } else {
            audio.pause();
            // Change it into pause button
            playButton.innerHTML =
              '<i class="fas fa-play" style="color: white;"></i>';
          }
        });
      })(audio, playButton);

      // Change to play button when the audio ends
      ((audio, playButton) => {
        audio.addEventListener("ended", function () {
          playButton.innerHTML =
            '<i class="fas fa-play" style="color: white;"></i>';
        });
      })(audio, playButton);

      audioControls.appendChild(playButton);
      audioItem.appendChild(audioControls);

      // Append the audio to the audio list container
      audioListContainer.appendChild(audioItem);
      audioItem.appendChild(audio);

      ((file, audioItem, checkBox, playButton) => {
        // create an aud-item for timeline similar to the img-item
        let audItem;

        let audioList = document.getElementById("audContent");
        audioItem.addEventListener("click", function (event) {
          if (event.target !== playButton && event.target.tagName !== "I") {
            if (event.target !== checkBox) checkBox.checked = !checkBox.checked;
            if (checkBox.checked) {
              audItem = document.createElement("div");
              audItem.classList.add("aud-item");
              audItem.classList.add("prevent-select");
              audItem.style.width = "50vw";
              audItem.innerHTML = `
          <form id="${file.name.replace(
            /\s/g,
            "_"
          )}_form" class="timeline-audio-modifiers">
            <button type="button" class="leftArrow">
              <i class="fa-solid fa-arrow-left"></i>
            </button>
            <input type="text" class="file-name" value="${
              file.name.length > 20
                ? file.name.substring(0, 20) + "..."
                : file.name
            }" readonly />
            <input
              type="number"
              name="audDuration"
              placeholder="10s"
            />
            <button type="button" class="rightArrow">
              <i class="fa-solid fa-arrow-right"></i>
            </button>
          </form>
        `;
              // we don't need an active class in audio, just left, right, duration change
              // add a duration change event listener
              let audDuration = audItem.querySelector(
                "input[name=audDuration]"
              );
              audDuration.addEventListener("change", function () {
                let duration = audDuration.value;
                if (duration === "") {
                  duration = 10;
                  audDuration.value = 10;
                }
                if (duration < 3) {
                  duration = 3;
                  audDuration.value = 3;
                }
                let audioWidth = duration * 5;
                audItem.style.width = audioWidth + "vw";
                // make it so that the text input is no longer selected
                audDuration.blur();
                previewProject();
              });

              // add a left arrow click event listener, which exchanges the audio element with the one before it
              let leftArrow = audItem.querySelector(".leftArrow");
              leftArrow.addEventListener("click", function () {
                let previous = audItem.previousElementSibling;
                if (previous) {
                  audItem.parentNode.insertBefore(audItem, previous);
                }
              });

              // add a right arrow click event listener, which exchanges the audio element with the one after it
              let rightArrow = audItem.querySelector(".rightArrow");
              rightArrow.addEventListener("click", function () {
                let next = audItem.nextElementSibling;
                if (next) {
                  audItem.parentNode.insertBefore(next, audItem);
                }
              });
              audioList.appendChild(audItem);
            } else {
              audioList.removeChild(audItem);
            }
            previewProject();
          }
        });
      })(file, audioItem, checkBox, playButton);
    }
  }
}

window.onload = () => {
  displayFiles([]);
};

// Submit project for processing
function exportProject() {
  // Alert if timeline is empty
  if (
    !document.getElementById("image-grid-container").childElementCount ||
    !document.getElementById("imgContent").childElementCount
  ) {
    alert("Please add at least one image to the timeline before exporting.");
    return;
  }

  // Open a custom dialog box to confirm the video format and resolution
  var dialog_container = document.getElementById("dialog-container");
  dialog_container.setAttribute("style", "display: block;");

  var dialog = document.getElementById("dialog");
  dialog.showModal();

  dialog.querySelector(".close").addEventListener("click", () => {
    dialog.close();
    dialog_container.setAttribute("style", "display: none;");
  });

  dialog.querySelector(".confirm").addEventListener("click", () => {
    // Fetch the project name and the export resolution and store it as json file
    var projectInput = document.getElementById("projectName");
    var formatInput = document.getElementById("exportFormat");
    var resolutionInput = document.getElementById("resolution");

    var projectName =
      projectInput.value == "" ? projectInput.placeholder : projectInput.value;
    var exportFormat = formatInput.value;
    var exportResolution = resolutionInput.value;
    var height, width;

    if (exportResolution == "360p") {
      height = 360;
      width = 640;
    } else if (exportResolution == "480p") {
      height = 480;
      width = 854;
    } else if (exportResolution == "720p") {
      height = 720;
      width = 1280;
    } else if (exportResolution == "1080p") {
      height = 1080;
      width = 1920;
    } else if (exportResolution == "2160p") {
      height = 2160;
      width = 3840;
    } else {
      height = parseInt(document.getElementById("height").value);
      width = parseInt(document.getElementById("width").value);
    }

    // Create a json object

    // get all the image elements one by one, in order of occurrence, with their respective durations and transitions
    let imageContent = document.getElementById("imgContent");
    let images = [];
    for (let i = 0; i < imageContent.children.length; i++) {
      let image = imageContent.children[i];
      let duration = image.querySelector("input[name=imgDuration]").value;
      if (duration === "") {
        duration = 5;
        image.querySelector("input[name=imgDuration]").value = 5;
      }
      let transition = image.querySelector("input[name=imgTransition]").value;
      // get source of the image, src, from the name of the form element which is child of image, after removing the _form suffix
      let src = image.querySelector("form").id.replace("_form", "");
      images.push({
        file: src,
        duration_ms: duration * 1000,
        transition: transition,
      });
    }

    // get all the audio elements one by one, in order of occurrence, with their respective durations
    let audioContent = document.getElementById("audContent");
    let audio = [];
    for (let i = 0; i < audioContent.children.length; i++) {
      let audioItem = audioContent.children[i];
      let duration = audioItem.querySelector("input[name=audDuration]").value;
      if (duration === "") {
        duration = 10;
        audioItem.querySelector("input[name=audDuration]").value = 10;
      }
      // get source of the audio, src, from the name of the form element, after removing the _form suffix
      let src = audioItem.querySelector("form").id.replace("_form", "");
      audio.push({
        file: src,
        duration_ms: duration * 1000,
      });
    }

    var project = {
      name: projectName,
      format: exportFormat,
      height: height,
      width: width,
      images: images,
      audio: audio,
    };

    // write this json file into the textbox with id json
    document.getElementById("json").value = JSON.stringify(project);
    // set the text of submit button to please wait
    document.getElementById("submit").textContent = "Please wait... ";
    // add a spinning loading icon to the submit button
    document.getElementById("submit").innerHTML +=
      '<i class="fas fa-spinner fa-spin"></i>';

    // set the toSubmit flag to true
    toSubmit = true;
    submitProject();
  });

  showResolution();
}

// Submit project for processing
async function previewProject() {
  if (
    !document.getElementById("image-grid-container").childElementCount ||
    !document.getElementById("imgContent").childElementCount
  ) {
    return;
  }

  // set the cotent of the play button as a spinner
  document.getElementById("playButton").innerHTML =
    '<i class="fas fa-spinner fa-spin" style="color: white;"></i>';

  // Wait until activeUploads is zero
  while (activeUploads !== 0) {
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }

  var projectName =
    projectInput.value == "" ? projectInput.placeholder : projectInput.value;

  // get all the image elements one by one, in order of occurrence, with their respective durations and transitions
  let imageContent = document.getElementById("imgContent");
  let images = [];
  for (let i = 0; i < imageContent.children.length; i++) {
    let image = imageContent.children[i];
    let duration = image.querySelector("input[name=imgDuration]").value;
    if (duration === "") {
      duration = 5;
      image.querySelector("input[name=imgDuration]").value = 5;
    }
    let transition = image.querySelector("input[name=imgTransition]").value;
    // get source of the image, src, from the name of the form element which is child of image, after removing the _form suffix
    let src = image.querySelector("form").id.replace("_form", "");
    images.push({
      file: src,
      duration_ms: duration * 1000,
      transition: transition,
    });
  }

  // get all the audio elements one by one, in order of occurrence, with their respective durations
  let audioContent = document.getElementById("audContent");
  let audio = [];
  for (let i = 0; i < audioContent.children.length; i++) {
    let audioItem = audioContent.children[i];
    let duration = audioItem.querySelector("input[name=audDuration]").value;
    if (duration === "") {
      duration = 10;
      audioItem.querySelector("input[name=audDuration]").value = 10;
    }
    // get source of the audio, src, from the name of the form element, after removing the _form suffix
    let src = audioItem.querySelector("form").id.replace("_form", "");
    audio.push({
      file: src,
      duration_ms: duration * 1000,
    });
  }

  var project = {
    name: projectName,
    format: "mp4",
    height: 360,
    width: 640,
    images: images,
    audio: audio,
  };

  // write this json file into the textbox with id json
  document.getElementById("json").value = JSON.stringify(project);

  console.log("Previewing project: ", project);

  // send the project json to the server at the /preview endpoint
  fetch("/preview", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(project),
  }).then((response) => {
    if (!response.ok) {
      alert("Error: " + response.statusText);
    } else {
      getPreview();
    }
  });
}

function showResolution() {
  var Res = document.getElementById("resolution").value;

  if (Res !== "Custom") {
    var allTabs = document.querySelectorAll(".hidden");
    allTabs.forEach((tab) => {
      tab.style.display = "none";
    });
    return;
  }

  // Hide all tabs
  var allTabs = document.querySelectorAll(".hidden");

  allTabs.forEach((tab) => {
    tab.style.display = "none";
  });

  // Show the selected tab
  document.getElementById(Res).style.display = "block";
}

// Generate the seconds labels for the timeline
function generateRuler() {
  const duration = 300;

  // Clear the ruler container
  const rulerContainer = document.getElementById("ruler");
  rulerContainer.innerHTML = "";

  // Generate the ruler ticks
  for (let i = 0; i <= duration; i += 5) {
    const tickLabel = document.createElement("div");
    tickLabel.className = "tickLabel";
    tickLabel.textContent = `${i}s`;
    rulerContainer.appendChild(tickLabel);

    for (let j = 0; j < 4; j += 1) {
      const tickLabel = document.createElement("div");
      tickLabel.className = "tickLabel";
      tickLabel.textContent = ` | `;
      rulerContainer.appendChild(tickLabel);
    }
  }
}

// Make the video controls work
let video = document.getElementById("video");
let playButton = document.getElementById("playButton");
let fromStartButton = document.getElementById("fromStartButton");
let toEndButton = document.getElementById("toEndButton");
let rewindButton = document.getElementById("rewindButton");
let forwardButton = document.getElementById("forwardButton");

playButton.addEventListener("click", function () {
  if (video.paused) {
    video.play();
    // Change it into play button
    playButton.innerHTML = '<i class="fas fa-pause" style="color: white;"></i>';
  } else {
    video.pause();
    // Change it into pause button
    playButton.innerHTML = '<i class="fas fa-play" style="color: white;"></i>';
  }
});

fromStartButton.addEventListener("click", function () {
  video.currentTime = 0;
});

toEndButton.addEventListener("click", function () {
  video.currentTime = video.duration;
  video.pause();
  // Change it into pause button
  playButton.innerHTML = '<i class="fas fa-play" style="color: white;"></i>';
});

rewindButton.addEventListener("click", function () {
  video.currentTime -= 5;
});

forwardButton.addEventListener("click", function () {
  video.currentTime += 5;
});

// Make the seekbar work
let seekBar = document.getElementById("seekBar");

video.addEventListener("timeupdate", function () {
  let value = (100 / video.duration) * video.currentTime;
  seekBar.value = value;
});

function seek() {
  let time = video.duration * (seekBar.value / 100);
  video.currentTime = time;
}

// If video ends then change the play button to play
video.addEventListener("ended", function () {
  playButton.innerHTML = '<i class="fas fa-play" style="color: white;"></i>';
});

generateRuler();

function handleSubmit(event) {
  event.preventDefault();
  return false;
}

function searchImage(searchTerm) {
  let imageDivs = document.querySelectorAll(".image-grid");

  imageDivs.forEach((div) => {
    let altText = div.querySelector("img").alt.toLowerCase();

    if (altText.includes(searchTerm)) {
      div.style.display = "flex";
    } else {
      div.style.display = "none";
    }
  });
}

let findImg = document.getElementById("searchright");
findImg.addEventListener("keydown", () => {
  let searchTerm = findImg.value;
  searchImage(searchTerm.toLowerCase());
});

function searchAudio(searchTerm) {
  let audioDivs = document.querySelectorAll(".audio-item");

  audioDivs.forEach((div) => {
    let altText = div.querySelector("audio").alt.toLowerCase();

    if (altText.includes(searchTerm)) {
      div.style.display = "flex";
    } else {
      div.style.display = "none";
    }
  });
}

let findAud = document.getElementById("searchright2");
findAud.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
  }
  let searchTerm = findAud.value;
  searchAudio(searchTerm.toLowerCase());
});

document.getElementById("transition-list-content").style.display = "none";
document.getElementById("transition-list-placeholder").style.display = "flex";

// make the transition selection work
let transitionList = document.getElementById("transition-list-container");
for (let i = 0; i < transitionList.children.length; i++) {
  transitionList.children[i].addEventListener("click", function () {
    let activeImage = document.querySelector(".img-item.active");
    if (activeImage) {
      // set the value of the child form's imgTransition input to the transition name
      activeImage.querySelector("input[name=imgTransition]").value =
        transitionList.children[i].id;
    }
    // add the active class to the transition list element
    for (let j = 0; j < transitionList.children.length; j++) {
      transitionList.children[j].classList.remove("active");
    }
    transitionList.children[i].classList.add("active");
    previewProject();
  });
}

function searchTransition(searchTerm) {
  let transDivs = document.querySelectorAll(".transition-item");

  transDivs.forEach((div) => {
    let transName = div.id.toLowerCase();

    if (transName.includes(searchTerm)) {
      div.style.display = "flex";
    } else {
      div.style.display = "none";
    }
  });
}

let findTrans = document.getElementById("searchright1");
findTrans.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
  }
  let searchTerm = findTrans.value;
  searchTransition(searchTerm.toLowerCase());
});

// create a function to handle the form submission if the toSubmit flag is true
function submitProject() {
  if (toSubmit && activeUploads == 0) {
    document.getElementById("drop-zone").submit();
  }
}

// Create a jQuery object for the uploader element
$(document).ready(function () {
  var uploader = $("#drop-zone");
  // Initialize the dmUploader plugin
  uploader.dmUploader({
    url: "/upload_files",
    onInit: function () {
      // console.log("Uploader initialized");
    },
    onNewFile: function (id, file) {
      console.log("New file added to queue, id:", id);
      activeUploads++;
    },
    onUploadProgress: function (id, percent) {
      console.log("Upload progress for file id", id, ":", percent, "%");
    },
    onUploadSuccess: function (id, data) {
      console.log(
        "Upload finished for file id",
        id,
        ", server response:",
        data
      );
      activeUploads--;
      submitProject();
    },
  });

  // When a file is added to the queue, upload it immediately
  uploader.on("newFile", function (id, file) {
    uploader.dmUploader("start", id);
  });
});

function getPreview() {
  // fetch the video from the server
  fetch("/get_preview")
    .then((response) => {
      if (!response.ok) {
        alert("Error: " + response.statusText);
      }
      return response.blob();
    })
    .then((blob) => {
      // create a url for the blob
      let url = URL.createObjectURL(blob);
      // set the video source to the url
      video.src = url;
      // When the video has loaded its metadata, reset the currentTime and seekBar.value
      video.onloadedmetadata = function () {
        video.currentTime = 0;
        seekBar.value = 0;
        seek();
        // set the content of play button back to play icon
        document.getElementById("playButton").innerHTML =
          '<i class="fas fa-play" style="color: white;"></i>';
      };
    });
}

// once the page has loaded, fetch the sample audio and image list
// first get the names of the sample audio files from the sample-audio id textbox
// then get the names of the sample image files from the sample-images id textbox
// then fetch the audio and image files from the server and create a list of javascript file objects for these all of these files
// finally, call the displayFiles function with the list of file objects

window.onload = () => {
  let audioNames = document.getElementById("sample-audio").value.split(",");
  let imageNames = document.getElementById("sample-images").value.split(",");

  let audioFiles = [];
  let imageFiles = [];

  if (audioNames.length != 0 && audioNames[0] != "") {
    audioNames.forEach((name) => {
      fetch(`/get_samples/audio/${name}`)
        .then((response) => response.blob())
        .then((blob) => {
          audioFiles.push(new File([blob], name, { type: "audio/mpeg" }));
          if (audioFiles.length === audioNames.length) {
            displayFiles(audioFiles);
          }
        });
    });
  }

  // get the image files from the server using the /get_samples/<media_type>/<filename> endpoint
  if (imageNames.length != 0 && imageNames[0] != "") {
    imageNames.forEach((name) => {
      fetch(`/get_samples/images/${name}`)
        .then((response) => response.blob())
        .then((blob) => {
          imageFiles.push(new File([blob], name, { type: "image/png" }));
          if (imageFiles.length === imageNames.length) {
            displayFiles(imageFiles);
          }
        });
    });
  }
};
