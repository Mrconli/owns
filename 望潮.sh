#######################################################################################

#    望潮

#    控制脚本：Ver:1.0.4
#    本脚本为通用控制脚本，主要目的是使用一个账号一个环境变量
#    通用其他变量未适配多环境变量的的脚本...
#    交流：Mrconli(850810137)     Q群：301723952
#   

#    适配作者：@xzxxn777的望潮脚本使用多环境变量。
#    环境变量：
#        mrconli_WangChao     格式：账号#密码    

#    一个账号一个环境变量  
#    多账号必须新建多个环境变量 

#    updata:2024-10-28
#    写的比较乱，以后再慢慢改.....

#######################################################################################


#----------------------------自定义区----------------------------#
MAX_CONCURRENT_JOBS=1         # 设置并发数（可以根据需要自定义）
CK_ENV="mrconli_WangChao"     # 这是一个你自己收集变量设置的环境变量名，必须和自己用的环境变量名保持一致
CK="WangChao"                 # 原始脚本使用的环境变量名
SP_NAME="望潮.js"             # 下载适配脚本后保存的文件名，需要包含后缀
SP_FILE="https://raw.githubusercontent.com/xzxxn777/Surge/refs/heads/main/Script/WangChao/WangChao.js"
                              # 雪乃脚本仓库地址，自行修改 
ENV_SCRIPT="./env/WangChao_env.js"      # 适配环境变量，特殊脚本需要自定义
ENV_FILE="${CK_ENV}_list.json"          # 理论不需要更改此行
FENGE="&"                               # 适配环境变量脚本用的参数，不要改
TASK_SCRIPT="./solo/$SP_NAME"           # 定义原始脚本的路径，不要修改

#----------------------------自定义区----------------------------#


# 删除脚本，网络不好的可以注释掉，手动更新
rm -rf "./solo/$SP_NAME"

download_wc() {
    local local_destination="$PWD/solo"
    local local_file="$local_destination/$SP_NAME"
    echo "开始下载适配脚本文件到$local_destination目录"
    mkdir -p "$local_destination"
    if curl -sS -o "$local_file" "$SP_FILE"; then
        echo "下载完成，如需重新下载或更新请先删除该文件"
        if [ -f "$local_file" ]; then
            chmod +x "$local_file"
        fi
    else
        echo "下载失败，请检查网络或SP_FILE的参数值！！！"
        exit 1  # 下载失败，停止脚本执行
    fi
}

if [ -f "$TASK_SCRIPT" ]; then
    echo "已找到适配脚本文件，开始运行..."
    chmod +x "$TASK_SCRIPT"
else
    echo "未找到适配脚本文件，尝试拉取远程仓库..."
    download_wc
fi


echo "
=============================================
↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

👉望潮  Ver:1.0.4 

#    适配作者：@xzxxn777望潮脚本使用多环境变量。
#    BY：Mrconli(850810137)
#    updata:2024-10-28

↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
=============================================
"


# 删除历史缓存ck文件
if [ -f "$ENV_FILE" ]; then
    rm -f "$ENV_FILE"
fi

# 生成环境变量存储文件
export env_json="$CK_ENV"
export delimiter="$FENGE"
node "$ENV_SCRIPT"

# 检查缓存ck文件是否存在
if [ ! -f "$ENV_FILE" ]; then
    echo "缓存环境变量文件不存在！"
    exit 1
fi

# 读取缓存ck文件中的每一行
while IFS= read -r line || [ -n "$line" ]; do  # 处理空行
    if [ -z "$line" ]; then
        continue  # 跳过空行
    fi

    # 设置环境变量
    export "$CK"="$line"

    # 启动任务并在后台执行
    echo "
=============================================
遍历缓存CK，执行脚本[${TASK_SCRIPT}]...
============================================="

    # 输出当前正在执行的环境变量
    echo "🎉🎉🎉正在执行账号: ${CK}='${line}'"
    node "$TASK_SCRIPT" &  # 在后台执行脚本

    # 控制并发数
    while [ "$(jobs -r | wc -l)" -ge "$MAX_CONCURRENT_JOBS" ]; do
        sleep 1  # 等待，直到有空闲的后台进程
    done

done < "$ENV_FILE"

# 等待所有子进程结束
wait

# 清理缓存ck文件
rm -f "$ENV_FILE"

echo "
=============================================
清理缓存，所有CK任务执行完成...
=============================================
"