// 引入 fs 模块，用于文件操作
const fs = require('fs');

// 获取环境变量
const env = process.env;

// 定义需要拼接的环境变量名和分隔符
const ckPrefix = process.env.env_json; 
const fg = process.env.delimiter; 

// 获取匹配的环境变量并拼接
const concatenatedCK = Object.keys(env)
    .filter(key => key === ckPrefix) // 精确匹配环境变量名
    .map(key => env[key])
    .join(fg); // 使用分隔符拼接

// 动态生成文件名
const filePath = `${ckPrefix}_list.json`;

// 将结果写入文件并处理可能的错误
fs.writeFile(filePath, concatenatedCK, 'utf8', (err) => {
    if (err) {
        return console.error('写入文件时出错:', err);
    }

    // 读取文件内容，处理符号并更新
    fs.readFile(filePath, 'utf8', (err, data) => {
        if (err) {
            return console.error('读取文件时出错:', err);
        }

        // 用换行符替换所有的 fg 字符，并在末尾添加换行符
        const updatedData = data.replace(new RegExp(fg, 'g'), '\n') + '\n';

        // 替换所有的 # 为 &
        const finalData = updatedData.replace(/#/g, '&');

        // 将修改后的内容写回文件
        fs.writeFile(filePath, finalData, 'utf8', (err) => {
            if (err) {
                return console.error('写入文件时出错:', err);
            }
            console.log(`缓存文件 ${filePath} 创建成功......`);
        });
    });
});
