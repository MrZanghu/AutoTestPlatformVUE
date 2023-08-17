function selectOrCancelAll() {
    var $all_select = document.getElementById("all_select").checked;
    var $testsuite_list = document.querySelectorAll('tbody input');

    if ($all_select) {
        // 全选
        for (var i = 0; i < $testsuite_list.length; i++) {
            $testsuite_list[i].checked = true;
        }
    } else
        //取消全选
    {
        for (var j = 0; j < $testsuite_list.length; j++) {
            $testsuite_list[j].checked = false;
        }
    }
}

function ischecked() {
    var $ex_suite = document.getElementsByName("ex_suite");
    var $ex_time = document.getElementsByName("ex_time").item(0).value;

    if ($ex_suite) {
        $.getJSON("/atp/test_suite/atp/get_job_name/", {"ex_time": $ex_time}, function (data) {
            if (data["status"] === 2001) {
                alert("当前时间已存在任务，请一分钟后再试");
                // 重复任务但未勾选用例的情况，导致判重与勾选判断相互调用，以判重优先
                return false;
            } else {
                var $allCheck = document.getElementsByName("testsuite_list");
                //遍历每一个复选框，为true则上传
                var checks = false;

                for (var i = 0; i < $allCheck.length; i++) {
                    if ($allCheck[i].checked === true) {
                        alert("点击确认执行集合，跳转至执行结果页等待");
                        checks= true;
                        return true;
                    }
                }

                if (checks=== false){
                    alert("请选择要执行的测试集合");
                }
            }
        })
    }
}