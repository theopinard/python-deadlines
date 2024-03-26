function update_filtering(data) {
	var page_url = window.location.pathname;
	store.set('{{site.domain}}-subs', data.subs);

	$('.confItem').hide();

	// Loop through selected values in data.subs
	for (const s of data.subs) {
		// Show elements with class .s-conf (where s is the selected value)
		$('.' + s + '-conf').show();
	}

  if (data.subs.length === 0 || data.subs.length == data.all_subs.length) {
		window.history.pushState('', '', page_url);
  } else {
		// Join the selected values into a query parameter
		window.history.pushState('', '', page_url + '?sub=' + data.subs.join());
  }
}

function createCalendarFromObject(data) {
  return createCalendar({
		options: {
			class: 'calendar-obj',

			// You can pass an ID. If you don't, one will be generated for you
			id: data.id,
		},
		data: {
			// Event title
			title: data.title,

			// Event start date
			start: data.start_date,

      // Event duration (minutes)
      duration: 60,

			// You can also choose to set an end time
			// If an end time is set, this will take precedence over duration
			end: data.end_date,

			// Event Address
			address: data.place,

			// Event Description
			description: '<a href='+data.link+'>'+data.title+'</a>',
		},
  });
}
