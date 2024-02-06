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
var fileList = document.getElementById("file-list");

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

function displayFiles(files) {
  for (var i = 0; i < files.length; i++) {
    var fileItem = document.createElement("div");
    fileItem.textContent = `File Name: ${files[i].name}, Size: ${files[i].size} bytes`;
    fileList.appendChild(fileItem);
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
  const duration = 500;

  // Clear the ruler container
  const rulerContainer = document.getElementById("ruler");
  rulerContainer.innerHTML = "";

  // Generate the ruler ticks
  for (let i = 0; i <= duration; i += 5) {
    const tickLabel = document.createElement("div");
    tickLabel.className = "tickLabel";
    tickLabel.textContent = `${i}s`;

    rulerContainer.appendChild(tickLabel);
  }
}

generateRuler();
