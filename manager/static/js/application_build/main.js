/**
 * Created by brujitos on 15-02-26.
 */

define(function (require) {
    $('#new-build').on('click', function (e) {
        e.preventDefault();

        var postUrl = $('#new-build-form').attr('action');
        var branch = $('#id_branch').val();

        var csrfToken = $("#new-build-form input[name=csrfmiddlewaretoken]").val();

        if (branch.length > 0) {
            $.ajax({
                type: "POST",
                url: postUrl,
                data: { branch: branch, csrfmiddlewaretoken: csrfToken }
            })
                .done(function (response) {
                    if (response.status == 0) {
                        $('#new-build').hide();
                        $("#message").show();
                        $("#build-log").show();

                        $("#message").addClass('alert-success');
                        $("#message").text(response.message);

                        var pollUrl = response.build_image_logs_url;

                        var pollInterval = setInterval(function () {
                            $.ajax({
                                type: "GET",
                                url: pollUrl
                            }).done(function (response) {
                                pollUrl = response.build_image_logs_url;
                                if (response.status == 0) {
                                    $.each(response.data, function (index, content) {
                                        $("#build-log div").prepend(JSON.stringify(content) + "<br/>");
                                    });
                                } else {
                                    // Cancel timer
                                    clearInterval(pollInterval);
                                    $("#message").text("Finished building application");

                                    if (response.status == 3) {
                                        $("#message").removeClass('alert-success');
                                        $("#message").addClass('alert-danger');
                                    }
                                }
                            });
                        }, 3000)
                    }
                });
        }


        return false;
    })
});
