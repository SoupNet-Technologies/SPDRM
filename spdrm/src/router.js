function move(s) {
  const route = routes[s] || routes.home;

  main.style.backgroundImage = "";

  if (route.is404) {
    route.render();
    moveurl(s);
    if (route.meta) loadmeta(...route.meta);
    return;
  }

  if (route.isAbyss) {
    main.innerHTML = "";
    randimg();
    moveurl(s);
    if (route.meta) loadmeta(...route.meta);
    return;
  }

  if (route.iframe) {
    main.innerHTML = `<iframe src='${route.iframe}' frameborder='0' style='height:99%; width:99%;'></iframe>`;
    moveurl(s);
    if (route.meta) loadmeta(...route.meta);
    return;
  }

  initmain(route.title || "");

  if (route.bgImage) {
    main.style = `background-image: url('${route.bgImage}'); background-repeat: no-repeat; background-attachment: fixed; background-size: cover; background-blend-mode: divide;`;
  }

  if (route.render) route.render();

  if (!route.noAd) generateAd();
  moveurl(s);
  if (route.meta) loadmeta(...route.meta);
}

function moveurl(s) {
    window.location.replace(s == "home" ? "#" : "#" + s);
  //_paq.push(['trackEvent', 'Menu', s]);
}

function loadmeta(title, desc, keywords) {
    document.title = title + siteData.seotitle;
    document
        .querySelector('meta[name="description"]')
        .setAttribute("content", desc);
    document
        .querySelector('meta[name="keywords"]')
        .setAttribute("content", keywords);
}

window.onload = () => {
    let url = new URL(window.location.href);
    loadnav();
    const hash = url.hash.slice(1) || "home";
    move(hash in routes ? hash : "home");
};
