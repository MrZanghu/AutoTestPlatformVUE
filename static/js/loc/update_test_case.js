function check() {
    // 提交数据时进行验证
    var $case_name_input = $("#case_name_input");
    var $case_name_info = $("#case_name_info");

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


    var flag = true;
    var list = [$case_name_input,$request_data_input, $uri_input,
         $maintainer_input,  $request_method_input, $status_input,];
    var list2= [$case_name_info,$request_data_info,$uri_info,
        $maintainer_info,$request_method_info,$status_info];

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
