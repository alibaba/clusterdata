#!/bin/bash
prepare_dir() {
    mkdir -p data/NodeResourceUsage data/PodMetaInfo data/PodResourceUsage
}

# you can change the start_idx and end_idx to fetch the data you want
fetch_data() {
    # get node resource usage
    get_node_resource_usage() {
        local_path="data/NodeResourceUsage/node_resource_usage"
        remote_paths="NodeResourceUsage/node_resource_usage"
        start_idx=0
        end_idx=215
        for idx in $(seq $start_idx $end_idx); do
            file_name="${local_path}_$idx.tar.gz"
            remote_path="${remote_paths}_$idx.tar.gz"
            url="https://aliopentrace.oss-cn-beijing.aliyuncs.com/v2023UnifiedSchedulerTraces/$remote_path"
            command="wget -c --retry-connrefused --tries=0 --timeout=50 -O $file_name $url"
            $command
        done
    }
    # get pod meta info
    get_pod_meta_info() {
        local_path="data/PodMetaInfo/pod_meta_info"
        remote_paths="PodMetaInfo/pod_meta_info"
        file_name="${local_path}.tar.gz"
        remote_path="${remote_paths}.tar.gz"
        url="https://aliopentrace.oss-cn-beijing.aliyuncs.com/v2023UnifiedSchedulerTraces/$remote_path"
        command="wget -c --retry-connrefused --tries=0 --timeout=50 -O $file_name $url"
        $command
    }
    
    # get pod resource usage
    get_pod_resource_usage() {
        local_path="data/PodResourceUsage/pod_resource_usage"
        remote_paths="PodResourceUsage/pod_resource_usage"
        start_idx=-1
        end_idx=215
        for idx in $(seq $start_idx $end_idx); do
            file_name="${local_path}_$idx.tar.gz"
            remote_path="${remote_paths}_$idx.tar.gz"
            url="https://aliopentrace.oss-cn-beijing.aliyuncs.com/v2023UnifiedSchedulerTraces/$remote_path"
            command="wget -c --retry-connrefused --tries=0 --timeout=50 -O $file_name $url"
            $command
        done
    }
    get_node_resource_usage
    get_pod_meta_info
    get_pod_resource_usage
}
prepare_dir
fetch_data 