function myFunction(key) {
    var x = document.getElementById(key);
    var btn = document.getElementById("btn".concat(key));
    if (x.style.display === "none") {
      x.style.display = "block";
      btn.textContent = "\u2B9F";
    } else {
      x.style.display = "none";
      btn.textContent = "\u2B9E";
    }
}
