function parseInterval(value) {
    var result = new Date(1,1,1);
    result.setMilliseconds(value*1000);
    return result;
}

(function($) {
    $(document).ready(function() {
        var loading = $('#loading');
        var results = [];
        $.getJSON("/api/v1/users", function(result) {
            var dropdown = $("#user_id");

            $.each(result, function(item) {
                dropdown.append($("<option />").val(this.user_id).text(this.name));
                results[this.user_id] = this;
            });
            dropdown.show();
            loading.hide();
        });
        $('#user_id').change(function() {
            var id = $(this).val();
            if(results[id]) {
                $('#name').text(results[id]['name']);
                $('#avatar').attr('src', results[id]['avatar']);
            } else {
                $('#name').text('');
                $('#avatar').attr('src', '');
            }

            chart(loading);
        });
    });
})(jQuery);