$(function(){
    $( 'input.address' ).each( function() {
        var $this = $( this );
	var geo = $( '#id_' + $this.attr( 'name' ) + '_geocode' );
        $this.geocomplete({ json: geo }).change( function() {
            var data = JSON.parse( geo.val() );
	    if( $this.val() != data.formatted_address ) {
                geo.val( '' );
            }
        });
    });
});
