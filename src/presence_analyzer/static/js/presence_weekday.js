function chart(loading) {
    var selected_user = $("#user_id").val();
    var chart_div = $('#chart_div');
    if (selected_user) {
        loading.show();
        chart_div.hide();
        $.getJSON("/api/v1/mean_time_weekday/" + selected_user, function (result) {
            $.each(result, function (index, value) {
                value[1] = parseInterval(value[1]);
            });
            var data = new google.visualization.DataTable();
            data.addColumn('string', 'Weekday');
            data.addColumn('datetime', 'Mean time (h:m:s)');
            data.addRows(result);
            var options = {
                hAxis: {title: 'Weekday'}
            };
            var formatter = new google.visualization.DateFormat({pattern: 'HH:mm:ss'});
            formatter.format(data, 1);

            chart_div.show();
            loading.hide();
            var chart = new google.visualization.ColumnChart(chart_div[0]);
            chart.draw(data, options);
        });
    }
}