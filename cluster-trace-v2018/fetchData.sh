#!/bin/bash  
  
url='http://aliopentrace.oss-cn-beijing.aliyuncs.com/v2018Traces'

mkdir data
cd data

curl ${url}/machine_meta.tar.gz -o machine_meta.tar.gz
curl ${url}/machine_usage.tar.gz -o machine_usage.tar.gz
curl ${url}/container_meta.tar.gz -o container_meta.tar.gz
curl ${url}/container_usage.tar.gz -o container_usage.tar.gz
curl ${url}/batch_task.tar.gz -o batch_task.tar.gz
curl ${url}/batch_instance.tar.gz -o batch_instance.tar.gz