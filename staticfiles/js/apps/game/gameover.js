let endState = document.querySelector(".endState");
let words = endState.innerHTML.trim().split(" ");
let newContent = words.map(word => 
    word.split("").map((letter, letterIndex) => 
        `<span class="${letterIndex === word.length - 1 ? "wordEnd" : ""}">${letter}</span>`
    ).join("")
).join(" ");    

endState.innerHTML = newContent;
console.log(newContent)