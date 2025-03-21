function endStateThingy(event) {
        const msg = document.querySelector(".endState");
        const words = msg.innerHTML.trim().split(" ");
        const newContent = words.map(word => 
            word.split("").map((letter, letterIndex, arr) => 
                `<span class="${letterIndex === arr.length - 1 ? "wordEnd" : ""}">${letter}</span>`
            ).join("")
        ).join(" ");
    
        msg.innerHTML = newContent;
        console.log(newContent)
}


endStateThingy();