// cards module — the fancy card variant, recovered from the deployed spdrm.com
// snapshot (modules/cards.js). Base createCard lives in utils.js; this only adds
// the decorative variant. Enable with "modules": ["cards"].

createCard.fancy = function (title, post, more) {
    let card = document.createElement("div");
    card.className = "card fancy";
    if (title) {
        let header = document.createElement("div");
        header.className = "card-header";
        let titleElement = document.createElement("h3");
        titleElement.className = "card-title";
        titleElement.innerHTML = title;
        header.appendChild(titleElement);
        card.appendChild(header);
    }
    if (post) {
        let postElement = document.createElement("p");
        postElement.className = "card-post";
        postElement.innerHTML = post;
        card.appendChild(postElement);
    }
    if (more) {
        card.appendChild(more);
    }
    main.appendChild(card);
};
