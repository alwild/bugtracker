$(document).ready(function(){
	
	$('.lookups-delete').bind('click', function(e){
		e.preventDefault();
		var id = $(this).attr('id');
		var href = $(this).attr('url');
		var li = $(this)[0].parentNode;
		$.post(href, 
				{'id' : id},
				function(response){
					$(li).remove();
				});
	});
	
});