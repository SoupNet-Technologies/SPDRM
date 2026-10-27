// carousel module — recovered from the deployed spdrm.com snapshot
// (modules/carousel.js). A horizontally scrolling, scroll-snapped image strip
// where every image opens in the zoom modal. Enable with "modules": ["carousel"].

function createCarousel(images) {
    if (!images || !images.length) {
        images = [
            {
                title: "One",
                src: "assets/header.svg",
            },
            {
                title: "Two",
                src: "assets/nav.svg",
            },
        ];
    }
    let carousel = document.createElement("div");
    carousel.className = "carousel";

    images.forEach(function (image) {
        let imageDiv = document.createElement("div");
        imageDiv.className = "image-div";

        let imgElement = document.createElement("img");
        imgElement.src = image.src;
        imgElement.alt = image.title;
        imgElement.className = "carousel-image";
        imgElement.addEventListener("click", function () {
            zoomimg(imgElement);
        });
        imageDiv.appendChild(imgElement);
        carousel.appendChild(imageDiv);
    });

    main.appendChild(carousel);
}

createCard.carousel = function (title, post, images) {
    if (title) {
        let header = document.createElement("div");
        header.className = "card-header";
        let titleElement = document.createElement("h3");
        titleElement.className = "card-title";
        titleElement.innerHTML = title;
        main.appendChild(header);
    }
    if (post) {
        let postElement = document.createElement("p");
        postElement.className = "card-post";
        postElement.innerHTML = post;
        main.appendChild(postElement);
    }
    createCarousel(images);
};
