import { populateTree } from "./populateHelpers.js";

if (window.treeInfos){
    populateTree(window.treeInfos)
    setTimeout(()=>{
        const btn = document.querySelector("#leave-btn-tree")
        if (btn)
            btn.innerText = "Back to gamemodes"
    }, 0)
}