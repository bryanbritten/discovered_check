function hideModalTabContent() {
    var tabcontent = document.getElementsByClassName('tabcontent');
    for (var i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = 'none';
    }
}

function deactivateActiveTabs() {
    var tablinks = document.getElementsByClassName('tablinks');
    for (var i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(' active', '');
    }
}

function displayDefaultTab(modalID) {
    var tab, tabContent;

    hideModalTabContent();
    deactivateActiveTabs();

    if (modalID === "bug-modal") {
        tab = document.getElementById("bug-report-tab");
        tab.className += " active";
        tabContent = document.getElementById("bug-report");
        tabContent.style.display = "block";
    } else {
        tab = document.getElementById("api-tab");
        tab.className += " active";
        tabContent = document.getElementById("api");
        tabContent.style.display = "block";
    }
}

function toggleModal(modalID) {
    var modal = document.getElementById(modalID);
    if (typeof modal === 'undefined' || modal === null) {
        return;
    }
    if (modal.style.display !== 'block') {
        modal.style.display = 'block';
    } else {
        modal.style.display = 'none';
    }
    displayDefaultTab(modalID);
}

function openTab(event, tabName) {
    hideModalTabContent();
    deactivateActiveTabs();

    document.getElementById(tabName).style.display = 'block';
    event.currentTarget.className += ' active';
}