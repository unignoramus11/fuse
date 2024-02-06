// Set a random project name with an adjective and an animal
var projectInput = document.getElementById("projectName");
projectInput.placeholder = "Loading...";
fetch("https://random-word-form.herokuapp.com/random/adjective")
  .then((response) => response.json())
  .then((adjective) => {
    fetch("https://random-word-form.herokuapp.com/random/animal")
      .then((response) => response.json())
      .then((noun) => {
        var newName = adjective[0] + " " + noun[0];
        projectInput.placeholder = newName;
      });
  });

// Change the title bar every time the project is renamed
projectInput.addEventListener("input", function () {
  document.title = "Fuse | " + projectInput.value;
});

// Change the search icon color when the input is focused for all the search boxes
var searchInput = document.getElementsByClassName("searchbutton");
var searchIcon = document.getElementsByClassName("mglass");

for (var i = 0; i < searchInput.length; i++) {
  searchInput[i].addEventListener("focus", function () {
    this.nextElementSibling.style.color = "#3f3351";
  });

  searchInput[i].addEventListener("blur", function () {
    this.nextElementSibling.style.color = "black";
  });
}

// Change the color of the search icon when the input is focused
var searchInput = document.getElementById("search");
var searchIcon = document.getElementById("searchicon");

// Drag and drop support
var dropZone = document.getElementById("drop-zone");
var fileInput = document.getElementById("docpicker");
var fileList = document.getElementById("image-list");

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

    // Check the file type and add it to the appropriate list
    if (file.type.startsWith("image/")) {
      var grid = document.createElement("div");
      grid.classList.add("image-grid");
      var img = document.createElement("img");
      img.src = URL.createObjectURL(file);
      img.style.width = "100%";
      img.alt = file.name;
      grid.appendChild(img);
      document.getElementById("image-grid-container").appendChild(grid);
    } else if (file.type.startsWith("audio/")) {
      var container = document.createElement("div");
      grid.classList.add("audio-list");
      // make it so that the 
      document.getElementById("audio-list").appendChild(grid);
    }
  }
}

// Submit project for processing
function exportProject() {
  // Open a custom dialog box to confirm the project name

  var dialog = document.getElementById("dialog");
  dialog.showModal();

  dialog.querySelector(".close").addEventListener("click", () => {
    dialog.close();
  });

  dialog.querySelector(".confirm").addEventListener("click", () => {
    dialog.close();
  });

  // Let users choose the export resolution

  var resolution = document.getElementById("resolution");

  // Send the project to the server for processing

  var projectName = projectInput.value;
  var exportResolution = resolution.value;
}

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

generateRuler();
