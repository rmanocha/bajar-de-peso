$('#id_date').datepicker({dateFormat: 'yy-mm-dd', maxDate: '+0d'});
$('#id_target_date').datepicker({dateFormat: 'yy-mm-dd'}).qtip({
    content: 'How soon do you wanna reach your target weight?',
    style: {
        name: 'cream',
        tip: 'topLeft'
    },    
    show: 'mouseover',
    hide: 'mouseout'
});

$('#id_target_weight').qtip({
    content: 'How light do you wanna be?',
    style: {
        name: 'cream',
        tip: 'topLeft'
    },    
    show: 'focus',
    hide: 'blur'
});

$('#id_height').qtip({
    content: 'Your height (in cms). This is used to calculate your BMI.',
    style: {
        name: 'cream',
        tip: 'topLeft'
    },    
    show: 'focus',
    hide: 'blur'
});

$('.weight-input').live('dblclick', function() {
    var weight = $(this).html();
    var new_elem = $('<input type="text" />').val(weight).blur(function() { $(this).parent().html(weight); $(this).remove(); });
    $(this).html(new_elem);
    new_elem.focus();
}).each(function() {
    $(this).qtip({
        content: 'Double click to edit this entry',
        style: {
            name: 'cream',
            tip: 'topLeft'
        },
        show: 'mouseover',
        hide: 'mouseout'
    });
});

$('.delete-entry').live('click', function() {
    tr_elem = $(this).parent();
    date = tr_elem.find('input')[0].value;
    console.log('abt to delete for ' + date);
    $.post('/delete_data/', {'date' : date},
        function(data) {
            tr_elem.slideUp('slow', function() { $(this).remove(); });
        }
    );
});

$('input').live('keypress', function(e) {
    if(e.keyCode == 13) {
        var elem = $(this);
        var date_elem = elem.parent().prev('td').find('input')[0].value;
        $.post('/', {'date' : date_elem, 'weight' : elem.val()},
            function(data) {
                if(data.error == 0) {
                    elem.parent().html(data.weight);
                    $('#placeholder').html('');
                    drawChart();
                } //something needs to happen here
        }, 'json');
        elem.parent().next().next().next().children().remove(); //removing the cancel image
    }
});

google.load('visualization', '1', {'packages' : ['linechart']});
google.setOnLoadCallback(drawChart);

function drawChart() {
    if($('#placeholder').length == 0)
        return
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
        chart.draw(data, {width: 540, height: 270, title : 'My Weight Tracker'});
    });
}
