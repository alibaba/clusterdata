#!/bin/bash
prepare_dir() {
    mkdir -p data/NodeMetrics data/MSMetrics data/MSRTMCR data/CallGraph
}

# $1 = start_day, $2 = end_day
# $3 = start_hour, $4 = end_hour
fetch_data() {
    declare -a file_names=(
        "data/CallGraph/CallGraph" "data/MSMetrics/MSMetrics"
        "data/NodeMetrics/NodeMetrics" "data/MSRTMCR/MSRTMCR"
    )
    declare -a remote_paths=(
        "CallGraph/CallGraph" "MSMetricsUpdate/MSMetricsUpdate"
        "NodeMetricsUpdate/NodeMetricsUpdate" "MCRRTUpdate/MCRRTUpdate"
    )
    declare -a ratios=(3 30 720 3)
    start_hour=$(($1 * 24 * 60 + $3 * 60))
    end_hour=$(($2 * 24 * 60 + $4 * 60))
    for i in $(seq 0 3); do
        start_idx=$(($start_hour / ${ratios[$i]}))
        end_idx=$(($end_hour / ${ratios[$i]} - 1))
        if [[ $i == 2 && $(($end_hour % ${ratios[$i]})) != 0 ]]; then
            end_idx=$(($end_idx + 1))
        fi
        for idx in $(seq $start_idx $end_idx); do
            file_name="${file_names[$i]}_$idx.tar.gz"
            remote_path="${remote_paths[$i]}_$idx.tar.gz"
            url="https://aliopentrace.oss-cn-beijing.aliyuncs.com/v2022MicroservicesTraces/$remote_path"
            command="wget -c --retry-connrefused --tries=0 --timeout=50 -O $file_name $url"
            $command
        done
    done
}

for ARGUMENT in "$@"; do
    KEY=$(echo $ARGUMENT | cut -f1 -d=)

    KEY_LENGTH=${#KEY}
    VALUE="${ARGUMENT:$KEY_LENGTH+1}"

    export "$KEY"="$VALUE"
done
start_day=$(expr $(echo $start_date | cut -f1 -dd) + 0)
start_hour=$(expr $(echo $start_date | cut -f2 -dd) + 0)
end_day=$(expr $(echo $end_date | cut -f1 -dd) + 0)
end_hour=$(expr $(echo $end_date | cut -f2 -dd) + 0)
prepare_dir
fetch_data $start_day $end_day $start_hour $end_hour