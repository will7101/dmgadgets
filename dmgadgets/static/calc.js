$(function () {
    $('#exprForm').submit(function (event) {
            event.preventDefault();
            $.ajax({
                type: 'GET',
                url: 'api/parse',
                data: {
                    expr: $('#expr').val(),
                },
                dataType: 'json',
                success: function (data) {
                    console.log(data);
                    if (data['status'] === 'ok') {
                        let $result_list = $('#resultList');
                        $result_list.empty();

                        $.each(data['result_list'], function (i, item) {
                            console.log(item);
                            let $li = $('<li>', {
                                'class': 'list-group-item',
                            });

                            let $title = $('<h4>', {
                                'class': 'mb-3',
                            }).html(item['title']);

                            let $content = $('<p>', {
                                'class': 'text-monospace',
                            }).html(item['content']);

                            $li.append($title);
                            $li.append($content);

                            $result_list.append($li);
                        });

                        let $truth_table = $('#truthTable');
                        $truth_table.empty();

                        let $thead = $('<thead>').appendTo($truth_table);
                        let $tr = $('<tr>').appendTo($thead);

                        $.each(data['var_names'], function (i, var_name) {
                            $('<th>', {
                                scope: 'col',
                                text: var_name,
                            }).appendTo($tr);
                        });

                        $('<th>', {
                            scope: 'col',
                            text: $('#expr').val(),
                        }).appendTo($tr);

                        let $tbody = $('<tbody>').appendTo($truth_table);

                        $.each(data['truth_table'], function (i, row) {
                            let $tr = $('<tr>').appendTo($tbody);
                            $.each(data['var_names'], function (i, var_name) {
                                let value = row[var_name];
                                $('<td>', {
                                    class : value === true ? "color-true" : "color-false",
                                    text: Number(value),
                                }).appendTo($tr);
                            });

                            $('<td>', {
                                text: Number(row['result']),
                            }).appendTo($tr);
                        });

                    } else {
                        alert(data['msg']);
                    }
                }
            });
        }
    );

    $('#exprForm input[type=radio]').change(function () {
        console.log(this.value);
        if(this.value === 'expr') {
            $('#expr').prop('disabled', false);
            $('#fieldTruth').prop('disabled', true);
            $('#varNum').slider('disable')
        }else if(this.value==='truth'){
            $('#expr').prop('disabled', true);
            $('#fieldTruth').prop('disabled', false);
            $('#varNum').slider('enable')
        }
    });

    $('#varNum').on('slide', function (event) {
        $('#varNumLabel').text(event.value);
    })
});
