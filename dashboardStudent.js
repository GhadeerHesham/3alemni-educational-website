const resizeBtn = document.getElementById('resize');
resizeBtn.addEventListener('click', function(e) {
    e.preventDefault();
    document.body.classList.toggle('sb-expand');
});

let navbar = document.querySelector('.dashboard-header .navbar');
let menu = document.querySelector('#menu');

// Toggle the navbar on menu click
menu.onclick = () => {
    navbar.classList.toggle('active');
}

// Hide the navbar on scroll
window.onscroll = () => {
    navbar.classList.remove('active');
}