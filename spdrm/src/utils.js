function html(strings, ...values) {
  let out = '';
  const nodes = [];
  for (let i = 0; i < strings.length; i++) {
    out += strings[i];
    if (i < values.length) {
      const v = values[i];
      if (v === null || v === undefined) continue;
      if (Array.isArray(v)) {
        for (const item of v) {
          if (item instanceof Node) {
            nodes.push(item);
            out += `<!--ph${nodes.length - 1}-->`;
          } else {
            out += String(item).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
          }
        }
      } else if (v instanceof Node) {
        nodes.push(v);
        out += `<!--ph${nodes.length - 1}-->`;
      } else {
        out += String(v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
      }
    }
  }
  const el = document.createElement('div');
  el.innerHTML = out;
  if (nodes.length) {
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_COMMENT, null, false);
    while (walker.nextNode()) {
      const match = walker.currentNode.nodeValue.match(/^ph(\d+)$/);
      if (match) {
        walker.currentNode.parentNode.replaceChild(nodes[+match[1]], walker.currentNode);
      }
    }
  }
  if (el.children.length === 1) return el.children[0];
  const frag = document.createDocumentFragment();
  frag.append(...Array.from(el.children));
  return frag;
}

function initmain(title) {
    main.innerHTML = "";
    main.append(html`
      <div class="mainhead">
        <h2 style="margin:0;padding:0;position:absolute;bottom:0;left:0">${title}</h2>
      </div>
    `);
}
function generateAd() {
    if (!adUrls || adUrls.length === 0) return;
    randomAd = adUrls[Math.floor(Math.random() * adUrls.length)];
    if (!randomAd) return;
    if (randomAd.url) {
        main.append(html`<br><a href="${randomAd.url}" target="_blank"><img src="${randomAd.src}" style="height:30px;padding:0;margin:0;margin-bottom:6vmin"></a>`);
    } else {
        main.append(html`<br><img src="${randomAd.src}" style="height:30px;padding:0;margin:0;margin-bottom:6vmin">`);
    }
}
function createCard(title, post, more) {
    let card = document.createElement("div");
    card.className = "card";
    if (title) {
        card.append(html`<div class="card-header"><h3 class="card-title">${title}</h3></div>`);
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
}
function appendP(parent, text) {
    parent.append(html`<p style="text-align:center;margin-top:0"><sup>${text}</sup></p>`);
}
function zoomimg(s) {
    const src = s.src || (Array.isArray(s) ? s[0] : "");
    const title = s.title || (Array.isArray(s) ? s[1] : "");
    dialog.innerHTML = `<img src="${src}" onclick="window.dialog.close()"><h5>${title}</h5>`;
    dialog.showModal();
}
function generateDialog(title, message) {
    dialog.innerHTML = `<button style="" onclick="window.dialog.close()">Exit</button><br><h2>${message}</h2><br><h5>${title}</h5>`;
    dialog.style = "min-width: 60%";
    dialog.showModal();
}
function randimg() {
    let width = main.offsetWidth;
    let height = main.offsetHeight - 4;

    let pixels = new Uint8ClampedArray(width * height * 4);

    let d = 0;
    for (let i = 0; i < pixels.length; i++) {
        let rnd = Math.floor(Math.random() * 256);
        let rndwt = Math.floor(Math.random() * 185) + 70;
        d++;
        switch (d) {
            case 1: // r
                pixels[i] = rnd;
                break;
            case 2: // g
                pixels[i] = rnd;
                break;
            case 3: // b
                pixels[i] = rnd;
                break;
            default: // y
                pixels[i] = rnd;
                d = 0;
                break;
        }
    }

    let image = new ImageData(pixels, width, height);
    let canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    main.append(canvas);
    let context = canvas.getContext("2d");
    context.putImageData(image, 0, 0);
}
function devclick() {
    aside.innerHTML += "<p>Dev</p>";
    let buttons = [
        {
            text: "Open Modal",
            action: () => generateDialog("hello", "it works"),
        },
        { text: "Test Api", action: () => testapi() },
    ];

    buttons.forEach((b) => {
        let devbutton = document.createElement("button");
        devbutton.innerHTML = b.text;
        devbutton.onclick = b.action;
        aside.append(devbutton);
    });
}
function testapi() {
    $.ajax({
        url: "path/to/php/script.php",
        type: "get",
        dataType: "json",
        success: function (data) {
            // Parse the JSON string
            var csvData = JSON.parse(data);

            // Access the values in the array
            console.log(csvData["column1"]);
            console.log(csvData["column2"]);
            console.log(csvData["column3"]);
        },
    });
    /*const js_var = "some value";
    fetch("/api/save_to_file.php", {
        method: "POST",
        body: JSON.stringify({
            js_var: js_var,
        }),
    })
        .then((response) => response.json())
        .then((data) => {
            console.log(data);
        });*/
}
function isValidEmail(email) {
    const regex =
        /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return regex.test(email);
}
function maybeAnimate() {
    var random = Math.random();
    if (random < 0.5) {
        var element = document.querySelector(".blurry-vision");
        element.classList.add("animating");
        setTimeout(function () {
            element.classList.remove("animating");
        }, 1000);
    }
}

const mandelbrotSVG =
    '<svg width="280" height="280"><rect x="0" y="0" width="200" height="200" fill="black" /><g transform="translate(140,140) scale(69,69)"><path d="M-1,0C-1,0.6-0.6,1,0,1C0.6,1,1,0.6,1,0C1,-0.6,0.6,-1,0,-1C-0.6,-1,-1,-0.6,-1,0Z" fill="rgba(255,0,230,0.8)" /><g><circle cx="-1" cy="0" r="1" fill="none" stroke="#fff" stroke-width="0.01" /><circle cx="1" cy="0" r="1" fill="none" stroke="#fff" stroke-width="0.01" /></g><g><circle cx="0" cy="1" r="1" fill="rgba(255,0,0,0.8)" stroke="#fff" stroke-width="0.01" /><circle cx="0" cy="-1" r="1" fill="rgba(255,0,200,0.8)" stroke="#fff" stroke-width="0.01" /></g><g><circle cx="0" cy="0" r="1" fill="none" stroke="#fff" stroke-width="0.01" /></g></g></svg>';

function createMandelbrotSVG(width, height, element, arr) {
    let svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", width);
    svg.setAttribute("height", height);
    svg.style = "transform: scale(" + arr[4].inprng.value + ") rotate(90deg)";
    for (let x = 0; x < width; x++) {
        for (let y = 0; y < height; y++) {
            const value = calculateMandelbrotValue(x, y, width, height, arr);
            const rect = document.createElementNS(
                "http://www.w3.org/2000/svg",
                "rect"
            );
            let colls = ["red", "blue", "orange", "purple", "green"];
            let cull = "rgb(255," + (255 - value) + ", 255)";
            rect.setAttribute("x", x);
            rect.setAttribute("y", y);
            rect.setAttribute("width", 1);
            rect.setAttribute("height", 1);
            rect.setAttribute("fill", cull);
            rect.setAttribute("stroke", "none");
            svg.appendChild(rect);
        }
    }
    element.innerHTML = "";
    element.appendChild(svg);
    //return svg;
}

function calculateMandelbrotValue(x, y, w, h, arr) {
    const scaleX = 4 / w;
    const scaleY = 4 / h;
    const cx = x * scaleX - 2;
    const cy = y * scaleY - 2;

    let zx = 0;
    let zy = 0;
    let MAX_ITERATIONS = arr[5].inputval;

    for (let i = 0; i < MAX_ITERATIONS; i++) {
        const zx2 = zx * zx - zy * zy + cx;
        const zy2 = 2 * zx * zy + cy;
        if (zx2 * zx2 + zy2 * zy2 > 4) {
            return i;
        }
        zx = zx2;
        zy = zy2;
    }
    return MAX_ITERATIONS;
}

