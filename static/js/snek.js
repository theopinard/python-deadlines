function getSeasonStyles() {
	const today = new Date();
	const month = today.getMonth(); // 0-11
	const day = today.getDate();

	// Halloween: October
	if (month === 9) {
		return {
			body: 'url(#spider-web)',
			tongue: 'black',
		};
	}

	// Christmas: December and first week of January
	if (month === 11 || (month === 0 && day <= 7)) {
		return {
			body: 'url(#candy-cane)',
			tongue: 'red',
		};
	}

	if (month === 5) {
		return {
			body: 'url(#pride)',
			tongue: 'url(#progress)',
		};
	}

	if (month === 3 && day === 21) {
		return {
			body: 'url(#earth-day)',
			tongue: 'blue',
		};
	}

	if (month === 2 && day === 7) {
		return {
			body: 'pink',
			tongue: 'red',
		};
	}

	if (month === 10 && day === 18) {
		return {
			body: 'lightblue',
			tongue: 'blue',
		};
	}

	if (month == 2 && day == 17) {
		return {
			body: 'lightgreen',
			tongue: 'green',
		};
	}

	// Easter: March/April (needs to be calculated as it changes)
	// Function to calculate Easter for the current year
	function getEaster(year) {
		const a = year % 19;
		const b = Math.floor(year / 100);
		const c = year % 100;
		const d = Math.floor(b / 4);
		const e = b % 4;
		const f = Math.floor((b + 8) / 25);
		const g = Math.floor((b - f + 1) / 3);
		const h = (19 * a + b - d - g + 15) % 30;
		const i = Math.floor(c / 4);
		const k = c % 4;
		const l = (32 + 2 * e + 2 * i - h - k) % 7;
		const m = Math.floor((a + 11 * h + 22 * l) / 451);
		const month = Math.floor((h + l - 7 * m + 114) / 31) - 1;
		const day = ((h + l - 7 * m + 114) % 31) + 1;
		return { month, day };
	}

	// Check if it's Easter season (2 weeks around Easter Sunday)
	const easter = getEaster(today.getFullYear());
	const twoWeeksInMs = 14 * 24 * 60 * 60 * 1000;
	const easterDate = new Date(today.getFullYear(), easter.month, easter.day);
	const diff = Math.abs(today - easterDate);

	if (diff <= twoWeeksInMs) {
		return {
			body: 'url(#easter-eggs)',
			tongue: 'orange',
		};
	}

	// Default style for non-seasonal times
	return {
		body: '#646464',
		tongue: '#eea9b8',
	};
}

$(document).ready(function () {
	let clickCount = 0;

	$('#left-snek').on('click', function () {
		clickCount++;

		if (clickCount >= 5) {
			$(this).addClass('annoyed');
			$('#right-snek').addClass('annoyed');
		}
	});
});

$(function () {
	// Apply seasonal styles
	const styles = getSeasonStyles();

	// Add style tag for seasonal colors
	const styleTag = `
        <style id="seasonal-styles">
            #smol-snek-body path {
                fill: ${styles.body};
            }
            #smol-snek-tongue path {
                fill: ${styles.tongue};
            }
        </style>
    `;

	$('head').append(styleTag);

	// Rest of your existing code...
	setInterval(function () {
		$('#right-snek').addClass('wiggle');
		setTimeout(function () {
			$('#right-snek').removeClass('wiggle');
		}, 500);
	}, 15000);
	// Add wiggle animation every 5 seconds
	setInterval(function () {
		$('#right-snek').addClass('wiggle');
		setTimeout(function () {
			$('#right-snek').removeClass('wiggle');
		}, 500);
	}, 15000);

	// Add wiggle animation every 5 seconds
	setInterval(function () {
		$('#smol-snek-all').addClass('wiggle');
		setTimeout(function () {
			$('#smol-snek-all').removeClass('wiggle');
		}, 500);
	}, 31000);

	// Pin animation logic
	setTimeout(function () {
		$('#left-snek').show().addClass('visible');
	}, 2500);
	// Pin animation logic
	setTimeout(function () {
		$('#right-snek').show().addClass('visible');
	}, 3000);
	// Pin animation logic
	setTimeout(function () {
		$('#smol-snek-all').show().addClass('visible');
	}, 3250);

	// Show on scroll
	$(window).scroll(function () {
		if ($(window).scrollTop() > 100) {
			$('#location-pin').show().addClass('visible');
		}
	});
});
