$(document).ready(function() {
    $('.weight-input').live('dblclick', function() {
        var weight = $(this).html();
        cancel_elem = $('<a></a>').attr('href','#').append($('<img />').attr('src','/static/images/cancel.png').click(function() { new_elem.blur(); return false; }));
        var new_elem = $('<input type="text" />').val(weight).blur(function() { $(this).parent().html(weight); cancel_elem.remove(); });
        $(this).html(new_elem);
        new_elem.focus();
        //UUUUGGGGLLLLYYYY
        $(this).next().next().next().html(cancel_elem);
    });

    $('input').live('keypress', function(e) {
        if(e.keyCode == 13) {
            var elem = $(this);
            var date_elem = elem.parent().prev('td');
            $.post('/', {'date' : date_elem.html(), 'weight' : elem.val()},
                function(data) {
                    elem.parent().html(data.weight);
                    $('#placeholder').html('');
                    drawChart();
            }, 'json');
            elem.parent().next().next().next().children().remove();
        }
    });

    $('#add_prev_date').click(function() {
        if($('input').length != 0) {
            alert('Please enter data in the focused field before adding new entries');
            $('input')[0].focus();
        } else {
            $.get('/get_prev_date/', {}, function(data) {
                var delete_elem = $('<a></a>').attr('href','#').append($('<img />').attr('src', '/static/images/delete.png')).click(function() { $(this).parent().parent().remove(); return false; });
                var input_elem = $('<input type="text />');
                $('#data-table > tbody:last')
                    .append($('<tr></tr>')
                        .append($('<td></td>').html(data))
                        .append($('<td></td>').attr('class', 'weight-input')
                            .append(input_elem)
                        )
                        .append($('<td></td>').attr('id','loss-' + data))
                        .append($('<td></td>').attr('id', 'avg-' + data))
                        .append($('<td></td>').append(delete_elem))
                    );
                input_elem.focus();
            });
        }
        return false;
    });
});

google.load('visualization', '1', {'packages' : ['linechart']});
google.setOnLoadCallback(drawChart);

function drawChart() {
    var data = new google.visualization.DataTable();
    $.getJSON('/get_chart_data/', {}, function(weight_data) {
        data.addColumn('string', 'Date');
        data.addColumn('number', 'Weight (' + weight_units + ')');
        data.addColumn('number', 'Moving Avg. (' + weight_units + ')');
        data.addRows(weight_data.data.length);
        for(var i = 0; i < weight_data.data.length; i++) {
            data.setCell(i, 0, weight_data.data[i][0]);
            data.setCell(i, 1, weight_data.data[i][1]); 
            if(i > 3) {
                var tmp_sum = 0;
                for(var j = 0; j < 5; j++)
                    tmp_sum += weight_data.data[i - j][1];
                avg = Math.round((tmp_sum/5)*100)/100;
                data.setCell(i, 2, avg);
                $('#avg-' + weight_data.data[i][0]).html(avg);
            } else {
                $('#avg-' + weight_data.data[i][0]).html('N/A');
            }
            $('#loss-' + weight_data.data[i][0]).html((i > 0) ? Math.round((weight_data.data[i][1] - weight_data.data[i - 1][1])*100)/100 : 'N/A');
        }
        $('#placeholder').html('');
        var chart = new google.visualization.LineChart(document.getElementById('placeholder'));
        chart.draw(data, {width: 600, height: 300, title : 'My Weight Tracker'});
    });
}
