function addtmpParam() {
    var Table = document.getElementById("interfaceParam");
    var rowsNum = Table.rows.length - 1;
    NewRow = Table.insertRow(); //添加行
    ID = NewRow.insertCell(); //添加列
    ID.style.textAlign = "center";
    LocationPath = NewRow.insertCell();
    Method = NewRow.insertCell();
    Parameter = NewRow.insertCell();
    Action = NewRow.insertCell();
    Expected = NewRow.insertCell();
    operate = NewRow.insertCell();
    ID.innerHTML = rowsNum + 1;
    LocationPath.innerHTML = "<input id=LocationPath" + (rowsNum + 1) + " style='width: 100%;' type='text' />";


    var methods = [
        {value: "click(点击)"},
        {value: "sendkeys(输入)"},
        {value: "clear(清除输入框)"},
        {value: "isselect(是否已经被选择)"},
        {value: "-----------------------------------"},

        {value: "selectbytext(下拉框的内容)"},
        {value: "selectbyindex(下拉框的下标)"},
        {value: "-----------------------------------"},

        {value: "alertaccept(点击确认)"},
        {value: "alertdismiss(点击取消)"},
        {value: "alertgettext(获取弹出框内容)"},
        {value: "-----------------------------------"},

        {value: "gettext(获取文本属性)"},
        {value: "gettagname(获取标签类型)"},
        {value: "getattribute(获取指定属性值)"},
        {value: "-----------------------------------"},

        {value: "mouselkclick(模拟鼠标左键单击)"},
        {value: "mouserkclick(模拟鼠标右键单击)"},
        {value: "mousedclick(模拟鼠标双击)"},
        {value: "mouseclickhold(模拟鼠标左键长按)"},
        {value: "mouserelease(模拟鼠标长按后释放)"},
    ];

    Method.innerHTML = "<input id=Method" + (rowsNum + 1) + " style='width: 100%;' type='text' list=Melist" + (rowsNum + 1) + ">" +
        "<datalist id=Melist" + (rowsNum + 1) + "></datalist>";

    var ml = document.getElementById("Melist" + (rowsNum + 1));
    for (var i = 0; i < methods.length; i++) {
        var mds = methods[i];
        var op = document.createElement("option");
        op.setAttribute("value", mds.value);
        ml.appendChild(op);
    }

    Parameter.innerHTML = "<input id=Parameter" + (rowsNum + 1) + " style='width: 100%;' type='text' />";

    var actions = [
        {value: "open(打开)"},
        {value: "wait(等待)"},
        {value: "back(后退)"},
        {value: "forward(前进)"},
        {value: "refresh(刷新)"},
        {value: "-----------------------------------"},

        {value: "screenshot(截图)"},
        {value: "gettitle(获取窗口标题)"},
        {value: "closewindow(关闭当前页签)"},
        {value: "maximizewindow(窗口最大化)"},
    ];

    Action.innerHTML = "<input id=Action" + (rowsNum + 1) + " style='width: 100%;' type='text' list=Actlist" + (rowsNum + 1) + ">" +
        "<datalist id=Actlist" + (rowsNum + 1) + "></datalist>";

    var acl = document.getElementById("Actlist" + (rowsNum + 1));
    for (var j = 0; j < actions.length; j++) {
        var acs = actions[j];
        var aop = document.createElement("option");
        aop.setAttribute("value", acs.value);
        acl.appendChild(aop);
    }

    Expected.innerHTML = "<input id=Expected" + (rowsNum + 1) + " style='width: 100%;' type='text' />";
    operate.innerHTML = '<div id=operate' + (rowsNum + 1) + ' style="text-align: center">' +
        '<a style="cursor:pointer;color:red;"  onclick="deleteInterfaceParam();">删除</a>' +
        '</div>';
}


function deleteInterfaceParam() {
    var td = event.srcElement; // 通过event.srcElement 获取激活事件的对象 td
    var key = td.parentElement.parentElement.parentNode.rowIndex;  //获取行索引
    document.getElementById('interfaceParam').deleteRow(key); //删除

    //以下操作是保存删除数据后table中序号重新生成且有序
    var table = document.getElementById("interfaceParam");
    var tableRows = table.rows;
    //保存剩余表中数据到RowArr
    var RowArr = new Array();
    for (var i = 1; i < tableRows.length; i++) {
        var arr = new Array();
        var tempKey = tableRows[i].cells[0].innerText;
        arr.push($("#LocationPath" + tempKey).val());
        arr.push($("#Method" + tempKey).val());
        arr.push($("#Parameter" + tempKey).val());
        arr.push($("#Action" + tempKey).val());
        arr.push($("#Expected" + tempKey).val());
        RowArr.push(arr);
    }

    //删除表中数据
    if (table !== "undefined") {
        while (table.hasChildNodes()) {
            table.removeChild(table.lastChild);
        }
    }

    //重新生成表数据
    for (var i = 0; i < RowArr.length + 1; i++) {
        if (i == 0) {
            //生成表头
            NewRow = table.insertRow(); //添加行
            ID = NewRow.insertCell(); //添加列
            ID.style.textAlign = "center";
            ID.style.width = "5%";
            ID.innerHTML = "步骤编号";

            LocationPath = NewRow.insertCell();
            LocationPath.style.width = "20%";
            LocationPath.style.textAlign = "center";
            LocationPath.innerHTML = "定位路径";

            Method = NewRow.insertCell();
            Method.style.width = "17.5%";
            Method.style.textAlign = "center";
            Method.innerHTML = "方法|操作";

            Parameter = NewRow.insertCell();
            Parameter.style.width = "15%";
            Parameter.style.textAlign = "center";
            Parameter.innerHTML = "传入参数";

            Action = NewRow.insertCell();
            Action.style.width = "12%";
            Action.style.textAlign = "center";
            Action.innerHTML = "步骤动作";

            Expected = NewRow.insertCell();
            Expected.style.textAlign = "center";
            Expected.innerHTML = "预期结果";

            operate = NewRow.insertCell();
            operate.style.width = "10%";
            operate.style.textAlign = "center";
            operate.innerHTML = "操作";
        } else {
            //生成表数据
            NewRow = table.insertRow(); //添加行
            ID = NewRow.insertCell(); //添加列
            ID.style.textAlign = "center";
            LocationPath = NewRow.insertCell();
            Method = NewRow.insertCell();
            Parameter = NewRow.insertCell();
            Action = NewRow.insertCell();
            Expected = NewRow.insertCell();
            operate = NewRow.insertCell();
            ID.innerHTML = i;
            var rowsNum = i - 1;

            LocationPath.innerHTML = "<input id=LocationPath" + (rowsNum + 1) + " style='width: 100%;' type='text' value=" + RowArr[rowsNum][0] + ">";
            Method.innerHTML = "<input id=Method" + (rowsNum + 1) + " style='width: 100%;' type='text' value=" + RowArr[rowsNum][1] + " >";
            Parameter.innerHTML = "<input id=Parameter" + (rowsNum + 1) + " style='width: 100%;' type='text' value=" + RowArr[rowsNum][2] + ">";
            Action.innerHTML = "<input id=Action" + (rowsNum + 1) + " style='width: 100%;' type='text' value=" + RowArr[rowsNum][3] + ">";
            Expected.innerHTML = "<input id=Expected" + (rowsNum + 1) + " style='width: 100%;' type='text' value=" + RowArr[rowsNum][4] + ">";
            operate.innerHTML = '<div id=operate' + (rowsNum + 1) + ' style="text-align: center">' +
                '<a style="cursor:pointer;color:red;"  onclick="deleteInterfaceParam();">删除</a>' +
                '</div>';
        }
    }
}


$("#subbtn").click(function () {
    var table = document.getElementById("interfaceParam");
    var case_id = document.getElementById("case_id").innerText;
    // 获取span标签的内容

    var tableRows = table.rows;
    var RowArr = new Array();
    for (var i = 1; i < tableRows.length; i++) {
        var arr = new Array();
        var tempKey = tableRows[i].cells[0].innerText;
        arr.push($("#LocationPath" + tempKey).val());
        arr.push($("#Method" + tempKey).val());
        arr.push($("#Parameter" + tempKey).val());
        arr.push($("#Action" + tempKey).val());
        arr.push($("#Expected" + tempKey).val());
        RowArr.push(arr);
    }

    $.getJSON("/sea/update_test_case_interface/", {
        "steps": JSON.stringify(RowArr),
        "case_id": case_id
    }, function (data) {
        if (data["status"] === 2000) {
            window.open("/sea/test_case/", target = "_self");
        } else {
            alert(data["msg"]);
        }
    });
});