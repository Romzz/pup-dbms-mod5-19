$(function() {

	var list = {};
	var counter = 0;
	function onFormSubmit(event){

		var data = $(event.target).serializeArray();
		var thesis = {};


		for(var i = 0; i<data.length ; i++){
			thesis[data[i].name] = data[i].value;
		}
		
		// send data to server
			var thesis_create_api = '/api/thesis';
			$.post(thesis_create_api, thesis, function(response){

			// read response from server
			if (response.status = 'OK') {
				var thesis_list = response.data.year + ' ' + response.data.title  + '<a href="#" id="#edit">Edit</a>' + '<a href="#" id="#delete">Delete</a>' ;
				$('#thesis-list').prepend('<li>' + thesis_list + '</li>')
				$('input[type=text], [type=number]').val('');
			} else {

			}

			});

		return false;
	}

	function loadThesis(){
		var thesis_list_api = '/api/thesis';
		$.get(thesis_list_api, {} , function(response) {
			console.log('#thesis-list', response)
			response.data.forEach(function(thesis){
				var thesis_list = thesis.year + ' ' + thesis.title  + '<a href="#" id="#edit">Edit</a>' + '<span id="button"><a href="#">Delete</a><span>';
				$('#thesis-list').append('<li>' + thesis_list + '</li>')
			});
		});
	}

	loadThesis();

	$('form#create-form').submit(onFormSubmit);

	$(document).on('click', '#button', function(){
		$(this).closest('li').remove();
	});

});