let endStateThingy = ()=>{
    let msg = document.querySelector(".endState");
    let words = msg.innerHTML.trim().split(" ");
    let newContent = words.map(word => 
        word.split("").map((letter, letterIndex, arr) => 
            `<span class="${letterIndex === arr.length - 1 ? "wordEnd" : ""}">${letter}</span>`
        ).join("")
    ).join(" ");    

    msg.innerHTML = newContent;
    console.log(newContent)
}

endStateThingy()