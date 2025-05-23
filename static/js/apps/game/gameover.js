function setAnimationDelay(el, multiplier) {
  el.style.animationDelay = `calc(0.1s * ${multiplier})`;
}

function endStateThingy() {
    let globalLetterIndex  = 0

    const msg = document.querySelector(".endState");
    if (!msg) return;

    const words = msg.innerText.trim().split(" ");
    msg.innerHTML = "";

    words.forEach((word, wordIndex) => {
    word.split("").forEach((letter, letterIndex, arr) => {
        const mySpan = document.createElement("span");

        if ((letterIndex == arr.length - 1)) {
            mySpan.classList.add("wordEnd");
        }

        mySpan.innerText = letter;
        setAnimationDelay(mySpan, globalLetterIndex + 1);
        globalLetterIndex++
        msg.appendChild(mySpan);
    });

    if (wordIndex < words.length - 1) {
        msg.appendChild(document.createTextNode(" "));
    }
    });
}

endStateThingy();