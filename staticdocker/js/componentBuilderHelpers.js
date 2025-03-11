import {dragoverHandler, dragleaveHandler, dropHandler, addDragEvents} from "./dragDrop.js"
import {selectImg} from "./popup.js"
import {updateRight, addClassToAllDescendants} from "./render.js"
import {addEventToAllDescendants, addBasicEventsToPage} from "./basicEventManager.js"


const saveComponent = async (e) => {
    try {
        const response = await fetch("/save-component", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },

            body: JSON.stringify({html: root.innerHTML, name: componentName.value}),
        });
        const result = await response.json();
        console.log('Success:', result);
    } catch (error) {
        console.error('Error:', error);
    }
}


saveBtn.addEventListener("click", async (e) => {
    await saveComponent(e)
})


export const evaluateEmpty = () => {
    const childElements = root.querySelectorAll("*");

    for (let i = 0; i < childElements.length; i++) {
        if (!["img"].includes(childElements[i].tagName.toLowerCase())) {
            if (childElements[i].innerHTML.length == 0)
                childElements[i].classList.add("empty");
            else
                childElements[i].classList.remove("empty");
        }
    }
}

// let updateUrl = (atribute) =>{
//     let url = new URL(window.location);
//     url.searchParams.set('attr', atribute.toLowerCase());
//     window.history.pushState({ path: url.toString() }, '', url.toString());
// }


const createSubmenu = (context) => {

    const filteredJson = context
    const li = `
            ${
        Object.keys(filteredJson).map((key) => {
            const val = filteredJson[key];

            if (key !== "classnames" && typeof val === "object" && val !== null)
                return `<li class="dropstart">
                                <a class="dropdown-item dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" data-bs-auto-close="outside">
                                    ${key}
                                </a>
                            <ul class="dropdown-menu" data-bs-display="static">
                                ${createSubmenu(val)}
                            </ul>`
            else if (Array.isArray(val))
                return val.map((v) => `<li class="classnamesDropdowns" ><a class="dropdown-item lastDimention" href="#">${v}</a></li>`).join("");
            else
                return `<li><a class="dropdown-item lastDimention" href="#">${val}</a></li>`

        }).join("")
    }`;

    return li
}

export const buildClassesDropDown = (className) => {
    const filteredJson = contextClasses

    const dropDownElement = document.createElement("div");
    dropDownElement.classList.add("dropdown", "dropRoot");

    const dropDown = `
        <button id="classSelector" class="btn btn-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" data-bs-auto-close="outside" aria-expanded="false">
            ${className}
        </button>
        <ul id="classDrop"  class="dropdown-menu" data-bs-display="static" aria-labelledby="classSelector">
            ${createSubmenu(filteredJson)}
        </ul>
    `

    dropDownElement.innerHTML = dropDown;
    return dropDownElement;
}


window.changeTag = (e) => {
    console.log(e)

    console.log(currentClickedElement)

    const newElement = document.createElement(e.innerText);
    newElement.innerHTML = currentClickedElement.innerHTML;

    currentClickedElement.parentNode.replaceChild(newElement, currentClickedElement);

    currentClickedElement = newElement

    updateRight(currentClickedElement);

}


export let changeClass = (e) => {
    if (e.target.classList.value.includes("lastDimention")) {
        let originParent = e.target.closest('.dropRoot');

        let oldClass = originParent.querySelector('button')
        // console.log(e.target.innerHTML, " from : ", oldClass.innerText + "|")
        // console.log(currentClickedElement.classList)
        currentClickedElement.classList.replace(oldClass.innerText.trim(), (e.target.innerHTML))
        updateRight(currentClickedElement);

    }
}

export let deleteClass = (e) => {

    let originParent = e.target.closest('.container');
    let classToDelete = originParent.querySelector('button')


    currentClickedElement.classList.remove(classToDelete.innerText.trim())
    updateRight(currentClickedElement);

}


export let enebaleEditMode = (event) => {

    currentClickedElement = event.target;
    if (currentClickedElement.tagName == "IMG") {
        selectImg()
    }

    updateRight(currentClickedElement);
    const clickedElement = event.target;
    const allChildren = root.querySelectorAll('*');

    allChildren.forEach(child => {

        if (child !== clickedElement) {

            child.classList.remove('focused');
        }
    });

}

let enableFocus = (event) => {
    event.target.classList.add("focused")
    console.log('focused :)')
}


addBasicEventsToPage();
addEventToAllDescendants(root, 'click', enableFocus)
addClassToAllDescendants("componentBuilderRoot", "editable")

addDragEvents(root);