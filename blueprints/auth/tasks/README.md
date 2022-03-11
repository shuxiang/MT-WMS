## 异步任务
导入导出的任务实现api都放在这里


## API

### 导出api异步任务创建
url： POST /async/table_export
参数：
```
        GET 参数： 
                入库订单导出, 参数跟`入库订单`的导出功能一样 
                /api/async/table_export?_format=excel&startDate=2018-01-25&endDate=2018-05-24&q_type=order_q
                参数，出库单导出, 参数跟`出库订单`的导出功能一样
                /api/async/table_export?_format=excel&startDate=2018-05-09&endDate=2018-05-23&q_type=order_q&_start=0&_limit=10 
                参数，总装箱单导出, 参数跟`总装箱单导出`的导出功能一样
                /api/async/table_export?_format=excel&startDate=2018-05-09&endDate=2018-05-23&q_type=order_q&_start=0&_limit=10 
                库存单导出，参数跟`库位库存`菜单里的导出功能一样
                /api/async/table_export?_format=excel&startDate=2018-01-25&endDate=2018-05-24&q_type=order_q
        POST 参数：
                除了GET参数外，还需要传递post json参数：
                {'name': 'test-stockout-export', // excel名
                'task_type':'export', 
                'func': 'app.mod_export.service.stockout_order_export:export_stockout_file', 
                'func_name': u'出库单导出'}
                func和func_name可以通过GET `/api/async/table_export` 获取，会返回一个列表
```

响应：
        {'status': 'success', 'msg':'ok', 'data': {// 异步任务数据}}

### 异步任务状态
url: /async/status/<task_id>

响应：
        {'status': 'success', 'msg':'ok', 'data': {// 任务状态}}

### 文件下载
url: /async/download/<task_id>

响应：
        当任务状态完成时，返回文件。

### 异步任务列表
url: /async
参数： 参数用restless的q参数
响应：
        restless响应