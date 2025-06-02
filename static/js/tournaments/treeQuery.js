import { populateTree } from "./populateHelpers.js";

if (window.treeInfos){
    populateTree(window.treeInfos)
    setTimeout(()=>{
        const leaveBtn = document.querySelector("#leave-btn-tree")
        const readyBtn = document.querySelector("#ready-btn")
        if (leaveBtn)
            leaveBtn.innerText = "Back to gamemodes"
        if (readyBtn)
            readyBtn.remove()
    }, 0)
}