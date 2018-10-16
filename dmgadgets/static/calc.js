$(function () {
    $('#exprForm').submit(function (event) {
            console.log(event.data);
            event.preventDefault();
            if ($('#radioExpr').is(':checked')) {
                $.ajax({
                    type: 'GET',
                    url: 'api/parse',
                    data: {
                        expr: $('#expr').val()
                    },
                    dataType: 'json',
                    success: function (data) {
                        console.log(data);
                        if (data['status'] === 'ok') {
                            let $result_list = $('#resultList');
                            $result_list.empty();

                            $.each(data['result_list'], function (i, item) {
                                let $title = $('<h4>', {'class': 'mb-3'}).html(item['title']);
                                let $content = $('<p>', {'class': 'text-monospace'}).html(item['content']);
                                $('<li>', {
                                    'class': 'list-group-item'
                                }).append($title).append($content).appendTo($result_list);
                            });

                            let $truthTable = $('#truthTable');
                            $truthTable.empty();

                            let $thead = $('<thead>').appendTo($truthTable);
                            let $tr = $('<tr>').appendTo($thead);

                            $.each(data['var_names'], function (i, varName) {
                                $('<th>', {
                                    scope: 'col',
                                    text: varName
                                }).appendTo($tr);
                            });

                            $('<th>', {
                                scope: 'col',
                                text: $('#expr').val()
                            }).appendTo($tr);

                            let $tbody = $('<tbody>').appendTo($truthTable);

                            $.each(data['truth_table'], function (i, row) {
                                let $tr = $('<tr>').appendTo($tbody);
                                $.each(data['var_names'], function (i, varName) {
                                    let value = row[varName];
                                    $('<td>', {
                                        class: value === true ? 'color-true' : 'color-false',
                                        text: Number(value)
                                    }).appendTo($tr);
                                });

                                $('<td>', {text: Number(row['result'])}).appendTo($tr);
                            });

                            // console.log(data['image']);
                            $('#graph').empty().append(
                              $('<img>', {
                                  src: 'data:image/png;base64,' + data['image'],
                                  class: 'img-fluid'
                              })
                            );

                        } else {
                            alert(data['msg']);
                        }
                    }
                });
            } else {
                let args = {var_num: $('#varNumLabel').text()};
                $('#truthTable input').each(function () {
                    args[$(this).attr('name')] = Number($(this).val());
                });
                console.log(args);
                $.ajax({
                    type: 'GET',
                    url: 'api/from-truth-table',
                    data: args,
                    dataType: 'json',
                    success: function (data) {
                        console.log(data);
                        if (data['status'] === 'ok') {
                            let $result_list = $('#resultList');
                            $result_list.empty();

                            $.each(data['result_list'], function (i, item) {
                                let $title = $('<h4>', {'class': 'mb-3'}).html(item['title']);
                                let $content = $('<p>', {'class': 'text-monospace'}).html(item['content']);
                                $('<li>', {
                                    'class': 'list-group-item'
                                }).append($title).append($content).appendTo($result_list);
                            });
                        } else {
                            alert(data['msg']);
                        }
                    }
                });
            }
        }
    );

    function makeTable(varNum) {
        let $truthTable = $('#truthTable');
        $truthTable.empty();
        let $thead = $('<thead>').appendTo($truthTable);
        let $tr = $('<tr>').appendTo($thead);
        $.each('ABCDEF'.substr(0, varNum).split(''), function (i, varName) {
            $('<th>', {
                scope: 'col',
                text: varName
            }).appendTo($tr);
        });
        $('<th>', {
            scope: 'col',
            text: '表达式的值'
        }).appendTo($tr);

        let $tbody = $('<tbody>').appendTo($truthTable);
        for (let bin = 0; bin < (1 << varNum); ++bin) {
            let $tr = $('<tr>').appendTo($tbody);
            for (let i = varNum - 1; i >= 0; --i) {
                let value = (bin >> i) & 1; // bit from high to low
                $('<td>', {
                    class: value === 1 ? 'color-true' : 'color-false',
                    text: value
                }).appendTo($tr);
            }
            $('<td>').append($('<input>', {
                type: 'number',
                min: '0',
                max: '1',
                step: '1',
                name: 'val' + bin,
            })).appendTo($tr);
        }
    }

    $('#varNum').on('slide', function (event) {
        $('#varNumLabel').text(event.value);
        makeTable(event.value);
    });

    $('#exprForm input[type=radio]').change(function () {
        console.log(this.value);
        if (this.value === 'expr') {
            $('#expr').prop('disabled', false);
            $('#fieldTruth').prop('disabled', true);
            $('#varNum').slider('disable');
        } else if (this.value === 'truth') {
            $('#expr').prop('disabled', true);
            $('#fieldTruth').prop('disabled', false);
            $('#varNum').slider('enable');
            makeTable(Number($('#varNumLabel').text()));
        }
    });

    $('#radioExpr').prop('checked', true).change();
});
