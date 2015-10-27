$(function(){
    $( 'input.address' ).each( function() {
        var $this = $( this );
	var geo   = $( '#id_' + $this.attr( 'name' ) + '_geocode' );
        $this.geocomplete({ json: geo });
// .change( function() {
// 	    // if(self.val() != fmtd.val()) {
// 	    //     var cmp_names = ['country', 'country_code', 'locality', 'postal_code',
// 	    //     		 'route', 'street_number', 'state', 'state_code',
// 	    //     		 'formatted', 'latitude', 'longitude'];
// 	    //     for(var ii = 0; ii < cmp_names.length; ++ii)
// 	    //         $('input[name="' + self.attr('name') + '_' + cmp_names[ii] + '"]').val('');
// 	    // }
// 	});
    });
});
