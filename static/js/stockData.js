$(document).ready(function () {
    $("body").on('keyup', '#searchbar', function (e) {
        e.preventDefault();
        let text = $("#searchbar").val();
        let html = "";
        if (text.length >= 2) {
            $.ajax({
                url: '/getStockList',
                data: {
                    keyword: text
                },
                success: function (response) {
                    if (response.status == 'success') {
                        let data = response.data;
                        console.log(data)
                        $.each(JSON.parse(data), function (key, value) {
                            html += '<li role="presentation"><a target="_blank" role="menuitem" tabindex="-1" href="companyInfo/' + value.pk + '" class = "eventLink">' + value.fields.name + ' (' + value.fields.code + ')</a></li>';
                        });
                    } else {
                        html += '<li role="presentation"><a role="menuitem" tabindex="-1" href="#">' + response.message + '</a></li>';
                    }
                    $("#displist").html(html);
                    $("#displist").css("display", "block");
                },
                error: function () {
                    alert("Something went wrong. Please try again!")
                }
            });
        } else {
            $("#displist").html("");
            $("#displist").css("display", "none");
        }
    });

    $("body").on('click', '#buyStock', function (e) {
        $("#myModal").css("display", "block")
        $("#placeOrder").text("Buy")
        $("#placeOrder").attr('order', 'buy')
    });

    $("body").on('click', '#sellStock', function (e) {
        $("#myModal").css("display", "block")
        $("#placeOrder").text("Sell")
        $("#placeOrder").attr('order', 'sell')
    });

    $("body").on('click', '#closeModal', function (e) {
        $("#stockQty").val('');
        $("#stockQty").css('border', '');
        $("#myModal").css("display", "none")
        $("#placeOrder").data('order', '')
        $("#placeOrder").text("")
        $('.successmessage').text(''),
        $('.failuremessage').text('')
    });

    $("body").on('click', '#placeOrder', function (e) {
        let qty = $("#stockQty").val();
        if (qty == '' || qty <= 0 || qty % 1 != 0) {
            $("#stockQty").css('border', '1px solid red');
            return;
        }
        $("#stockQty").css('border', '');
        if ($("#placeOrder").attr('order') == 'buy') {
            e.preventDefault();
            let text = $("#companycode").text();
            $.ajax({
                url: '/buyStock',
                data: {
                    code: text,
                    quantity: qty
                },
                beforeSend: function() {
                    $('.successmessage').text(''),
                    $('.failuremessage').text('')
                },
                success: function (response) {
                    if (response.status == 'success') {
                        $('.successmessage').text(response.message)
                    } else {
                        $('.failuremessage').text(response.message)
                    }
                },
                error: function () {
                    alert("Something went wrong. Please try again!")
                }
            });
        } else {
            e.preventDefault();
            let text = $("#companycode").text();
            $.ajax({
                url: '/sellStock',
                data: {
                    code: text,
                    quantity: qty
                },
                beforeSend: function() {
                    $('.successmessage').text(''),
                    $('.failuremessage').text('')
                },
                success: function (response) {
                    if (response.status == 'success') {
                        $('.successmessage').text(response.message)
                    } else {
                        $('.failuremessage').text(response.message)
                    }
                },
                error: function () {
                    alert("Something went wrong. Please try again!")
                }
            });
        }
    });
});