import { populateTree } from "./populateHelpers.js";

if (window.treeInfos){
    populateTree(window.treeInfos)
    setTimeout(()=>{
        const leaveBtn = document.querySelector("#leave-btn-tree");
        const readyBtn = document.querySelector("#ready-btn");
        const titleTree = document.querySelector("#tournament-history-title");
        if (titleTree) {
            titleTree.innerText = "Tournament Result";
            // titleTree.parentElement.classList.add('text-center');
            titleTree.parentElement.classList.remove('justify-content-between');
            titleTree.parentElement.classList.add('justify-content-center');
            titleTree.style.fontWeight = 'bold';
            titleTree.style.fontSize = '2.5rem';
        }
        if (leaveBtn) {
            leaveBtn.innerText = "Go back"
            leaveBtn.removeAttribute('data-route');
            leaveBtn.onclick = function() {
                history.back();
            }
        }
        if (readyBtn)
            readyBtn.remove()
    }, 0)

}