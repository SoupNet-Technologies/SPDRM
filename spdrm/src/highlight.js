// highlight module — recovered from the deployed spdrm.com snapshot
// (modules/highlight.js). A conservative regex syntax highlighter for
// <code class="language-php"> and <code class="language-js"> blocks.
// Colors come from the .code-* classes in style.css.
// Enable with "modules": ["highlight"], then call highlight("js") / highlight("php")
// after your content renders.

const patternPHP = {
    'color': /#([0-9a-fA-F]{3}){1,2}\b/g,
    'variable': /\$[a-zA-Z_\x80-\xff][a-zA-Z0-9_\x80-\xff]*/g,
    'number': /\b-?(?:0x[\da-f]+|\d*\.?\d+(?:e-?\d+)?)\b/gi,
    'function': /[a-z0-9_]+(?=\()/gi,
    'boolean': /\b(?:true|false|null)\b/g,
    'constant': /\b[A-Z_][A-Z0-9_]*\b/g,
    'comment': /\/\/.*|\/\*[^]*?\*\//g,
};
const patternJS = {
    'color': /#([0-9a-fA-F]{3}){1,2}\b/g,
    'variable': /[a-zA-Z_$][0-9a-zA-Z_$]*/g,
    'number': /\b-?(?:0x[\da-f]+|\d*\.?\d+(?:e-?\d+)?)\b/gi,
    'function': /[a-z_$][a-zA-Z0-9_$]*(?=\()/gi,
    'boolean': /\b(?:true|false|null)\b/g,
    'constant': /\b[A-Z_][A-Z0-9_]*\b/g,
    'comment': /\/\/.*|\/\*[^]*?\*\//g,
};
function syntaxer(lang, code) {
    switch (lang) {
        case "php":
            for (let syntax in patternPHP) {
                code = code.replace(patternPHP[syntax], `<span class="code-${syntax}">$&</span>`);
            }
            break;
        case "js":
            for (let syntax in patternJS) {
                code = code.replace(patternJS[syntax], `<span class="code-${syntax}">$&</span>`);
            }
            break;
        default:
            break;
    }
    return code;
}
function highlight(lang = "php") {
    document.querySelectorAll('code').forEach(codeElement => {
        if (codeElement.classList.contains(("language-" + lang))) {
            codeElement.innerHTML = syntaxer(lang, codeElement.innerHTML);
        }
    });
}
