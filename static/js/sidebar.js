function toggleSidebarMenu() {
    var menu = document.getElementById("menu");
    if (typeof menu === 'undefined' || menu === null) {
        return;
    }
    if (menu.style.visibility === "hidden" || menu.style.visibility === "") {
        menu.style.visibility = "visible";
        menu.style.opacity = 1;
    } else {
        menu.style.visibility = "hidden";
        menu.style.opacity = 0;
    }
}