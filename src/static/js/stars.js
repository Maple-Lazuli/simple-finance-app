// Select the canvas element and set up the context
const canvas = document.getElementById('starsCanvas');
const ctx = canvas.getContext('2d');

// Resize the canvas to fit the window size
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

// Array to store the stars
const stars = [];
const numberOfStars = 100; // Number of stars you want to display
let slowDownTimer; // Timer for detecting inactivity

// Function to generate random values
function random(min, max) {
    return Math.random() * (max - min) + min;
}

// Star object constructor
function Star() {
    this.x = random(0, canvas.width);  // Random initial X position
    this.y = random(0, canvas.height); // Random initial Y position
    this.size = random(1, 3);          // Random size (tiny stars)
    this.color = `hsl(${random(0, 360)}, 100%, 50%)`; // Random color using HSL
    this.baseSpeedX = random(-0.5, 0.5); // Base speed for horizontal movement
    this.baseSpeedY = random(-0.5, 0.5); // Base speed for vertical movement
    this.speedX = this.baseSpeedX;       // Current speed (modifiable)
    this.speedY = this.baseSpeedY;       // Current speed (modifiable)
    this.speedMultiplier = 1;            // To control velocity scaling
}

// Update the star's position
Star.prototype.update = function() {
    this.x += this.speedX * this.speedMultiplier;
    this.y += this.speedY * this.speedMultiplier;

    // Boundary checking: if the star moves off-screen, wrap it around
    if (this.x < 0) this.x = canvas.width;
    if (this.x > canvas.width) this.x = 0;
    if (this.y < 0) this.y = canvas.height;
    if (this.y > canvas.height) this.y = 0;
};

// Draw the star on the canvas
Star.prototype.draw = function() {
    ctx.fillStyle = this.color;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    ctx.fill();
};

// Function to increase velocity on keypress
function increaseSpeed() {
    stars.forEach(star => {
        // Increase velocity by 0.1x on each keypress (you can adjust this)
        star.speedMultiplier += 0.5;
    });

    // Reset the slowdown timer on every key press
    resetSlowdownTimer();
}

// Function to reset the slowdown timer
function resetSlowdownTimer() {
    // Clear the previous timer
    clearTimeout(slowDownTimer);
    // Set a new timer to start slowing down after 5 seconds of inactivity
    slowDownTimer = setTimeout(slowDownStars, 5000); // 5 seconds (5000 ms)
}

// Function to gradually slow down the stars over 5 seconds
function slowDownStars() {
    let duration = 10000; // 10 seconds
    let startTime = Date.now();

    function gradualSlowdown() {
        let elapsedTime = Date.now() - startTime;
        let progress = elapsedTime / duration; // Progress of slowdown (0 to 1)

        if (progress < 1) {
            stars.forEach(star => {
                // Linearly decrease the speedMultiplier back to 1
                star.speedMultiplier = 1 + (1 - progress) * (star.speedMultiplier - 1); // Gradually reduces
            });
            requestAnimationFrame(gradualSlowdown); // Continue slowing down
        } else {
            // Ensure that speedMultiplier is exactly 1 when slowdown finishes
            stars.forEach(star => star.speedMultiplier = 1);
        }
    }
    gradualSlowdown(); // Start the slowdown process
}

// Create an array of stars
for (let i = 0; i < numberOfStars; i++) {
    stars.push(new Star());
}

// Animation loop
function animate() {
    // Clear the canvas on every frame
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Update and draw each star
    stars.forEach(star => {
        star.update();
        star.draw();
    });

    // Request the next frame
    requestAnimationFrame(animate);
}

// Handle window resize
window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});

// Listen for any keypress to trigger speed increase
window.addEventListener('keydown', increaseSpeed);

// Start the animation loop
animate();
