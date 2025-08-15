(function() {
	function updateNavbarState(navbar) {
		if (window.scrollY > 0) {
			navbar.classList.add('scrolled');
		} else {
			navbar.classList.remove('scrolled');
		}
	}

	document.addEventListener('DOMContentLoaded', function() {
		var navbar = document.querySelector('.navbar');
		if (!navbar) return;

		updateNavbarState(navbar);

		var ticking = false;
		window.addEventListener('scroll', function() {
			if (!ticking) {
				window.requestAnimationFrame(function() {
					updateNavbarState(navbar);
					ticking = false;
				});
				ticking = true;
			}
		}, { passive: true });
	});
})();