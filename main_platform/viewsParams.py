# 用例关联判断
REQUEST_ERROR= 0 # 预请求处理错误
NO_INPUT_NO_OUTPUT= 1 # 无提取入参，无出参
NO_INPUT_Y_OUTPUT= 2 # 无提取入参，有出参
Y_INPUT_NO_OUTPUT= 3 # 有提取入参，无出参
Y_INPUT_Y_OUTPUT= 4 # 有提取入参，有出参

# 请求方式判断
request_method= ["get","post","put"]

# 上传文件创建用例字段
title_list= ["id", "case_name", "uri", "request_method",
              "request_data", "assert_key", "related_case_id",
              "extract_var", "maintainer", "user"]

# 任务状态
job_status= ["0","1","2","3"]