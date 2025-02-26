import {buildClassesDropDown, evaluateEmpty, deleteClass} from "./componentBuilderHelpers.js"
import { addEventToAllDescendants, addBasicEventsToPage} from "./basicEventManager.js"
import { dragoverHandler, dragleaveHandler, dropHandler, addDragEvents } from "./dragDrop.js"


export const addChild = () => {
    let div = document.createElement("div")
    currentClickedElement.appendChild(div)

    updateRight(currentClickedElement);
    evaluateEmpty();
}


const rmChild = (e) => {
    let toDelete = root.querySelectorAll(`[data-id="${e.target.getAttribute("data-id")}"]`)[0]
    currentClickedElement.removeChild(toDelete)

    updateRight(currentClickedElement);
    evaluateEmpty();
}

export const displayChildren = () =>{
    let atCleaner = document.querySelectorAll("[data-id]")

    atCleaner.forEach((at)=>at.removeAttribute("data-id"))

    if (currentClickedElement == undefined || currentClickedElement == null)
        return;

    const children = currentClickedElement.children;


    for (let i = 0 ; i < children.length; i++){
        const li            = document.createElement("li")
        const btnContain    = document.createElement("div")

        const upBtn         = document.createElement("div")
        const downBtn       = document.createElement("div")

        upBtn.innerHTML   = "&uarr;"
        downBtn.innerHTML = "&darr;"

        const deleteBtn  = document.createElement("div")
        deleteBtn.classList.add("minus")

        li.classList.add("d-flex")
        li.classList.add("align-items-center")
        li.classList.add("justify-content-center")

        btnContain.classList.add("m-2")
        upBtn.classList.add("p-2")
        upBtn.classList.add("updwn")
        
        downBtn.classList.add("p-2")
        downBtn.classList.add("updwn")

        deleteBtn.addEventListener("click", (e)=>{rmChild(e)})

        li.setAttribute("data-id", i)
        deleteBtn.setAttribute("data-id", i)
        children[i].setAttribute("data-id", i)
       
        li.addEventListener("mouseenter", (e)=>{
            console.log(currentClickedElement)

            let toHover = currentClickedElement.querySelectorAll(`[data-id="${e.target.getAttribute("data-id")}"]`)[0]
            console.log(toHover)
            toHover.classList.add("hoveredChild")
        })


               
        li.addEventListener("mouseleave", (e)=>{
            console.log(currentClickedElement)

            let toHover = currentClickedElement.querySelectorAll(`[data-id="${e.target.getAttribute("data-id")}"]`)[0]
            console.log(toHover)
            toHover.classList.remove("hoveredChild")
        })


        upBtn.addEventListener("click", (e)=>{
            let closestLi = e.target.closest("li")
            let beforeId =  closestLi.getAttribute("data-id") - 1
            let moveBefore = currentClickedElement.querySelectorAll(`[data-id="${beforeId}"]`)[0]
            let toMove = currentClickedElement.querySelectorAll(`[data-id="${closestLi.getAttribute("data-id")}"]`)[0]
            currentClickedElement.insertBefore(toMove ,moveBefore)
            toMove.classList.remove("hoveredChild")

            updateRight(currentClickedElement)
        })

        downBtn.addEventListener("click", (e)=>{
            let closestLi = e.target.closest("li")
            let beforeId =  (parseInt(closestLi.getAttribute("data-id")) + 2).toString()


            let moveBefore = currentClickedElement.querySelectorAll(`[data-id="${beforeId}"]`)[0]
            let toMove = currentClickedElement.querySelectorAll(`[data-id="${closestLi.getAttribute("data-id")}"]`)[0]
            currentClickedElement.insertBefore(toMove ,moveBefore)
            toMove.classList.remove("hoveredChild")

            updateRight(currentClickedElement)
        })


        li.innerText   = children[i].tagName;
        li.appendChild(deleteBtn)
        btnContain.appendChild(upBtn)
        btnContain.appendChild(downBtn)

        li.appendChild(btnContain)

        console.log(li)
        childAnchor.appendChild(li)
    }
}

export let updateAttributes = () =>{

    let attributes = contextData[currentClickedElement.tagName.toLowerCase()]

    attributes.forEach((attribute) => {
            const elementAttribute = currentClickedElement[attribute]

            const container =  document.createElement("div")
            const key  = document.createElement("div")
            const value  = document.createElement("input")

            container.classList.add("container","d-flex","justify-content-center","align-items-center")
            key.classList.add("col","m-3", "bold")
            value.classList.add("col","m-3","text-end")
           
            value.id = attribute
            value.setAttribute("type", "text")
            value.value =  ((elementAttribute != undefined) || (elementAttribute != null)) ? elementAttribute : ""


            value.addEventListener('keydown', function(event) {
                if (event.key === 'Enter') {
                    console.log('Enter key was pressed', value.value);
                
                    currentClickedElement.setAttribute(value.id, value.value)
                }
            });
            key.textContent = attribute
            container.appendChild(key)
            container.appendChild(value)
            elemAttributes.appendChild(container)
    });
}



export let updateRight = (target)=>{
    elemTag.innerHTML = '';
    elemAttributes.innerHTML = '';
    classAnchor.innerHTML = '';
    childAnchor.innerHTML = '';

    if (target != undefined){
        elemTag.innerText = target.tagName

        target.classList.forEach((className) => {
            if(!(className == "editable" || className == "focused" || className == "empty")){
                const classDropContainer = document.createElement("div")
    
                classDropContainer.classList.add("container", "d-flex", "justify-content-start", "align-items-center")
    
                const drop  = buildClassesDropDown(className)
                const sub   = document.createElement("div")
    
                sub.addEventListener("click", (e)=>{ deleteClass(e)})
                sub.classList.add("minus")
                drop.appendChild(sub)
                classDropContainer.appendChild(drop)
    
    
                classAnchor.appendChild(classDropContainer)
            }
        });

        addAttributeToTxtDescendants("componentBuilderRoot","contenteditable", "true")
        displayChildren();
    
        updateAttributes()
        evaluateEmpty();
    
        addEventToAllDescendants(root, 'dragover', dragoverHandler)
        addEventToAllDescendants(root, 'dragleave', dragoverHandler)
        addEventToAllDescendants(root, 'drop', dragoverHandler)
    }

}



export const addClassToAllDescendants = (parentId, className) => {
    const parentElement = document.getElementById(parentId);
    if (parentElement) {
        parentElement.querySelectorAll('*').forEach((element) => {
            if (!element.classList.contains(className)) {
                element.classList.add(className);
            }
        });
    } else {
        console.error('Parent element not found.');
    }
}


let addAttributeToTxtDescendants = (parentId, attribute, value) => {
    const parentElement = document.getElementById(parentId);
    if (parentElement) {
        parentElement.querySelectorAll('*').forEach((element) => {
            if (["p","h1","h2","h3","h4","h5","h6","a"].includes(element.tagName.toLowerCase())) {

                element.setAttribute(attribute, value);
            }
        });
    } else {
        console.error('Parent element not found.');
    }
}

