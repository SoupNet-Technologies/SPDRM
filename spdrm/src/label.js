// label module — recovered from the deployed spdrm.com snapshot
// (modules/label.js). A small bold caption, usually placed between cards.
// Enable with "modules": ["label"].

function createLabel(text, size = "1.2rem") {
    let label = document.createElement("div");
    label.className = "label";

    label.innerHTML = "<p style='font-size:" + size + ";'><b>" + text + "</b></p>";

    main.appendChild(label);
}
