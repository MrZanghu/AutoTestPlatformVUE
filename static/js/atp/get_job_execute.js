$(function () {
    var badge= document.getElementsByClassName("badge badge-secondary")[0];

    $.getJSON("/atp/get_job_execute/", function (data) {
        if (data["status"] === 200) {
            badge.innerHTML= data["sum"];
        }else {
            badge.innerHTML= 0;
        }
    })
})