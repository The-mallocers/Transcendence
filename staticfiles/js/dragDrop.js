import {updateRight} from "./render.js"

let oldDropAreaBg
let oldBgIsSet = false


const getComponentById = async () => {
    const response = await fetch(`/get-component/${currentDrag.id}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    });


    return await response.json()
}

export const dragoverHandler = (e) => {
    e.preventDefault();
    if (!oldBgIsSet) {
        oldDropAreaBg = e.target.style.background
        oldBgIsSet = true
    }
    e.target.style.background = 'lightblue';
}


export const dragleaveHandler = (e) => {
    e.preventDefault();

    e.target.style.background = oldDropAreaBg;

    oldBgIsSet = false
}

export const dropHandler = async (e) => {
    e.preventDefault();
    const result = await getComponentById(e);
    e.target.style.background = oldDropAreaBg;
    oldBgIsSet = false
    e.target.innerHTML = e.target.innerHTML + result.component.html
    currentDrag = undefined

    updateRight(currentClickedElement)
}

export const addDragEvents = (root) => {
    for (let i = 0; i < componentLib.children.length; i++) {
        componentLib.children[i].addEventListener('dragstart', (e) => {
            console.log(e.target)
            currentDrag = e.target
        })

        componentLib.children[i].addEventListener('dragend', (e) => {
            console.log("stoped")
        })
    }


    root.addEventListener('dragover', dragoverHandler)
    root.addEventListener('dragleave', dragleaveHandler)
    root.addEventListener('drop', dropHandler);
}


// export  { dragoverHandler, dragleaveHandler, dropHandler };