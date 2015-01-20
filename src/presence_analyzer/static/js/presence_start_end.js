function chart(loading) {
    var selected_user = $("#user_id").val(),
        chart_div = $('#chart_div'),
        dates = [],
        data = new google.visualization.DataTable();
    if (selected_user) {
        loading.show();
        chart_div.hide();

        $.getJSON('/api/v1/presence_start_end/' + selected_user, function (result) {
            var formatter = new google.visualization.DateFormat({pattern: 'HH:mm:ss'}),
                chart = new google.visualization.Timeline(chart_div[0]),
                options = {hAxis: {title: 'Weekday'}};

            $.each(result, function (i, el) {
                dates.push([el.weekday, new Date(el.start), new Date(el.end)]);
            });

            data.addColumn('string', 'Weekday');
            data.addColumn({type: 'datetime', id: 'Start'});
            data.addColumn({type: 'datetime', id: 'End'});
            data.addRows(dates);
            formatter.format(data, 1);
            formatter.format(data, 2);

            chart_div.show();
            loading.hide();
            chart.draw(data, options);
        })
    }
}