const left_score = document.getElementById('myScore');
const right_score = document.getElementById('enemyScore');
const vs = document.querySelector('.vs')



if (left_score && right_score) {
    left_score.innerText = window.local.left_score
    right_score.innerText = window.local.right_score
}

if (vs) {
    
    if(window.local.left_name == '') {
        window.local.left_name = 'Guest'
    }
    if(window.local.right_name == '') {
        window.local.right_name = 'Guest'
    }


    vs.innerText = `${window.local.left_name} vs ${window.local.right_name}`
}





