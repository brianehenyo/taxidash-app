(function () {

    window.setTimeout(function () {
        $.ajax({
            type: 'post',
            url: '/discover/refresh/',
            data: {
                'latitude': $('#hdnLatitude').val(),
                'longitude': $('#hdnLongitude').val(),
                'csrfmiddlewaretoken': window.CSRF_TOKEN
            },
            success: function (data) {
                $(".main").append(data.trip_cards);
                $(".loader").css('visibility', 'hidden');
                console.log("SUCCESS");

                var app = {
                    isLoading: true,
                    visibleCards: {},
                    location: [],
                    spinner: document.querySelector('.loader'),
                    cardTemplate: document.querySelector('.cardTemplate'),
                    container: document.querySelector('.main'),
                    addDialog: document.querySelector('.dialog-container')
                };

                var selectedTrip = "";

                //Add event listener for all cards
                trip_cards = $('.card');
                trip_cards.each(function (index) {
                    $(this).on("click", function () {
                        selectedTrip = $(this).attr('id');
                        app.toggleAddDialog(true, $(this).find(".organizer").text(), selectedTrip);
                    });
                });

                document.getElementById('butCancel').addEventListener('click', function () {
                    // Close the add new city dialog
                    app.toggleAddDialog(false);
                });

                app.toggleAddDialog = function (visible, organizer, trip_id) {
                    if (visible) {
                        $(".dialog-organizer").text(organizer);
                        $("#trip_id").val(trip_id);

                        if (sessionStorage.getItem('taxidash_user')) {
                            $("#txtPassenger").val(sessionStorage.getItem('taxidash_user'));
                        }

                        $('#butJoin').on('click', function () {
                            // Record name as cookie
                            var passenger = $("#txtPassenger").val();
                            if (!sessionStorage.getItem('taxidash_user')) {
                                sessionStorage.setItem('taxidash_user', passenger);
                            } else if (sessionStorage.getItem('taxidash_user') !== passenger) {
                                sessionStorage.setItem('taxidash_user', passenger);
                            }

                            app.toggleAddDialog(false);
                        });

                        app.addDialog.classList.add('dialog-container--visible');
                    } else {
                        app.addDialog.classList.remove('dialog-container--visible');
                    }
                };
            },
            error: function (xhr, status, error) {
                console.log(error);
            }
        });
    }, 5000);

})();