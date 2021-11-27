$(document).ready(function () {
    $("body").on('keyup', '#searchbar', function (e) {
        e.preventDefault();
        let text = $("#searchbar").val();
        let html = "";
        if (text.length >= 2) {
            $.ajax({
                url: 'getStockList',
                data: {
                    keyword: text
                },
                success: function (response) {
                    if(response.status == 'success') {
                        let data = response.data;
                        console.log(data)
                        $.each(JSON.parse(data), function (key, value) {
                            html += '<li role="presentation"><a target="_blank" role="menuitem" tabindex="-1" href="companyInfo/'+value.pk+'" class = "eventLink">' + value.fields.name + ' (' +value.fields.code+')</a></li>'; 
                        });
                    } else {
                        html += '<li role="presentation"><a role="menuitem" tabindex="-1" href="#">'+response.message+'</a></li>';
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
});