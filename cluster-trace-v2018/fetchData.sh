#!/bin/bash  
  
url='http://aliopentrace.oss-cn-beijing.aliyuncs.com/v2018Traces'

mkdir data
cd data

wget -c --retry-connrefused --tries=0 --timeout=50 ${url}/machine_meta.tar.gz
wget -c --retry-connrefused --tries=0 --timeout=50  ${url}/machine_usage.tar.gz
wget -c --retry-connrefused --tries=0 --timeout=50  ${url}/container_meta.tar.gz
wget -c --retry-connrefused --tries=0 --timeout=50  ${url}/container_usage.tar.gz
wget -c --retry-connrefused --tries=0 --timeout=50  ${url}/batch_task.tar.gz
wget -c --retry-connrefused --tries=0 --timeout=50  ${url}/batch_instance.tar.gz