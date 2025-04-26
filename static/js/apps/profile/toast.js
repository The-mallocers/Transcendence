

function toast_friend(message, data, itemToDelete){
    const date = new Date();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const time = `${hours}:${minutes}`;
    
    const toastHtml = `
    <div class="toast" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="toast-header">
            <img src="/static/assets/imgs/chat.png" class="rounded me-2" alt="..." style="width: 20px; height: 20px; object-fit: contain;">
            <strong class="me-auto">Friend Notification</strong>
            <small>${time}</small>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">${message}</div>
        <div class="mt-2 pt-2 border-top d-flex justify-content-end">
            <button type="button" class="btn type-intra-green me-2 accept_friend">Accept</button>
            <button type="button" class="btn type-intra-white refuse_friend">Refuse</button>
        </div>
    </div>`;
    
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    toastContainer.innerHTML += toastHtml;
    
    const newToast = toastContainer.lastChild;
    const acceptButton = newToast.querySelector('.accept_friend');
    acceptButton.addEventListener('click', function() {
        if (itemToDelete) {
            itemToDelete.remove();
        }
        window.handleAcceptFriend(data.content.username);
    });
    const refuseButton = newToast.querySelector('.refuse_friend');
    refuseButton.addEventListener('click', function() {
        if (itemToDelete) {
            itemToDelete.remove();
        }
        window.handleRefuseFriend(data.content.username);
    });
    const toastBootstrap = new bootstrap.Toast(newToast);
    toastBootstrap.show();
    
    newToast.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

function toast_duel(message, data, itemToDelete){
    const date = new Date();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const time = `${hours}:${minutes}`;
    
    const toastHtml = `
    <div class="toast" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="toast-header">
            <img src="/static/assets/imgs/chat.png" class="rounded me-2" alt="..." style="width: 20px; height: 20px; object-fit: contain;">
            <strong class="me-auto">Friend Notification</strong>
            <small>${time}</small>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">${message}</div>
        <div class="mt-2 pt-2 border-top d-flex justify-content-end">
            <button type="button" class="btn type-intra-green me-2 accept_duel">Accept</button>
            <button type="button" class="btn type-intra-white refuse_duel">Refuse</button>
        </div>
    </div>`;

    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    toastContainer.innerHTML += toastHtml;
    
    const newToast = toastContainer.lastChild;
    const acceptDuel = newToast.querySelector('.accept_duel');
    acceptDuel.addEventListener('click', function() {
        window.handleAcceptDuel(data.content.code);
    });
    const refuseDuel = newToast.querySelector('.refuse_duel');
    refuseDuel.addEventListener('click', function() {
        if (itemToDelete) {
            itemToDelete.remove();
        }
        window.handleRefuseDuel(data.content.code);
    });
    const toastBootstrap = new bootstrap.Toast(newToast);
    toastBootstrap.show();
    
    newToast.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

function toast_message(message){
    const date = new Date();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const time = `${hours}:${minutes}`;
    
    const toastHtml = `
    <div class="toast" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="toast-header">
            <img src="/static/assets/imgs/chat.png" class="rounded me-2" alt="..." style="width: 20px; height: 20px; object-fit: contain;">
            <strong class="me-auto">Notification</strong>
            <small>${time}</small>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">${message}</div>
    </div>`;
    
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    toastContainer.innerHTML += toastHtml;
    
    const newToast = toastContainer.lastChild;
    const toastBootstrap = new bootstrap.Toast(newToast);
    toastBootstrap.show();
    
    newToast.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

export {toast_friend};
export {toast_duel};
export {toast_message};