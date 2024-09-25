$(document).ready(function(){
    $(".owl-carousel").owlCarousel({
        loop: true,
        margin: 10,
        nav: true,
        responsive: {
            0: {
                items: 1
            },
            600: {
                items: 2
            },
            1000: {
                items: 3
            }
        }
    });
});


window.addEventListener('scroll', function() {
    var navbar = document.getElementById('navbar');
    if (window.scrollY > window.innerHeight/1.2) {
        navbar.classList.add('navbar-red');
    } else {
        navbar.classList.remove('navbar-red');
    }
});