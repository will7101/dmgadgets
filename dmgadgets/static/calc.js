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

                            let $title = $('<h4>',{
                                'class': 'mb-3',
                            }).html(item['title']);

                            let $content = $('<p>',{
                                'class': 'text-monospace',
                            }).html(item['content']);

                            $li.append($title);
                            $li.append($content);

                            $result_list.append($li);
                        });

                        let $truth_table = $('#truthTable');
                        $truth_table.empty();

                        // let thead = document.createElement('thead');
                        // let tr = thead.appendChild(document.createElement('tr'));
                        //
                        // $.each(data['var_names'], function (i, item) {
                        //     let th = document.createElement('th');
                        //     th.setAttribute('scope', 'col');
                        //     th.innerText = item;
                        //     tr.appendChild(th);
                        // });
                        //
                        // let th = document.createElement('th');
                        // th.setAttribute('scope', 'col');
                        // th.innerText = $('#expr').val();
                        // tr.appendChild(th);
                        //
                        // let tbo
                        //
                        // $.each(data['truth_table'], function (i, item) {
                        //     console.log(item);
                        //
                        // });

                        let $thead = $('<thead>');
                        let $tr = $('<tr>');


                    } else {
                        alert(data['msg']);
                    }
                }
            });
        }
    );
});
