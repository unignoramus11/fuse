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

dropZone.addEventListener("dragover", function (e) {
  e.preventDefault();
  dropZone.style.border = "2px dashed #3f3351";
});

dropZone.addEventListener("dragleave", function () {
  dropZone.style.border = "";
});

dropZone.addEventListener("drop", function (e) {
  e.preventDefault();
  dropZone.style.border = "";

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
  // Iterate over the files
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


      // Fade the image when selected
      (function (img) {
        img.addEventListener("click", function () {
          img.classList.toggle("selected");
        });
      })(img);

      // Append the image to the grid
      grid.appendChild(img);
      document.getElementById("image-grid-container").appendChild(grid);

    } else if (file.type.startsWith("audio/")) {
      // Get the audio list container
      audioListContainer = document.getElementById("audio-list-container");
      var audioItem = document.createElement("div");
      audioItem.classList.add("audio-item");
      audioItem.classList.add("prevent-select");

      var checkBox = document.createElement("input");
      checkBox.type = "checkbox";
      checkBox.classList.add("audio-checkbox");
      audioItem.append(checkBox);

      var audio = document.createElement("audio");
      audio.src = URL.createObjectURL(file);
      audio.alt = file.name;

      // Show the file name beside the audio
      var audioName = document.createElement("p");
      audioName.textContent = file.name;
      audioItem.appendChild(audioName);

      // Custom audio controls
      var audioControls = document.createElement("div");
      audioControls.classList.add("audio-controls");
      var playButton = document.createElement("button");
      playButton.type = "button";
      playButton.classList.add("play-button");
      playButton.innerHTML = '<i class="fas fa-play" style="color: white;"></i>';

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

      // Change to play button when the audio ends
      audio.addEventListener("ended", function () {
        playButton.innerHTML =
          '<i class="fas fa-play" style="color: white;"></i>';
      });

      audioControls.appendChild(playButton);
      audioItem.appendChild(audioControls);

      // Append the audio to the audio list container
      audioListContainer.appendChild(audioItem);
      audioItem.appendChild(audio);

      audioItem.addEventListener('click', function (event) {
        if (event.target !== checkBox && event.target !== playButton && event.target.tagName !== 'I') {
          checkBox.checked = !checkBox.checked;
        }
      });
    }
  }
}


// Submit project for processing
function exportProject() {
  // Open a custom dialog box to confirm the video format and resolution
  if (document.getElementById("image-grid-container").childElementCount == 0) {
    // TODO: Show error of timeline empty
    alert("Please upload images to the project before exporting.");
    return;
  }

  var dialog_container = document.getElementById("dialog-container");
  dialog_container.setAttribute("style", "display: block;");

  var dialog = document.getElementById("dialog");
  dialog.showModal();

  dialog.querySelector(".close").addEventListener("click", () => {
    dialog.close();
    dialog_container.setAttribute("style", "display: none;");
  });

  dialog.querySelector(".confirm").addEventListener("click", () => {
    // Send the project to the server for processing
    dialog_container.setAttribute("style", "display: none;");
    // Show success message
    var success_dialog_container = document.getElementById("succesful-dialog-container");
    success_dialog_container.setAttribute("style", "display: block;");
    var success_dialog = document.getElementById("succesful-dialog");
    success_dialog.showModal();

    success_dialog.querySelector(".dashboardPage").addEventListener("click", () => {
      document.getElementById('drop-zone').submit();
      success_dialog.close();
      success_dialog_container.setAttribute("style", "display: none;");
    });
    dialog.close();
  });

  // Let users choose the export resolution
  var resolution = document.getElementById("resolution");
  var projectName = projectInput.value;
  var exportResolution = resolution.value;
  showResolution();

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

generateRuler();


function handleSubmit(event) {
  event.preventDefault();
  return false;
}

function searchImage(searchTerm) {
  let imageDivs = document.querySelectorAll(".image-grid");

  imageDivs.forEach(div => {
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
  searchImage(searchTerm.toLowerCase())
});


function searchAudio(searchTerm) {
  let audioDivs = document.querySelectorAll(".audio-item");

  audioDivs.forEach(div => {
    let altText = div.querySelector("audio").alt.toLowerCase();

    if (altText.includes(searchTerm)) {
      div.style.display = "flex";
    } else {
      div.style.display = "none";
    }
  });
}

let findAud = document.getElementById("searchright2");
findAud.addEventListener("keydown", () => {
  let searchTerm = findAud.value;
  searchAudio(searchTerm.toLowerCase())
});