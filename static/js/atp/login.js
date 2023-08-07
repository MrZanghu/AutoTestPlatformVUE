$(function () {
    $("img").click(function () {
        $(this).attr("src","/atp/get_code/?t="+Math.random())
    })
})