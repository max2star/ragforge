echo "现在测试千问LLM大模型"
curl -i -X POST http://118.193.126.254:1025/v1/chat/completions -H 'Content-Type: application/json' -d '@qwen_llm.json'
echo "\n"

echo  "现在测试BGE-M3向量化模型"
curl http://118.193.126.254:8080/embed -X POST -d '@./embedding.json' -H 'Content-Type: application/json'
echo "\n"

echo '现在测试VL 32B视觉大模型'
date
curl -X POST -H 'Content-Type: application/json' http://118.193.126.254:3525/v1/chat/completions -d '@./qwen_vlm.json'
date
echo "\n"

echo "现在测试Rerank模型"
curl 118.193.126.254:1111/rerank -X POST  -d "@./rerank.json" -H 'Content-Type: application/json'
echo "\n"

echo "现在测试DeepSeek 70B大模型"
curl -H "Accept: application/json" -H "Content-type: application/json"  -X POST -d '@./deepseek_70b_llm.json' http://118.193.126.254:1025/v1/chat/completions
echo "\n"

#本环境不使用 32B Deepseek
#echo "现在测试DeepSeek 32B大模型"
#curl -H "Accept: application/json" -H "Content-type: application/json"  -X POST -d '@./deepseek_32b_llm.json' http://118.193.126.254:1025/v1/chat/completions
#echo "\n"
