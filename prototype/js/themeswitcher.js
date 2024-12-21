// JavaScript for Theme Switching

document.addEventListener('DOMContentLoaded', () => {
    const themeDropdown = document.getElementById('theme-dropdown');
    const body = document.body;

    // Load saved theme from localStorage
    const savedTheme = localStorage.getItem('selectedTheme');
    if (savedTheme) {
        body.classList.add(savedTheme);
        themeDropdown.value = savedTheme;
    }

    // Listen for theme changes
    themeDropdown.addEventListener('change', (event) => {
        const selectedTheme = event.target.value;

        // Remove previous theme classes
        body.className = body.className.replace(/\btheme-\w+\b/g, '');
        if (selectedTheme) {
            body.classList.add(selectedTheme);
        }

        // Save theme to localStorage
        localStorage.setItem('selectedTheme', selectedTheme || '');
    });
});
