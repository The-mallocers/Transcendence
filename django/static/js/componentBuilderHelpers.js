const root = document.getElementById("componentBuilderRoot")
const lastElement = root.lastElementChild
const add  = document.createElement("div")

const elemTag = document.getElementById("elementTag")
const elemAttributes = document.getElementById("elementAttributes")
const classAnchor = document.getElementById("elementClasses")
const childAnchor = document.getElementById("elementChilds")

const classAdd = document.getElementById("classAdd")
const childAdd = document.getElementById("childAdd")

// const classAnchor = document.getElementById("elementClasses")


let currentClickedElement


const evaluateEmpty = ()=>{
    const childElements = root.querySelectorAll("*");


    for (let i = 0; i < childElements.length; i++){

        // emptyChildren.forEach((el)=>{
        //     console.log(el instanceof HTMLElement);
            if (!["img"].includes(childElements[i].tagName.toLowerCase())){
                if (childElements[i].innerHTML.length == 0)
                    childElements[i].classList.add("empty");
                else
                    childElements[i].classList.remove("empty");
            }
        // })
    }
    // const emptyChildren = Array.from(childElements).filter(child => {
    //     return !child.innerHTML.trim(); 
    // });

}

const addChild = () => {
    let div = document.createElement("div")
    currentClickedElement.appendChild(div)

    updateRight(currentClickedElement);
    evaluateEmpty();
}


const rmChild = (e) => {

    // console.log("/////" + e.target.getAttribute("data-id"), root.querySelectorAll(e.target.getAttribute("data-id"))[0])

    let toDelete = root.querySelectorAll(`[data-id="${e.target.getAttribute("data-id")}"]`)[0]

    // div.classList.add("empty");
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
        const li       = document.createElement("li")
        const span       = document.createElement("p")


        const deleteBtn  = document.createElement("div")
        deleteBtn.classList.add("minus")

        deleteBtn.addEventListener("click", (e)=>{rmChild(e)})
        children[i].setAttribute("data-id", i)
        deleteBtn.setAttribute("data-id", i)
        span.classList.add("text-truncate")
        // console.log(children[i])
        li.innerText   = children[i].tagName + " | ";
        span.innerText = `${children[i].innerText}`

        li.appendChild(deleteBtn)
        li.appendChild(span)

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

let updateRight = (target)=>{
    elemTag.innerHTML = '';
    elemAttributes.innerHTML = '';
    classAnchor.innerHTML = '';
    childAnchor.innerHTML = '';
    elemTag.innerText = target.tagName

    target.classList.forEach((className) => {
        if(!(className == "editable" || className == "focused" || className == "empty")){
            const classDropContainer = document.createElement("div")

            classDropContainer.classList.add("container", "d-flex", "justify-content-start", "align-items-center")

            const drop  = buildClassesDropDown(className)
            const sub   = document.createElement("div")

            sub.addEventListener("click", (e)=>{ deleteClass(e)})
            sub.classList.add("minus")
            console.log(drop)

            // const btn = drop.querySelector("#dropdownMenuButton2")
            // btn.textContent = className
            drop.appendChild(sub)
            classDropContainer.appendChild(drop)


            classAnchor.appendChild(classDropContainer)
        }
    });


    addAttributeToTxtDescendants("componentBuilderRoot","contenteditable", "true")
    displayChildren();
    updateUrl(currentClickedElement.tagName)
    updateAttributes()
    evaluateEmpty();
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
    // if (e.target.classList.value.includes("lastDimention")){
        let originParent = e.target.closest('.container');
        let classToDelete = originParent.querySelector('button')

        // console.log(classToDelete.innerText)
        // updateRight(currentClickedElement);
        currentClickedElement.classList.remove(classToDelete.innerText.trim())
        updateRight(currentClickedElement);

    // }
}


let enableDebug = (event) => {

    currentClickedElement = event.target; 
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


addEventToAllDescendants(root, 'click', enableFocus)


addClassToAllDescendants("componentBuilderRoot", "editable")



