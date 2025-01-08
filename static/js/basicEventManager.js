
import {enebaleEditMode} from "./componentBuilderHelpers.js"

function addEventListenerOnce(element, event, handler) {
    const eventKey = `${event}-listener`;

    if (!element[eventKey]) {
        element.addEventListener(event, handler);
        element[eventKey] = true;
    }
}


export let addEventToAllDescendants = (parent, event, handler) => {
    const parentElement = parent
    if (parentElement) {
        parentElement.querySelectorAll('*').forEach((element) => {
            addEventListenerOnce(element, event, handler)
        });
    } else {
        console.error('Parent element not found.');
    }
}

export const addBasicEventsToPage = ()=>{
    root.addEventListener('click', (e)=>{
        enebaleEditMode(e);
    });
    
    
    
    classAnchor.addEventListener('click', (e)=>{changeClass(e)})
    
    
    classAdd.addEventListener("click", ()=>{
        if (currentClickedElement){
            currentClickedElement.classList.add("new-class")
            updateRight(currentClickedElement)
        }
    
    })
    
    childAdd.addEventListener('click', (e)=>{addChild()})
}