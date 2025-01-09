class Rectangle {
    constructor(x, y, width, height, color = '#3498db', speed = 10) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.color = color;
        this.speed = speed;
        this.moveDirection = 0;
    }

    draw(ctx) {
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }

    move() {
        this.x += this.moveDirection * this.speed;
    }
}

class Ball {
    constructor(x, y, width, height, color = '#3498db', speed = 1) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.color = color;
        this.speed = speed;
        this.dy = speed; // Ball's vertical speed
    }

    draw(ctx) {
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }

    move() {
        this.y += this.dy;

        // Reverse direction when hitting top or bottom of the canvas
        if (this.y <= 0 || this.y + this.height >= canvas.height) {
            this.dy = -this.dy; // Reverse vertical direction
        }
    }

    checkCollision(rectangle) {
        if (this.x < rectangle.x + rectangle.width &&
            this.x + this.width > rectangle.x &&
            this.y < rectangle.y + rectangle.height &&
            this.y + this.height > rectangle.y) 
        {
            this.dy = -this.dy; // Reverse direction on collision
        }
    }
}

const canvas = document.getElementById('myCanvas');
const ctx = canvas.getContext('2d');

// Create an instance of Rectangle
const rectangle = new Rectangle(450, 0, 100, 25);
const rectangle2 = new Rectangle(450, 475, 100, 25);
const ball = new Ball(450, 250, 25, 25);

//On fait comme Cub3d, plutot que de directement bouger le rectangle, on change sa variable direction 
// qui va etre changer lors du call a update()
window.addEventListener('keydown', (e) => {
    if (e.key === 'a' || e.key === 'A') {
        rectangle.moveDirection = -1;
    } 
    else if (e.key === 'd' || e.key === 'D') {
        rectangle.moveDirection = 1;
    }
    else if (e.key === 'j' || e.key === 'J') {
        rectangle2.moveDirection = -1;
    } 
    else if (e.key === 'l' || e.key === 'L') {
        rectangle2.moveDirection = 1;
    }
});

window.addEventListener('keyup', (e) => {
    if (e.key === 'a' || e.key === 'A' || e.key === 'd' || e.key === 'D') {
        rectangle.moveDirection = 0;
    } else if (e.key === 'j' || e.key === 'J' || e.key === 'l' || e.key === 'L') {
        rectangle2.moveDirection = 0;
    }
});

function update() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Move
    rectangle.move();
    rectangle2.move();
    ball.move();

    // Check for collisions
    ball.checkCollision(rectangle);
    ball.checkCollision(rectangle2);

    //Draw all
    rectangle.draw(ctx);
    rectangle2.draw(ctx);
    ball.draw(ctx);

    // Methode de javascript qui demande la prochaine frame pour avoir un framerate smooth
    requestAnimationFrame(update);
}

// Start the animation loop
update();

