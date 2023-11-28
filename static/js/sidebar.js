document.getElementById("avatar").addEventListener("click", () => {
    var menu = document.getElementById("menu");
    if (menu.style.visibility === "hidden" || menu.style.visibility === "") {
        menu.style.visibility = "visible";
        menu.style.opacity = 1;
    } else {
        menu.style.visibility = "hidden";
        menu.style.opacity = 0;
    }
})