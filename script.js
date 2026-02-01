const navLinks = document.querySelectorAll('.nav-links a');

navLinks.forEach((link) => {
  link.addEventListener('click', () => {
    const toggle = document.querySelector('.nav-links');
    if (toggle) {
      toggle.classList.remove('open');
    }
  });
});
