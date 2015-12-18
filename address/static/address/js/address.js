function django_input_address_setup() {
    $('input.address').each(function() {
        var self = $(this);
        //Skip if already setup
        if (self.data('django_input_address_setup')) {
            return true;
        }

        var cmps = $('#' + self.attr('name') + '_components');
        var fmtd = $('input[name="' + self.attr('name') + '_formatted"]');
        self.geocomplete({
            details: cmps,
            detailsAttribute: 'data-geo'
        }).change(function() {
            if (self.val() != fmtd.val()) {
                var cmp_names = [
                    'country',
                    'country_code',
                    'locality',
                    'postal_code',
                    'route',
                    'street_number',
                    'state',
                    'state_code',
                    'formatted',
                    'latitude',
                    'longitude'
                ];
                for (var ii = 0; ii < cmp_names.length; ++ii)
                    $('input[name="' + self.attr('name') + '_' + cmp_names[ii] + '"]').val('');
            }
        });

        //Add data so element will not be setup again
        self.data('django_input_address_setup', true);
    });
}


$(function() {
	django_input_address_setup();
});