import { dragoverHandler, dragleaveHandler, dropHandler } from "./dragDrop.js"


const root = document.getElementById("componentBuilderRoot")
const lastElement = root.lastElementChild
const add  = document.createElement("div")

const elemTag = document.getElementById("elementTag")
const elemAttributes = document.getElementById("elementAttributes")
const classAnchor = document.getElementById("elementClasses")
const childAnchor = document.getElementById("elementChilds")

const classAdd = document.getElementById("classAdd")
const childAdd = document.getElementById("childAdd")


const saveBtn = document.getElementById("saveBtn")
const componentName = document.getElementById("componentName")


const componentLib = document.getElementById("componentLib")


const saveComponent = async (e)=>{
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



saveBtn.addEventListener("click", async (e)=> {await saveComponent(e)})



const evaluateEmpty = ()=>{
    const childElements = root.querySelectorAll("*");

    for (let i = 0; i < childElements.length; i++){
        if (!["img"].includes(childElements[i].tagName.toLowerCase())){
            if (childElements[i].innerHTML.length == 0)
                childElements[i].classList.add("empty");
            else
                childElements[i].classList.remove("empty");
        }
    }
}

const addChild = () => {
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




const displayChildren = () =>{
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

let updateUrl = (atribute) =>{
    let url = new URL(window.location);
    url.searchParams.set('attr', atribute.toLowerCase());
    window.history.pushState({ path: url.toString() }, '', url.toString());
}

let updateAttributes = () =>{

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


            console.log(key, value)
        
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

function isLastDimension(obj) {

    if (typeof obj !== "object" || obj === null) {
      return false;
    }
  
    return Object.values(obj).every(
      (value) => typeof value !== "object" || value === null
    );
  }

const createSubmenu = (context) => {

    const filteredJson = context
    const li = `
            ${
                Object.keys(filteredJson).map((key) => {
                    const val = filteredJson[key];
                
                    if (key !== "classnames" && typeof val === "object" && val !== null)
                        return`<li class="dropstart">
                                <a class="dropdown-item dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" data-bs-auto-close="outside">
                                    ${key}
                                </a>
                            <ul class="dropdown-menu" data-bs-display="static">
                                ${createSubmenu(val)}
                            </ul>`
                    else if (Array.isArray(val))
                        return val.map((v) => `<li class="classnamesDropdowns" ><a class="dropdown-item lastDimention" href="#">${v}</a></li>`).join("");
                    else
                        return`<li><a class="dropdown-item lastDimention" href="#">${val}</a></li>`

                  }).join("")
            }`;

    return li
}

const buildClassesDropDown = (className) => {
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


let changeTag = (e)=>{
    console.log(e)

    console.log(currentClickedElement)

    const newElement = document.createElement(e.innerText);
    newElement.innerHTML = currentClickedElement.innerHTML; 

    currentClickedElement.parentNode.replaceChild(newElement, currentClickedElement);

    currentClickedElement = newElement

    updateRight(currentClickedElement);

}


let changeClass = (e)=>{
    if (e.target.classList.value.includes("lastDimention")){
        let originParent = e.target.closest('.dropRoot');

        let oldClass = originParent.querySelector('button')
        console.log(e.target.innerHTML, " from : ", oldClass.innerText + "|")
        console.log(currentClickedElement.classList)
        currentClickedElement.classList.replace(oldClass.innerText.trim(), (e.target.innerHTML))
        updateRight(currentClickedElement);

    }
}

let deleteClass = (e)=>{

        let originParent = e.target.closest('.container');
        let classToDelete = originParent.querySelector('button')


        currentClickedElement.classList.remove(classToDelete.innerText.trim())
        updateRight(currentClickedElement);

}

const openPopup = (popup, untouchable)=>{
    popup.classList.add("displayed")
    untouchable.classList.add("untouchable")
}

const selectImg = () =>{


    const imgPop = document.getElementById("imgSelectPopup")
    const toolsContainer = document.getElementById("toolsContainer")

    openPopup(imgPop, toolsContainer)

    let test = imgPop.querySelectorAll('.imgDisplay')

    for (let i = 0; i < test.length ; i++){
        test[i].addEventListener("click", (e)=>{
            let img = e.target.querySelector("img")
            console.log(img.getAttribute("src"))
            currentClickedElement.setAttribute("src", img.getAttribute("src"))

            imgPop.classList.remove("displayed")
            toolsContainer.classList.remove("untouchable")
        })
    }

    

    console.log(imgPop)
}

let enableDebug = (event) => {

    currentClickedElement = event.target; 
    if (currentClickedElement.tagName == "IMG"){
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

let addClassToAllDescendants = (parentId, className) => {
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

function addEventListenerOnce(element, event, handler) {
    const eventKey = `${event}-listener`;

    if (!element[eventKey]) {
        element.addEventListener(event, handler);
        element[eventKey] = true;
    }
}


let addEventToAllDescendants = (parent, event, handler) => {
    const parentElement = parent
    if (parentElement) {
        parentElement.querySelectorAll('*').forEach((element) => {
            addEventListenerOnce(element, event, handler)
        });
    } else {
        console.error('Parent element not found.');
    }
}



root.addEventListener('click', (e)=>{
    enableDebug(e);
});



classAnchor.addEventListener('click', (e)=>{changeClass(e)})




classAdd.addEventListener("click", ()=>{
    if (currentClickedElement){
        currentClickedElement.classList.add("new-class")
        updateRight(currentClickedElement)
    }

})

childAdd.addEventListener('click', (e)=>{addChild()})



for (let i = 0; i < componentLib.children.length; i++){
    componentLib.children[i].addEventListener('dragstart', (e)=>{
        console.log(e.target)
        currentDrag = e.target
    })



    componentLib.children[i].addEventListener('dragend', (e)=>{
        console.log("stoped")
    })
}



addEventToAllDescendants(root, 'click', enableFocus)
addClassToAllDescendants("componentBuilderRoot", "editable")

root.addEventListener('dragover', dragoverHandler)
root.addEventListener('dragleave', dragleaveHandler)
root.addEventListener('drop', dropHandler);


