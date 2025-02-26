const RECTANGLE_SPEED = 15;
const BALL_SPEED = 2;

class Rectangle {
    constructor(x, y, width, height, color = '#3498db', speed = RECTANGLE_SPEED) {
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
        if (this.x < 0)
            this.x = 0;
        else if (this.x + this.width > canvas.width)
            this.x = canvas.width - this.width;
    }
}

class Ball {
    constructor(x, y, width, height, color = '#3498db', speed = BALL_SPEED) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.color = color;
        this.speed = speed;
        this.dy = speed; // Ball's vertical speed
        this.dx = 0;
    }

    draw(ctx) {
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }

    move() {
        this.y += this.dy;
        this.x += this.dx;
        // Reverse direction when hitting top or bottom of the canvas
        if (this.y <= 0 || this.y + this.height >= canvas.height) {
            this.dy = -this.dy; // Reverse vertical direction
        }
        if (this.x <= 0 || this.x + this.width >= canvas.width) {
            this.dx = -this.dx; // Reverse horizontal direction
        }

    }

    checkCollision(rectangle) {
        if (this.x < rectangle.x + rectangle.width &&
            this.x + this.width > rectangle.x &&
            this.y < rectangle.y + rectangle.height &&
            this.y + this.height > rectangle.y) {
            this.dy = -this.dy; // Reverse direction on collision
            const BALL_CENTER = (this.x + this.width) / 2;
            const RECTANGLE_CENTER = (rectangle.x + rectangle.width) / 2;
            this.dx = (BALL_CENTER - RECTANGLE_CENTER) / 10;
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
    } else if (e.key === 'd' || e.key === 'D') {
        rectangle.moveDirection = 1;
    } else if (e.key === 'j' || e.key === 'J') {
        rectangle2.moveDirection = -1;
    } else if (e.key === 'l' || e.key === 'L') {
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

