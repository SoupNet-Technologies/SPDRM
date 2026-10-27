function loadsynth() {
    const synth = new Synthesizer();
    let fieldtest = document.createElement("fieldset");
    fieldtest.innerHTML = "<legend>Tests</legend>";
    let modseq = document.createElement("button");
    modseq.innerHTML = "Mod Seq";
    modseq.onclick = () => {
        seqGui();
    };
    let freqplay = document.createElement("button");
    freqplay.innerHTML = "Play Freq";
    freqplay.onclick = () => {
        synth.playFreq(440, 100);
    };
    let noteplay = document.createElement("button");
    noteplay.innerHTML = "Play Note";
    noteplay.onclick = () => {
        synth.playNote(69, 100);
    };
    let seqplay = document.createElement("button");
    seqplay.innerHTML = "Play Seq";
    seqplay.onclick = () => {
        const sequence = [
            { time: 0, note: 69, duration: 0.25 },
            { time: 0.25, note: 67, duration: 0.25 },
            { time: 0.5, note: 65, duration: 0.59 },
            { time: 1, note: 67, duration: 0.5 },
            { time: 1.5, note: 69, duration: 0.5 },
            { time: 2, note: 65, duration: 0.5 },
            { time: 2.5, note: 67, duration: 0.5 },
            { time: 3, note: 64, duration: 0.5 },
            { time: 3.5, note: 65, duration: 0.5 },
            { time: 4, note: 62, duration: 2 },
            { time: 5, note: 0, duration: 0 },
            { time: 6, note: 21, duration: 3 },
            { time: 6, note: 33, duration: 3 },
            { time: 7, note: 0, duration: 0 },
            { time: 8, note: 0, duration: 0 },
            { time: 9, note: 0, duration: 0 },
            { time: 10, note: 0, duration: 0 },
            { time: 11, note: 0, duration: 0 },
            { time: 12, note: 0, duration: 0 },
            { time: 13, note: 0, duration: 0 },
            { time: 14, note: 0, duration: 0 },
            { time: 15, note: 0, duration: 0 },
        ];

        synth.playSequence(sequence, 150);
    };

    fieldtest.appendChild(freqplay);
    fieldtest.appendChild(noteplay);
    fieldtest.appendChild(seqplay);
    fieldtest.appendChild(modseq);

    let fieldadsr = document.createElement("fieldset");
    fieldadsr.innerHTML = "<legend>ADSR</legend>";
    let adsra = document.createElement("input");
    adsra.setAttribute("type", "range");
    adsra.defaultValue = synth.attack * 100;
    adsra.max = 20;
    adsra.oninput = () => {
        synth.attack = adsra.value / 100;
    };
    let adsrd = document.createElement("input");
    adsrd.setAttribute("type", "range");
    adsrd.defaultValue = synth.decay * 100;
    //adsrd.max = 80;
    adsrd.oninput = () => {
        synth.decay = adsrd.value / 100;
    };
    let adsrs = document.createElement("input");
    adsrs.setAttribute("type", "range");
    adsrs.defaultValue = synth.sustain * 100;
    adsrs.max = 70;
    adsrs.oninput = () => {
        synth.sustain = adsrs.value / 100;
    };
    let adsrr = document.createElement("input");
    adsrr.setAttribute("type", "range");
    adsrr.defaultValue = synth.release * 100;
    //adsrr.max = 20;
    adsrr.oninput = () => {
        synth.release = adsrr.value / 100;
    };

    fieldadsr.appendChild(adsra);
    fieldadsr.appendChild(adsrd);
    fieldadsr.appendChild(adsrs);
    fieldadsr.appendChild(adsrr);

    var fieldfilter = document.createElement("fieldset");
    fieldfilter.innerHTML = "<legend>Filter</legend>";
    let filtercutoff = document.createElement("input");
    filtercutoff.setAttribute("type", "range");
    filtercutoff.min = 1000;
    filtercutoff.max = 22000;
    filtercutoff.defaultValue = synth.cutoff;
    //adsrd.max = 80;
    filtercutoff.oninput = () => {
        synth.cutoff = filtercutoff.value;
    };
    let filterresonance = document.createElement("input");
    filterresonance.setAttribute("type", "range");
    filterresonance.max = 1000;
    filterresonance.defaultValue = synth.resonance;
    //adsrd.max = 80;
    filterresonance.oninput = () => {
        synth.resonance = filterresonance.value;
    };
    fieldfilter.appendChild(filtercutoff);
    fieldfilter.appendChild(filterresonance);
    let fieldseq = document.createElement("fieldset");
    fieldseq.innerHTML = "<legend>Sequencer</legend><p>Time Grid</p>";
    let fieldseqctrl = document.createElement("fieldset");
    fieldseqctrl.innerHTML = "<legend>Controls</legend>";
    let fscplay = document.createElement("button");
    fscplay.innerText = "Play";
    let fscstop = document.createElement("button");
    fscstop.innerText = "Stop";
    let fscbpminp = document.createElement("input");
    fscbpminp.setAttribute("type", "text");
    fscbpminp.setAttribute("maxLength", 3);
    fscbpminp.setAttribute("pattern", "[\x30-\x39]{1,3}");
    fscbpminp.style = "width: 6vmin; margin-left: 2vmin";
    fscbpminp.value = "150";
    let fscsetbpm = document.createElement("button");
    fscsetbpm.innerText = "Set";

    fieldseqctrl.appendChild(fscplay);
    fieldseqctrl.appendChild(fscstop);
    fieldseqctrl.appendChild(fscbpminp);
    fieldseqctrl.appendChild(fscsetbpm);
    fieldseq.appendChild(fieldseqctrl);
    main.appendChild(fieldadsr);
    createPianoKeyboard(synth);
    let synmand = document.createElement("div");
    synmand.innerHTML = mandelbrotSVG;
    main.appendChild(synmand);
    generateAd();
    main.appendChild(fieldfilter);
    main.appendChild(fieldtest);
    createSequencer(fieldseq);
    main.appendChild(fieldseq);
}
class Synthesizer {
    constructor() {
        this.audioContext = new AudioContext();
        this.audioContext.gain = 0.5;
        this.effectsBus = this.audioContext.createGain();
        this.effectsBus.gain.value = 1;
        this.oscillators = [];
        this.sequencer = [];
        this.attack = 0.01;
        this.decay = 0.1;
        this.sustain = 0.5;
        this.release = 0.3;
        this.cutoff = 20000; //(audioContext.sampleRate/2) - 20000
        this.resonance = 0; // 0-1000
    }

    playFreq(frequency, duration) {
        const oscillator = this.audioContext.createOscillator();
        oscillator.frequency.value = frequency;
        oscillator.connect(this.audioContext.destination);

        oscillator.start();

        this.oscillators.push(oscillator);

        setTimeout(() => {
            oscillator.stop();
        }, duration);
    }
    playNote(note, duration) {
        const oscillator = this.audioContext.createOscillator();
        oscillator.frequency.value = this.noteToFrequency(note);

        const filter = this.audioContext.createBiquadFilter();
        filter.type = "lowpass";
        filter.frequency.value = this.cutoff;
        filter.Q.value = this.resonance;
        oscillator.connect(filter);
        filter.connect(this.effectsBus);
        this.adsr = this.audioContext.createGain();
        this.adsr.gain.value = 0;
        oscillator.connect(this.adsr);
        this.adsr.connect(this.audioContext.destination);
        oscillator.start();
        let attack = this.attack - 0.1;
        let release = this.release - 0.1;
        this.adsr.gain.linearRampToValueAtTime(
            1,
            this.audioContext.currentTime + attack
        );
        this.adsr.gain.linearRampToValueAtTime(
            this.sustain,
            this.audioContext.currentTime + attack + this.decay
        );
        setTimeout(() => {
            this.adsr.gain.linearRampToValueAtTime(
                0,
                this.audioContext.currentTime + release
            );
            oscillator.stop();
        }, duration);
        this.oscillators.push(oscillator);
    }

    noteToFrequency(note) {
        return Math.pow(2, (note - 69) / 12) * 440;
    }

    playSequence(sequence, tempo) {
        this.sequencer = sequence;
        let interval = 60000 / tempo; // interval in ms

        this.sequencer.forEach((note) => {
            setTimeout(() => {
                if (Number.isInteger(note.time)) {
                    seqGui(note.time + 1);
                }
                this.playNote(note.note, getNoteDuration(tempo, note.duration));

                //this.playNote(note.note, synth.release * 100);
            }, note.time * interval);
        });
    }

    stop() {
        this.oscillators.forEach((oscillator) => {
            oscillator.stop();
        });
    }
}
function createPianoKeyboard(synth) {
    let keys = [
        "C",
        "C#",
        "D",
        "D#",
        "E",
        "F",
        "F#",
        "G",
        "G#",
        "A",
        "A#",
        "B",
        "C",
        "C#",
        "D",
        "D#",
        "E",
        "F",
        "F#",
        "G",
        "G#",
        "A",
        "A#",
        "B",
        "C",
    ];
    let cont = document.createElement("fieldset");
    let contleg = document.createElement("legend");
    contleg.innerHTML = "Keys";
    cont.appendChild(contleg);
    for (let i = 0; i < keys.length; i++) {
        let button = document.createElement("button");
        button.style =
            "font-size: 0.2vmin; display: flex; flex-direction: column; align-items: center;";
        button.innerText = keys[i];
        if (keys[i].indexOf("#") !== -1) {
            button.className = "black";
            button.style.color = "grey";
        } else {
            button.className = "white";
        }
        button.addEventListener("click", () => {
            synth.playNote(48 + i, 200);
        });
        cont.className = "pianocont";
        cont.appendChild(button);
    }
    main.appendChild(cont);
}
function createSequencer(field) {
    // create the fieldset element
    const fieldset = document.createElement("fieldset");
    fieldset.innerHTML = "<legend>Grid <button>Reset</button></legend>";
    fieldset.style.display = "grid";
    fieldset.style.gridTemplateColumns = "repeat(8, 1fr)";
    fieldset.style.padding = "0";
    //fieldset.classList.add("seqfield");

    // create the grid
    for (let i = 0; i < 2; i++) {
        for (let j = 0; j < 8; j++) {
            if (i == 0) {
                var t = j + 1;
            } else {
                var t = j + 9;
            }
            const div = document.createElement("div");
            div.style = "border: 1px solid red; color: rgba(255,255,255,0.2);";
            seqRefresh(div);
            div.classList.add("seqdiv");
            div.name = t;
            div.textContent = `${t}`;
            div.innerHTML += "<br><button style='padding:0'>&#127925</button>";
            div.addEventListener("click", () => {
                seqGui(div.name);
                /*
                seqRefresh(div);*/
            });
            fieldset.appendChild(div);
        }
    }
    field.appendChild(fieldset);
}

function seqRefresh(div) {
    if (div.classList.contains("selected")) {
        div.style = "border: 1px solid white; background: black; color: red";
    }
}
function seqGui(s) {
    const ddivs = document.getElementsByTagName("div");
    const divs = [];
    for (let d in ddivs) {
        if (Number(d) >= 0) {
            let dd = ddivs[Number(d)];
            if (dd.classList.contains("seqdiv")) {
                divs.push(dd);
            }
        }
    }
    divs.forEach((d) => {
        //d.classList.remove("selected");
        if (d.name == s) {
            d.style =
                "border: 1px solid lightgrey; color: rgba(255,255,255,0.6);";
        } else {
            d.style = "border: 1px solid red; color: rgba(255,255,255,0.2);";
        }
    });
}

function getNoteDuration(bpm, noteLength) {
    const beatDuration = 60000 / bpm;
    return beatDuration * noteLength;
}
