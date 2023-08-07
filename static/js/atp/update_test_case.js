$(function () {
    var $belong_module_input = $("#belong_module_input");
    var $belong_project_input = $("#belong_project_input");

    $belong_module_input.change(function () {
        var module = $belong_module_input.val().trim(); // trim去空格
        var project = $belong_project_input.val().trim();
        if (module) {
            $.getJSON('/atp/check_module_belong_project/',
                {"belong_module": module, "belong_project": project}, function (data) {
                    var $belong_module_info = $("#belong_module_info");
                    if (data.code === 901) {
                        $belong_module_info.html(data["msg"]).css("color", "red");
                    } else {
                        $belong_module_info.html(data["msg"]).css("color", "");
                    }
                })
        }
    });
})

function check() {
    // 提交数据时进行验证
    var $case_name_input = $("#case_name_input");
    var $case_name_info = $("#case_name_info");

    var $belong_project_input = $("#belong_project_input");
    var $belong_project_info = $("#belong_project_info");

    var $belong_module_input = $("#belong_module_input");
    var $belong_module_info = $("#belong_module_info");
    var $belong_module_info_color = $belong_module_info.css("color");

    var $request_data_input = $("#request_data_input");
    var $request_data_info = $("#request_data_info");

    var $uri_input = $("#uri_input");
    var $uri_info = $("#uri_info");

    var $maintainer_input = $("#maintainer_input");
    var $maintainer_info = $("#maintainer_info");

    var $request_method_input = $("#request_method_input");
    var $request_method_info = $("#request_method_info");

    var $status_input = $("#status_input");
    var $status_info = $("#status_info");

    var $user_input = $("#user_input");
    var $user_info = $("#user_info");

    var flag = true;
    var list = [$case_name_input, $belong_project_input, $belong_module_input, $request_data_input, $uri_input,
         $maintainer_input,  $request_method_input, $status_input,
         $user_input];
    var list2= [$case_name_info,$belong_project_info,$belong_module_info,$request_data_info,$uri_info,
        $maintainer_info,$request_method_info,$status_info,$user_info];

    if ($belong_module_info_color === 'rgb(255, 0, 0)') {
        flag = false;
    }

    for (i = 0; i < list.length; i++) {
        if (!list[i].val().trim()) {
            list2[i].html("此项不能为空").css("color", "red");
            flag= false;
        }
    }

    if (flag === false) {
        return false;
    } else {
        return true;
    }
}
