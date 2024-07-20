function openNav() {
     document.getElementById("mySidebar").style.width = "50%";
     document.getElementById("mySidebar").style.display = "block";
}

function closeNav() {
     document.getElementById("mySidebar").style.display = "none";
}
// Script to open and close sidebar
function w3_open() {
     document.getElementById("mySidebar").style.display = "block";
     document.getElementById("myOverlay").style.display = "block";
}

function w3_close() {
     document.getElementById("mySidebar").style.display = "none";
     document.getElementById("myOverlay").style.display = "none";
}
