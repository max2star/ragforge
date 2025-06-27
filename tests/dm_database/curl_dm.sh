./disql
conn
RAGFLOW001
Sysdba@123
SELECT table_name FROM user_tables;
select * from "user";
select * from "user" where email=='M@M.test';
select id from "user" where email=='M@M.test';
select * from tenant_llm where tenant_id=='795107284b3211f0b11e7e78d9ed0d3b' and llm_name=='qwen_large';
update tenant_llm set max_tokens=16384 where tenant_id=='795107284b3211f0b11e7e78d9ed0d3b' and llm_name=='qwen_large';
select * from llm where llm_name=='qwen_large' and fid='OpenAI-API-Compatible';
