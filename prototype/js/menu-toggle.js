document.addEventListener('DOMContentLoaded', function() {
    const menuToggleButton = document.querySelector('.menu-toggle-button');
    const sideMenu = document.querySelector('.side-menu');

    if (menuToggleButton && sideMenu) {
        menuToggleButton.addEventListener('click', function() {
            sideMenu.classList.toggle('open');
        });
    }
});
