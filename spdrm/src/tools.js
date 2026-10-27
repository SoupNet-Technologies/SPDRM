function loadtools() {
    let toolsarr = [
        {
            btntxt: "English to Pig Latin",
            btnclick: () => {
                move("piglatin");
            },
        },
        {
            btntxt: "Video Shuffler",
            btnclick: () => {
                move("vidshuffle");
            },
        },
    ];
    toolsarr.forEach((e) => {
        let btn = document.createElement("button");
        btn.innerText = e.btntxt;
        btn.onclick = e.btnclick;
        createCard(e.btntxt, "", btn);
        //main.appendChild(btn);
    });
}
function isPalindrome(str) {
    str = str.replace(/[^a-z0-9]/gi, "").toLowerCase();
    let reversed = str.split("").reverse().join("");
    return reversed === str;
}
const paldefaults = [
    "Ten animals I slam in a net",
    "Do geese see God?",
    "A Santa at NASA",
    "Dogma: I am God",
    "No devil lived on",
    "Too bad I hid a boot",
    "Yo, Banana Boy!",
    "Madam, in Eden I'm Adam",
    "Go deliver a dare, evil is afoot",
    "No lemon, no melon",
    "Do nine men interpret? Nine men, I nod",
    "Doc, note: I dissent. A fast never prevents a fatness. I diet on cod.",
    "Poor Dan is in a droop.",
    "Never odd or even.",
    "Mr. Owl ate my metal worm.",
    "Murder, for a jar of red rum",
    "Was it a rat I saw",
    "Senile felines",
    "Too hot to hoot",
    "Gateman sees name, garageman sees nametag",
    "Kayak",
    "Rise to vote, sir",
    "Tokyo, no pot",
    "Step on no pets",
    "Drab as a fool, aloof as a bard",
    "Niagara, o roar again",
    "A man, a plan, a canal, Panama",
    "Ma has a ham",
    "No sir, away, anxiety",
    "Was it a car or a cat I saw?",
    "Able was I ere I saw Elba",
    "Nurses run",
    "Lonely Tylenol",
    "Live, evil",
    "Sums are not set as a test on Erasmus",
    "No, it is op",
    "God saw I was dog",
    "Never odd or a eve",
    "Rats live on no evil star",
    "Won't lovers revolt now?",
    "Rise to vote, sirs",
    "Dammit, I'm mad",
    "A nut for a jar of tuna",
    "Egad, a base tone denotes a bad age",
    "Red rum, sir, is murder",
    "Was it a cat I saw?",
    "Race fast, safe car",
    "Too bad I hid a booty",
    "Yawn, o brave new world",
    "Go hang a salami, I'm a lasagna hog",
    "A tin mug for a jar of gum",
    "Evil olive",
];
function getAverage(numbers) {
    if (!Array.isArray(numbers)) {
        return null;
    }
    if (numbers.length === 0) {
        return 0;
    }
    let sum = 0;
    for (const num of numbers) {
        sum += num;
    }
    return sum / numbers.length;
}

function getValuesFromCSVFile(file) {
    let reader = new FileReader();
    reader.onload = function () {
        let fileContents = reader.result;
        let rows = fileContents.split("\n");
        let numbers = [];
        for (let row of rows) {
            let columns = row.split(",");
            for (let column of columns) {
                numbers.push(parseInt(column, 10));
            }
        }
        return numbers;
    };
    reader.readAsText(file);
}
function loadkf() {
    let kffield = document.createElement("div");
    //kffield.innerHTML = "<legend>KF</legend>";
    kffield.style =
        "display: grid; grid-template-columns: repeat(4, 1fr); grid-gap: 3vmin";

    let kfinpstyle = "grid-column: 1 / span 3";
    let kfinp = [["Time"], ["Frames"], ["FPS"]];
    for (let i = 0; i < 3; i++) {
        kfinp[i][10] = document.createElement("input");
        kfinp[i][10].style = kfinpstyle;
        kfinp[i][10].setAttribute("type", "number");
        kfinp[i][20] = document.createElement("button");
        kfinp[i][20].innerText = kfinp[i][0];
        kfinp[i][20].onclick = (e) => {
            if (
                /^\d+$/.test(kfinp[1][10].value) &&
                /^\d+$/.test(kfinp[2][10].value) &&
                e.srcElement.innerText == "Time"
            ) {
                // get time
                console.log("time work");
                let p = Number(kfinp[1][10].value) / Number(kfinp[2][10].value);
                kfinp[0][10].value = p;
            } else if (
                /^\d+$/.test(kfinp[0][10].value) &&
                /^\d+$/.test(kfinp[2][10].value) &&
                e.srcElement.innerText == "Frames"
            ) {
                // get time
                console.log("frames work");
                let p = Number(kfinp[0][10].value) * Number(kfinp[2][10].value);
                kfinp[1][10].value = p;
            } else if (
                /^\d+$/.test(kfinp[0][10].value) &&
                /^\d+$/.test(kfinp[1][10].value) &&
                e.srcElement.innerText == "FPS"
            ) {
                // get fps
                console.log("fps work");
                let p = Number(kfinp[1][10].value) / Number(kfinp[0][10].value);
                kfinp[2][10].value = p;
            }
        };
        kffield.appendChild(kfinp[i][10]);
        kffield.appendChild(kfinp[i][20]);
    }
    createCard(
        "",
        "<details><summary>Read Me</summary>With Keyframer, you can easily and quickly convert between different time and frame rate units without having to do any manual calculations. Give it a try and see how much time and effort it can save you on your video projects.<ul><li>Input the values you know in two of the fields. For example, if you know the number of frames and the frame rate, enter those values in the corresponding fields.</li><li>Click the button next to the empty field to calculate the missing value. Keyframer will automatically fill in the empty field with the calculated value.</li><li>You can repeat this process as many times as needed to convert between frames, seconds, and FPS.</li></ul><br><b>Time</b> is a numeric value in seconds, 0.5 would be 500ms. <b>Frames</b> is a numeric value representing the total number of frames. <b>FPS</b> is a numeric value representing how many frames there are in a second.<br><br>That's it!<br></details>"
    );
    createCard("KF", "<sub>fill in any two values</br>", kffield);
}
async function imageToAscii(fileInput, scale, textarea) {
    const reader = new FileReader();
    reader.onload = function () {
        var img = new Image();
        img.src = reader.result;
        console.log(textarea);
        img.onload = function () {
            var canvas = document.createElement("canvas");
            var context = canvas.getContext("2d");
            canvas.width = img.width / scale;
            canvas.height = img.height / scale;
            context.drawImage(img, 0, 0, canvas.width, canvas.height);
            var imageData = context.getImageData(
                0,
                0,
                canvas.width,
                canvas.height
            );
            var data = imageData.data;
            var asciiArt = "";
            for (var y = 0; y < canvas.height; y++) {
                var line = "";

                for (var x = 0; x < canvas.width; x++) {
                    var red = data[(canvas.width * y + x) * 4];
                    var green = data[(canvas.width * y + x) * 4 + 1];
                    var blue = data[(canvas.width * y + x) * 4 + 2];

                    var character = getCharacterForColor(red, green, blue);

                    line += character;
                }
                asciiArt += line + "\n";
            }
            console.log(asciiArt);
            textarea.value = asciiArt;
            //return asciiArt;
        };
    };
    reader.readAsDataURL(fileInput.files[0]);
}
function getCharacterForColor(red, green, blue) {
    let brightness = (red + green + blue) / 3;
    let character = " ";
    if (brightness >= 240) {
        character = " ";
    } else if (brightness >= 220) {
        character = ".";
    } else if (brightness >= 200) {
        character = ":";
    } else if (brightness >= 180) {
        character = "-";
    } else if (brightness >= 160) {
        character = "=";
    } else if (brightness >= 140) {
        character = "+";
    } else if (brightness >= 120) {
        character = "*";
    } else if (brightness >= 100) {
        character = "%";
    } else if (brightness >= 80) {
        character = "&";
    } else if (brightness >= 40) {
        character = "€";
    } else if (brightness >= 20) {
        character = "@";
    } else if (brightness >= 5) {
        character = "S";
    } else {
        character = " ";
    }

    return character;
}
function getCharacterForColorOld(red, green, blue) {
    let brightness = (red + green + blue) / 3;
    let character = " ";
    if (brightness >= 240) {
        character = " ";
    } else if (brightness >= 200) {
        character = ".";
    } else if (brightness >= 160) {
        character = "*";
    } else if (brightness >= 120) {
        character = ":";
    } else if (brightness >= 80) {
        character = "o";
    } else if (brightness >= 40) {
        character = "&";
    } else {
        character = "#";
    }

    return character;
}
function translateToPigLatin(sentence) {
    let words = String(sentence).split(" ");
    let pigLatinSentence = "";
    for (let i = 0; i < words.length; i++) {
        let word = words[i];
        let isCapitalized = word[0] === word[0].toUpperCase();
        if (isCapitalized) {
            word = word.toLowerCase();
        }
        let firstLetter = word[0];
        let restOfWord = word.substring(1);
        let pigLatinWord = restOfWord + firstLetter + "ay";
        if (isCapitalized) {
            pigLatinWord =
                pigLatinWord[0].toUpperCase() + pigLatinWord.substring(1);
        }
        pigLatinSentence += pigLatinWord + " ";
    }
    return pigLatinSentence;
}

function shuffleVideo(fileInputElement) {
    // Check if file is a video
    if (!fileInputElement.files[0].type.includes("video")) {
        return false;
    }
    console.log("pass check video");
    // Check if video is under 5 minutes
    if (fileInputElement.files[0].duration > 5 * 60 * 1000) {
        return false;
    }
    console.log("pass check duration");

    // Create array of all frames from the video
    let frames = [];
    let video = document.createElement("video");
    video.src = URL.createObjectURL(fileInputElement.files[0]);
    console.log("canvas init");

    video.addEventListener("loadeddata", function () {
        let canvas = document.createElement("canvas");
        console.log("canvas loaded");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        let ctx = canvas.getContext("2d");

        let frameRate = video.duration / video.videoWidth;
        let currentTime = 0;
        let index = 0;

        while (currentTime < video.duration) {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            frames[index] = ctx.getImageData(0, 0, canvas.width, canvas.height);
            currentTime += frameRate;
            index++;
        }
        console.log("array created");
    });

    // Shuffle array of frames
    let currentIndex = frames.length;
    let tempValue;
    let randomIndex;

    while (currentIndex !== 0) {
        console.log(currentIndex);
        randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex--;

        tempValue = frames[currentIndex];
        frames[currentIndex] = frames[randomIndex];
        frames[randomIndex] = tempValue;
    }
    console.log("array shuffled");

    // Turn array of frames back into video
    let newVideo = document.createElement("video");
    newVideo.width = video.videoWidth;
    newVideo.height = video.videoHeight;

    let blob = new Blob([frames], { type: "video/webm" });
    newVideo.src = URL.createObjectURL(blob);

    // Add new video to DOM
    main.appendChild(newVideo);
    console.log("done");
}
class metadataEditor {
    constructor(fileInput) {
        this.fileInput = fileInput;
        this.initEditor();
    }

    initEditor() {
        let downloadButton = document.createElement("button");
        downloadButton.innerHTML = "Download";
        downloadButton.addEventListener("click", () => {
            this.downloadImage();
        });
        main.appendChild(downloadButton);
    }

    downloadImage() {
        let reader = new FileReader();
        reader.onloadend = (evt) => {
            let imageData = evt.target.result;
            let editedImageData = this.editMetadata(imageData);
            this.saveImage(editedImageData);
        };
        reader.readAsDataURL(this.fileInput.files[0]);
    }

    editMetadata(imageData) {
        console.log("metaa");
        // Edit the metadata here
        return imageData;
    }

    saveImage(editedImageData) {
        let a = document.createElement("a");
        a.href = editedImageData;
        a.download = "image.png";
        main.appendChild(a);
        a.click();
        a.remove();
    }
}
