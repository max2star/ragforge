echo "现在测试千问LLM大模型"
curl -i -X POST http://118.193.126.254:1025/v1/chat/completions \
-H 'Content-Type: application/json' \
-d '{
"model": "qwen_large",
"max_tokens": 1000,
"stream": false,
"messages": [{"role": "user","content": "你是谁？"}]
}'
echo "\n"
echo  "BGE-M3测试脚本"
curl http://118.193.126.254:8080/embed \
    -X POST \
    -d '{"inputs":"What is Deep Learning?"}' \
-H 'Content-Type: application/json'

echo "\n"
echo '现在测试VL 32B模型'
curl http://118.193.126.254:3525/v1/chat/completions -d ' {
"model": "qwen2.5-vl-32b-instruct",
"messages": [{
"role": "user",
"content": [
{"type": "image_url", "image_url": "/model/hua.jpg"},
{"type": "text", "text": "请描述下图片内容"}
]
}],
"max_tokens": 512,
"do_sample": true,
"repetition_penalty": 1.00,
"temperature": 0.01,
"top_p": 0.001,
"top_k": 1
}'

echo "\n"
echo "Rerank测试脚本"
curl 118.193.126.254:1111/rerank \
-X POST \
-d '{"query":"please introduce youself.", "texts": ["Deep Learning is a sub-filed of Machine Learning.", "Deep learning is a country."]}' \
-H 'Content-Type: application/json'

echo "\n"
echo "70B测试脚本"
curl -H "Accept: application/json" -H "Content-type: application/json"  -X POST -d '{
 "model": "DeepSeek-R1-Distill-Llama-70B",
 "messages": [{
  "role": "system",
  "content": "You are a helpful assistant."
 },
 {
  "role": "user",
  "content": "思考下先有蛋还是现有鸡？"
 }],
 "max_tokens": 1000,
 "presence_penalty": 1.03,
 "frequency_penalty": 1.0,
 "seed": null,
 "temperature": 0.5,
 "top_p": 0.95,
 "stream": false
}' http://118.193.126.254:1025/v1/chat/completions

echo "\n"
echo "32B测试脚本"
curl -H "Accept: application/json" -H "Content-type: application/json"  -X POST -d '{
    "model": "DeepSeek-R1-Distill-Qwen-32B",
    "messages": [
        {"role": /"system", "content": "你是一个导游"},
        {"role": "user", "content": "你好，我最近想去四川旅游，有什么地方推荐吗"}
    ],
    "stream": false,
    "max_tokens": 1024,
    "presence_penalty": 1.03,
    "frequency_penalty": 1.0,
    "repetition_penalty": 1.0,
    "temperature": 0.5,
    "top_p": 0.95,10
    "top_k": 10,
    "seed": null,
    "stop": ["stop1", "stop2"],
    "include_stop_str_in_output": false,
    "skip_special_tokens": true,min
    "ignore_eos": false
}' http://118.193.126.254:1025/v1/chat/completions
