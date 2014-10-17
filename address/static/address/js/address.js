$(function(){
    $('input.address').each(function(){
        var self = $(this);
        self.geocomplete({
            details: $('#' + self.attr('name') + '_components'),
            detailsAttribute: 'data-geo'
        });
    });
});
