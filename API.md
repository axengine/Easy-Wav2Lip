# 数字人Alpha API v0.1.0

## 获取配置
- GET /v1/config

```
{
    "face": [ 内置数字人
        {
            "name": "Face 1", 
            "path": "static/face/1.mp4"
        }
    ],
    "speaker": [ 内置语音风格
        {
            "name": "Speaker 1",
            "path": "static/speaker/1.wav"
        }
    ]
}
```

## 创建任务：生成数字人视频
- POST /v1/process

| 参数名 | 参数类型 | 说明 |
| --- | --- | --- |
| video | form_data.file | 上传数字人视频，要求：视频面部清洗，无大幅度动作，每一帧都要求人物面部存在，人物可以不说话 |
| audio | form_data.file | 数字人说话声音 |
| face | form_data.text | 选择的数字人path，例如：static/face/1.mp4。如果传了video该字段会被忽略 |
| text | form_data.text | 待生成语音的文本，如果传了audio，该自动以及后面的字段会被忽略 |
| language | form_data.text | 文本语言，例如:zh-cn/en，使用TTS时必传 |
| speaker | form_data.text | TTS语音风格，例如：static/speaker/1.wav，使用TTS时必传|

- 返回：任务Id

## 查询任务结果
- GET /v1/result?taskId=xxxx
- 返回
```
{
    "begin": 1711767757.9057734,任务开始时间
    "elapse": 75.47078704833984,任务持续时长
    "end": 1711767833.3765604,任务完成时间，未完成时没有
    "result": "static/output/d50d4e3e-b037-4df5-955b-6267c31d183a.mp4",生成视频路径，未完成时没有
    "taskId": "d50d4e3e-b037-4df5-955b-6267c31d183a"
}
```
