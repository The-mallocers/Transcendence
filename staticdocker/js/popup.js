const openPopup = (popup, untouchable) => {
    popup.classList.add("displayed")
    untouchable.classList.add("untouchable")
}

export const selectImg = () => {


    const imgPop = document.getElementById("imgSelectPopup")
    const toolsContainer = document.getElementById("toolsContainer")

    openPopup(imgPop, toolsContainer)

    let test = imgPop.querySelectorAll('.imgDisplay')

    for (let i = 0; i < test.length; i++) {
        test[i].addEventListener("click", (e) => {
            let img = e.target.querySelector("img")
            console.log(img.getAttribute("src"))
            currentClickedElement.setAttribute("src", img.getAttribute("src"))

            imgPop.classList.remove("displayed")
            toolsContainer.classList.remove("untouchable")
        })
    }
}