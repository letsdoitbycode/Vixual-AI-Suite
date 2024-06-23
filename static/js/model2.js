
    $(document).ready(function () {
        $('#qaForm').submit(function (event) {
            event.preventDefault();
            var formData = $(this).serialize();
            $.ajax({
                type: 'POST',
                url: '/get_answer',
                data: formData,
                success: function (response) {
                    $('#answer').text(response);
                }
            });
        });
    });