/**
 * new Env("金典satine-微信小程序")
 * cron 10 7 * * * jindian.js
 * Show: 签到 + 种树
 * 变量名: jindian_wx
 * 变量值:
 * jdshop.yili.com 域名headers 中 accesstoken的值
 * scriptVersionNow = "0.0.1";
 */

const plantJsonIdList = [{
    plantJsonId: 700001,
    name: "紫花苜蓿",
    needTime: 6,//6分钟成熟
    needWater: 10,//消耗10水滴
    reward: 90//获得90金币
}, {
    plantJsonId: 700002,
    name: "黑麦草",
    needTime: 120,
    needWater: 20,
    reward: 180
}, {
    plantJsonId: 700003,
    name: "羊草",
    needTime: 180,
    needWater: 40,
    reward: 360
}, {
    plantJsonId: 700004,
    name: "皇竹草",
    needTime: 360,
    needWater: 80,
    reward: 880
}]
const plantJsonId = plantJsonIdList[0]
const $ = new Env("金典satine-微信小程序");
const ckName = "jindian_wx";
const Notify = 1; //0为关闭通知,1为打开通知,默认为1
let envSplitor = ["@", "\n"]; //多账号分隔符
let strSplitor = '&'; //多变量分隔符
let scriptVersionNow = "0.0.1";
let msg = "";

async function start() {
    await getVersion("smallfawn/Note@main/JavaScript/test_v2.js");
    await getNotice();

    let taskall = [];
    for (let user of $.userList) {
        if (user.ckStatus) {
            taskall.push(await user.task());
            await $.wait(1000);
        }
    }
    await Promise.all(taskall);
}

class UserInfo {
    constructor(str) {
        this.index = ++$.userIdx;
        this.ck = str.split(strSplitor)[0]; //单账号多变量分隔符
        this.ckStatus = true;
        this.mc_ckStatus = true
        this.headers = {
            "Host": "jdshop.yili.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Lite Build/QKQ1.190910.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/107.0.5304.141 Mobile Safari/537.36 XWEB/5127 MMWEBSDK/20230405 MMWEBID/2585 MicroMessenger/8.0.35.2360(0x2800235D) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
            "accesstoken": this.ck,
            "content-type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "scene": "1089",
            "Referer": "https://servicewechat.com/wxf32616183fb4511e/480/page-frame.html",
        }
        this.speedId = ""
        this.goldNum = 0 //金币
        this.waterContainerNum = 0 //水滴
        this.mcToken = ""
        this.openId = ""
        this.unionId = ""
    }
    get_mc_headers() {
        return {
            "Host": "wx-yljdmc-game.mscampapi.digitalyili.com",
            "authorization": this.mcToken,
            "user-agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Lite Build/QKQ1.190910.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/107.0.5304.141 Mobile Safari/537.36 XWEB/5127 MMWEBSDK/20230405 MMWEBID/2585 MicroMessenger/8.0.35.2360(0x2800235D) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 miniProgram/wxf32616183fb4511e",
            "content-type": "application/json",
            "accept": "*/*",
            "origin": "https://wx-pubcos.yili.com",
            "x-requested-with": "com.tencent.mm",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://wx-pubcos.yili.com/",
            "accept-encoding": "gzip, deflate",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }
    }
    /**
     * 时间戳 转换为 2023-07-07 21:17:53 yyyy-mm-dd xx:xx:xx 格式
     * @param {*} timestamp 
     * @returns  yyyy-mm-dd xx:xx:xx 格式
     */
    formatTimestamp(timestamp) {
        var date = new Date(timestamp);
        var year = date.getFullYear();
        var month = ("0" + (date.getMonth() + 1)).slice(-2);
        var day = ("0" + date.getDate()).slice(-2);
        var hours = ("0" + date.getHours()).slice(-2);
        var minutes = ("0" + date.getMinutes()).slice(-2);
        var seconds = ("0" + date.getSeconds()).slice(-2);
        return year + "-" + month + "-" + day + " " + hours + ":" + minutes + ":" + seconds;
    }
    /**
     * 判断这个花的状态
     * @param {Object} plantVo
     * @returns 
     */
    async checkPlantStatus(plantVo) {
        let plantJsonId = plantVo["plantJsonId"] //花ID 代码
        let plantLevel = plantVo["plantLevel"] //花等级
        let plantTime = plantVo["plantTime"] //种植时间
        let waterTime = plantVo["waterTime"] //上次浇水时间
        let userPlantId = plantVo["userPlantId"] //花的种植ID  浇水时需要
        //$.DoubleLog(`种植时间${this.formatTimestamp(plantTime / 1000)}`)
        //$.DoubleLog(`上次浇水时间${this.formatTimestamp(waterTime / 1000)}`)
        //$.DoubleLog(`当前土地种植的是${i["plantVo"]["plantJsonId"]}代号`)//700001 紫花苜蓿 价格 40 收获90金币 消耗10水滴

        let currentTime = new Date().getTime(); // 获取当前时间戳
        if (plantJsonId == 700001) { // 判断plantJsonId是否为700001
            if (plantLevel == 1 && Math.abs(currentTime - plantTime) / 1000 / 60 > 4) { // 如果plantLevel为1
                if (this.speedId !== "") {
                    //this.speedId固定参数 每个用户绑定
                    if (this.waterContainerNum > 10) {
                        await this.mc_water(userPlantId, this.speedId)
                    }
                }
            } else if (plantLevel == 2 && Math.abs(currentTime - waterTime) / 1000 / 60 > 4) { // 如果plantLevel为2
                //收获
                if (this.speedId !== "") {
                    //this.speedId固定参数 每个用户绑定
                    await this.mc_harvest(userPlantId, this.speedId)

                }
            } else {
            }
        } else if (plantJsonId == 700002) {
            if (plantLevel == 1 && Math.abs(currentTime - plantTime) / 1000 / 60 > 61) { // 如果plantLevel为1
                if (this.waterContainerNum > 10) {
                    await this.mc_water(userPlantId, this.speedId)
                }
            } else if (plantLevel == 2 && Math.abs(currentTime - waterTime) / 1000 / 60 > 61) { // 如果plantLevel为2
                //收获
                if (this.speedId !== "") {
                    //this.speedId固定参数 每个用户绑定
                    await this.mc_harvest(userPlantId, this.speedId)

                }
            } else {

            }
        } else {
            return false
        }
    }


    generateNoncestr(e) {
        void 0 === e && (e = 32);
        for (var t = "", n = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"], o = 0; o < e; o++) t += n[Math.round(Math.random() * (n.length - 1))];
        return t
    }
    async task() {
        $.DoubleLog(`-------- 开始 【第${this.index}个账号】--------`)
        //小程序外部 信息
        await this.user_info()
        if (this.ckStatus == true) {
            //外部签到状态
            await this.sign_status()//根据状态签到
        }
        //牧场登录
        await this.mc_login()


        if (this.mc_ckStatus == true) {
            //牧场信息baseInfo
            await this.mc_get_info()

            //获得牧场speedId
            await this.mc_get_speedId()
            //任务列表 游戏API
            await this.mc_task_list()
        }


    }


    //信息 GET 
    async user_info() {
        let options = {
            url: `https://jdshop.yili.com/api/user/getUserInfo`,
            headers: this.headers,
        },
            result = await httpRequest(options);
        //console.log(options);
        //console.log(result);
        if (result["code"] == 200) {

            $.DoubleLog(`账号${this.index}  [${result["data"][0]["userId"]}][${result["data"][0]["nickname"]}]`);
            this.openId = result["data"][0]["openId"]
            this.unionId = result["data"][0]["unionId"]
            this.nickName = result["data"][0]["nickname"]
            this.avatar = result["data"][0]["avatar"]
        } else {
            $.DoubleLog(`账号${this.index}  获取信息失败 ❌ `);
            this.ckStatus = false
            console.log(options);
            console.log(result);
        }
    }

    //签到状态 GET 
    async sign_status() {
        let options = {
            url: `https://jdshop.yili.com/api/user/sign/status`,
            headers: this.headers,
        },
            result = await httpRequest(options);
        //console.log(options);
        //console.log(result);
        if (result["code"] == 200) {
            $.DoubleLog(`账号${this.index}  当前签到状态${result["data"]["signed"]} 本月累计签到${result["data"]["monthSignDays"]}🎉`);
            if (result["data"]["signed"] == false) {
                await this.do_sign()
            }
        } else {
            $.DoubleLog(`账号${this.index}  查询签到状态失效 ❌ `);
            console.log(options);
            console.log(result);
        }
    }

    //签到 GET 
    async do_sign() {
        let options = {
            url: `https://jdshop.yili.com/api/user/daily/sign?exParams=true`,
            headers: this.headers,
        },
            result = await httpRequest(options);
        //console.log(options);
        //console.log(result);
        if (result["code"] == 200) {
            $.DoubleLog(`账号${this.index}  签到成功 🎉 获得${result["data"]["dailySign"]["bonusPoints"]} 成长值${result["data"]["dailySign"]["bonusGrowths"]}🎉`);
        } else {
            $.DoubleLog(`账号${this.index}  签到失败 ❌ `);
            console.log(options);
            console.log(result);
        }
    }

    async mc_login() {
        let timestamp = Date.now()
        let nonce = this.generateNoncestr(16)
        let signature = MD5_Encrypt(`clientKey=IfWu0xwXlWgqkICA6Wn20qpo6a30hXX5&clientSecret=A4rHhUJfMjw2I9IODh5g40Ja1d3Yk1CU&nonce=${nonce}&timestamp=${timestamp}`)
        let options = {

            //clientKey=IfWu0xwXlWgqkICA6Wn20qpo6a30hXX5&clientSecret=A4rHhUJfMjw2I9IODh5g40Ja1d3Yk1CU&nonce=X9kDWncTF6o1rCrw&timestamp=1688811817748

            url: `https://wx-yljdmc-game.mscampapi.digitalyili.com/ga/open/api/login?signature=${signature}&timestamp=${timestamp}&nonce=${nonce}`,
            headers: this.get_mc_headers(),
            //主要是thirdId
            body: JSON.stringify({ "unionId": this.unionId, "thirdId": this.openId, "userId": this.openId, "nickName": this.nickName, "avatarUrl": this.avatar })
        }, result = await httpRequest(options);
        if (result["code"] == 0) {
            this.mcToken = result["data"]
            $.DoubleLog(`牧场登录成功`)
        } else {
            $.DoubleLog(`账号${this.index}  牧场登录成功失败 ❌ `);
            this.mc_ckStatus = false
            console.log(options);
            console.log(result);
        }
    }
    //牧场 获取牧场信息
    async mc_get_info() {
        let options = {
            url: `https://wx-yljdmc-game.mscampapi.digitalyili.com/ga/user/getBaseInfo`,
            headers: this.get_mc_headers(),
        },
            result = await httpRequest(options);
        //console.log(options);
        //console.log(result);
        if (result["code"] == 0) {
            this.goldNum = result["data"]["goldNum"]
            this.waterContainerNum = result["data"]["waterContainerNum"]
            $.DoubleLog(`牧场ID - ${result["data"]["id"]} [${result["data"]["nickName"]}] 当前金币${result["data"]["goldNum"]} 当前水滴${result["data"]["waterContainerNum"]}`)
        } else {
            $.DoubleLog(`账号${this.index}  获取牧场信息失败 ❌ `);
            console.log(options);
            console.log(result);
        }
    }
    //牧场 签到 - 金典有机 云牧场
    async mc_task_list() {
        let options = {
            url: `https://wx-yljdmc-game.mscampapi.digitalyili.com/ga/task/api/listTask`,
            headers: this.get_mc_headers(),
        },
            result = await httpRequest(options);
        //console.log(options);
        //console.log(result);
        //userTaskId 是 doTask后会刷新这个  刷新完成后可以用这个领取奖励
        //taskState 2已完成未领取  3已领取  1未完成  0是隐藏任务

        if (result["code"] == 0) {
            $.DoubleLog(`账号${this.index}  获取任务信息成功 🎉 `);
            for (let i of result["data"]) {
                if (i["taskState"] !== 0) {//不是隐藏任务
                    if (i["jsonId"] == 400001) {
                        if (i["taskState"] == 2) {
                            await this.mc_doReward(i["userTaskId"])
                        }
                        //每日登录

                        //可以直接领取
                    } else if (i["jsonId"] == 400004) {
                        if (i["taskState"] == 1) {
                            await this.mc_land_info()
                        }
                        //土地信息
                        //完成五次种植
                        //默认种植700001
                        //先检测土地信息（花信息）
                        //
                    } else if (i["jsonId"] == 400005) {
                        //完成五次浇水
                    } else if (i["jsonId"] == 400006) {
                        //完成五次收获
                    } else if (i["jsonId"] == 400007) {
                        await this.mc_hookReport()
                        //收集三次挂机金币
                    }
                }

            }
        } else {
            $.DoubleLog(`账号${this.index}  获取任务信息失败 ❌ `);
            console.log(options);
            console.log(result);
        }
    }

    //牧场 土地信息
    async mc_land_info() {
        let options = {
            url: `https://wx-yljdmc-game.mscampapi.digitalyili.com/ga/plant/api/selectUserLand`,
            headers: this.get_mc_headers(),
        },
            result = await httpRequest(options);
        //console.log(options);
        //console.log(result);
        if (result["code"] == 0) {
            $.DoubleLog(`账号${this.index}  获取土地信息成功 🎉 `);
            for (let i of result["data"]) {
                //变量每块土地
                if (i["lockStatus"] == 1) {
                    $.DoubleLog(`当前土地-${i["landCode"]}未种植 => 尝试种植`)
                    //执行种植
                    //未种植
                    //判断金币
                    if (this.goldNum > 40) {
                        await this.mc_plant(i["jsonId"], 700001, this.speedId)
                    }
                } else if (i["lockStatus"] == 2) {
                    //判断浇水 判断是否收获 是否需要浇水
                    await this.checkPlantStatus(i["plantVo"])
                    //
                    //已种植
                } else if (i["lockStatus"] == 0) {
                    //未解锁
                    $.DoubleLog(`当前土地-${i["landCode"]}未解锁 => 尝试解锁`)
                    //尝试解锁
                }
            }
        } else {
            $.DoubleLog(`账号${this.index}  获取土地信息失败 ❌ `);
            console.log(options);
            console.log(result);
        }
    }

    //牧场 执行任务 
    async mc_doTask(taskId) {
        let options = {
            url: `https://wx-yljdmc-game.mscampapi.digitalyili.com/ga/task/api/doTask`,
            headers: this.get_mc_headers(),
            body: JSON.stringify({ "taskId": taskId })
        },
            result = await httpRequest(options);
        //console.log(options);
        //console.log(result);
        //完成后会刷新task_list 中 userTaskId

        if (result["code"] == 0) {
            if (result["data"] == true) {
                $.DoubleLog(`账号${this.index}  执行任务成功 🎉 `);
            }

        } else {
            $.DoubleLog(`账号${this.index}  获取任务信息失败 ❌ `);
            console.log(options);
            console.log(result);
        }
    }

    //牧场 领取奖励
    async mc_doReward(userTaskId) {
        let options = {
            url: `https://wx-yljdmc-game.mscampapi.digitalyili.com/ga/task/api/doReward`,
            headers: this.get_mc_headers(),
            body: JSON.stringify({ "userTaskId": userTaskId })
        },
            result = await httpRequest(options);
        //console.log(options);
        //console.log(result);
        if (result["code"] == 0) {
            $.DoubleLog(`账号${this.index}  领取奖励成功 🎉 `);
            for (let i of result["data"]) {
                i[""]
            }
        } else {
            $.DoubleLog(`账号${this.index}  领取奖励失败 ❌ `);
            console.log(options);
            console.log(result);
        }
    }


    //牧场 获取speedID //用于种植
    async mc_get_speedId() {
        let options = {
            url: `https://wx-yljdmc-game.mscampapi.digitalyili.com/ga/plant/api/getPlantSpeed`,
            headers: this.get_mc_headers(),
        },
            result = await httpRequest(options);
        //console.log(options);
        //console.log(result);


        if (result["code"] == 0) {
            this.speedId = result["data"]["id"]
        } else {
            $.DoubleLog(`账号${this.index}  获取SpeedId失败 ❌ `);
            console.log(options);
            console.log(result);
        }
    }

    //牧场 收集积攒的金币
    async mc_hookReport() {
        let options = {
            url: `https://wx-yljdmc-game.mscampapi.digitalyili.com/ga/plant/api/hookReport`,
            headers: this.get_mc_headers(),
            body: JSON.stringify({})
        },
            result = await httpRequest(options);
        //console.log(options);
        //console.log(result);
        if (result["code"] == 0) {
            $.DoubleLog(`账号${this.index}  查询积攒金币成功`)
            await this.mc_hookReward(result["data"]["userPlantId"], result["data"]["hookReward"])
        } else {
            $.DoubleLog(`账号${this.index}  查询积攒金币成功失败 ❌ `);
            console.log(options);
            console.log(result);
        }
    }
    //牧场 收集积攒的金币
    async mc_hookReward(hookReportId, num) {
        let options = {
            url: `https://wx-yljdmc-game.mscampapi.digitalyili.com/ga/plant/api/hookReward`,
            headers: this.get_mc_headers(),
            body: JSON.stringify({ "hookReportId": hookReportId, "num": num })
        },
            result = await httpRequest(options);
        //console.log(options);
        //console.log(result);
        if (result["code"] == 0) {
            $.DoubleLog(`账号${this.index}  领取积攒金币成功 领取${num}个`)
        } else {
            $.DoubleLog(`账号${this.index}  领取积攒金币成功失败 ❌ `);
            console.log(options);
            console.log(result);
        }
    }
    /**
     * 牧场 种植
     * @param {*} landJsonId 土地ID
     * @param {*} plantJsonId 花ID
     * @param {*} speedId speedId 用户绑定的加速ID
     */
    async mc_plant(landJsonId, plantJsonId = 700001, speedId) {
        let options = {
            url: `https://wx-yljdmc-game.mscampapi.digitalyili.com/ga/plant/api/plant`,
            headers: this.get_mc_headers(),
            body: JSON.stringify({ "landJsonId": landJsonId, "plantJsonId": plantJsonId, "speedId": speedId })
        },
            result = await httpRequest(options);
        //console.log(options);
        //console.log(result);


        if (result["code"] == 0) {
            if (result["data"] == true) {
                console.log(`种植成功`); // id  userPlantId
            }
        } else {
            $.DoubleLog(`账号${this.index}  种植失败 ❌ `);
            console.log(options);
            console.log(result);
        }

    }

    //牧场 浇水
    async mc_water(userPlantId, speedId) {
        let options = {
            url: `https://wx-yljdmc-game.mscampapi.digitalyili.com/ga/plant/api/water`,
            headers: this.get_mc_headers(),
            body: JSON.stringify({ "userPlantId": userPlantId, "speedId": speedId })
        },
            result = await httpRequest(options);
        //console.log(options);
        //console.log(result);


        if (result["code"] == 0) {
            if (result["data"]["isSuccess"] == true) {
                //浇水成功
            }
        } else {
            $.DoubleLog(`账号${this.index}  浇水失败 ❌ `);
            console.log(options);
            console.log(result);
        }
    }

    //牧场 收获
    async mc_harvest(userPlantId, speedId) {
        let options = {
            url: `https://wx-yljdmc-game.mscampapi.digitalyili.com/ga/plant/api/harvest`,
            headers: this.get_mc_headers(),
            body: JSON.stringify({ "userPlantId": userPlantId, "speedId": speedId })
        },
            result = await httpRequest(options);
        //console.log(options);
        //console.log(result);



        if (result["code"] == 0) {

        } else {
            $.DoubleLog(`账号${this.index}   ❌ `);
            console.log(options);
            console.log(result);
        }
    }

}

!(async () => {
    if (!(await checkEnv())) return;
    if ($.userList.length > 0) {
        await start();
    } await $.SendMsg(msg);
})().catch((e) => console.log(e)).finally(() => $.done());

//********************************************************
/**
 * 变量检查与处理
 * @returns
 */
async function checkEnv() {
    let userCookie = ($.isNode() ? process.env[ckName] : $.getdata(ckName)) || "";
    //let userCount = 0;
    if (userCookie) {
        // console.log(userCookie);
        let e = envSplitor[0];
        for (let o of envSplitor)
            if (userCookie.indexOf(o) > -1) {
                e = o;
                break;
            }
        for (let n of userCookie.split(e)) n && $.userList.push(new UserInfo(n));
        //userCount = $.userList.length;
    } else {
        console.log("未找到CK");
        return;
    }
    return console.log(`共找到${$.userList.length}个账号`), true; //true == !0
}

/////////////////////////////////////////////////////////////////////////////////////
function httpRequest(options, method = null) {
    method = options.method ? options.method.toLowerCase() : options.body ? "post" : "get";
    return new Promise((resolve) => {
        $[method](options, (err, resp, data) => {
            if (err) {
                console.log(`${method}请求失败`);
                $.logErr(err);
            } else {
                if (data) {
                    try { data = JSON.parse(data); } catch (error) { }
                    resolve(data);
                } else {
                    console.log(`请求api返回数据为空，请检查自身原因`);
                }
            }
            resolve();
        });
    });
}
/**
 * 获取远程版本
 */
function getVersion(scriptUrl, timeout = 3 * 1000) {
    return new Promise((resolve) => {
        //"smallfawn/QLScriptPublic/main/suboer.js"
        const options = { url: `https://fastly.jsdelivr.net/gh/${scriptUrl}` };
        $.get(options, (err, resp, data) => {
            try {
                const regex = /scriptVersionNow\s*=\s*(["'`])([\d.]+)\1/;
                const match = data.match(regex);
                const scriptVersionLatest = match ? match[2] : "";
                console.log(`\n====== 当前版本：${scriptVersionNow} 📌 最新版本：${scriptVersionLatest} ======`);
            } catch (e) {
                $.logErr(e, resp);
            }
            resolve();
        }, timeout);
    });
}
/**
 * 获取远程通知
 */
async function getNotice() {
    try {
        const urls = [
            "https://fastly.jsdelivr.net/gh/smallfawn/Note@main/Notice.json",
            "https://gcore.jsdelivr.net/gh/smallfawn/Note@main/Notice.json",
            "https://cdn.jsdelivr.net/gh/smallfawn/Note@main/Notice.json",
            "https://ghproxy.com/https://raw.githubusercontent.com/smallfawn/Note/main/Notice.json",
            "https://gitee.com/smallfawn/Note/raw/master/Notice.json",
        ];
        let notice = null;
        for (const url of urls) {
            const options = { url, headers: { "User-Agent": "" }, };
            const result = await httpRequest(options);
            if (result && "notice" in result) {
                notice = result.notice.replace(/\\n/g, "\n");
                break;
            }
        }
        if (notice) { $.DoubleLog(notice); }
    } catch (e) {
        console.log(e);
    }
}
/**
 * md5 加密
 */
function MD5_Encrypt(a) { function b(a, b) { return (a << b) | (a >>> (32 - b)); } function c(a, b) { var c, d, e, f, g; return ((e = 2147483648 & a), (f = 2147483648 & b), (c = 1073741824 & a), (d = 1073741824 & b), (g = (1073741823 & a) + (1073741823 & b)), c & d ? 2147483648 ^ g ^ e ^ f : c | d ? 1073741824 & g ? 3221225472 ^ g ^ e ^ f : 1073741824 ^ g ^ e ^ f : g ^ e ^ f); } function d(a, b, c) { return (a & b) | (~a & c); } function e(a, b, c) { return (a & c) | (b & ~c); } function f(a, b, c) { return a ^ b ^ c; } function g(a, b, c) { return b ^ (a | ~c); } function h(a, e, f, g, h, i, j) { return (a = c(a, c(c(d(e, f, g), h), j))), c(b(a, i), e); } function i(a, d, f, g, h, i, j) { return (a = c(a, c(c(e(d, f, g), h), j))), c(b(a, i), d); } function j(a, d, e, g, h, i, j) { return (a = c(a, c(c(f(d, e, g), h), j))), c(b(a, i), d); } function k(a, d, e, f, h, i, j) { return (a = c(a, c(c(g(d, e, f), h), j))), c(b(a, i), d); } function l(a) { for (var b, c = a.length, d = c + 8, e = (d - (d % 64)) / 64, f = 16 * (e + 1), g = new Array(f - 1), h = 0, i = 0; c > i;) (b = (i - (i % 4)) / 4), (h = (i % 4) * 8), (g[b] = g[b] | (a.charCodeAt(i) << h)), i++; return ((b = (i - (i % 4)) / 4), (h = (i % 4) * 8), (g[b] = g[b] | (128 << h)), (g[f - 2] = c << 3), (g[f - 1] = c >>> 29), g); } function m(a) { var b, c, d = "", e = ""; for (c = 0; 3 >= c; c++) (b = (a >>> (8 * c)) & 255), (e = "0" + b.toString(16)), (d += e.substr(e.length - 2, 2)); return d; } function n(a) { a = a.replace(/\r\n/g, "\n"); for (var b = "", c = 0; c < a.length; c++) { var d = a.charCodeAt(c); 128 > d ? (b += String.fromCharCode(d)) : d > 127 && 2048 > d ? ((b += String.fromCharCode((d >> 6) | 192)), (b += String.fromCharCode((63 & d) | 128))) : ((b += String.fromCharCode((d >> 12) | 224)), (b += String.fromCharCode(((d >> 6) & 63) | 128)), (b += String.fromCharCode((63 & d) | 128))); } return b; } var o, p, q, r, s, t, u, v, w, x = [], y = 7, z = 12, A = 17, B = 22, C = 5, D = 9, E = 14, F = 20, G = 4, H = 11, I = 16, J = 23, K = 6, L = 10, M = 15, N = 21; for (a = n(a), x = l(a), t = 1732584193, u = 4023233417, v = 2562383102, w = 271733878, o = 0; o < x.length; o += 16) (p = t), (q = u), (r = v), (s = w), (t = h(t, u, v, w, x[o + 0], y, 3614090360)), (w = h(w, t, u, v, x[o + 1], z, 3905402710)), (v = h(v, w, t, u, x[o + 2], A, 606105819)), (u = h(u, v, w, t, x[o + 3], B, 3250441966)), (t = h(t, u, v, w, x[o + 4], y, 4118548399)), (w = h(w, t, u, v, x[o + 5], z, 1200080426)), (v = h(v, w, t, u, x[o + 6], A, 2821735955)), (u = h(u, v, w, t, x[o + 7], B, 4249261313)), (t = h(t, u, v, w, x[o + 8], y, 1770035416)), (w = h(w, t, u, v, x[o + 9], z, 2336552879)), (v = h(v, w, t, u, x[o + 10], A, 4294925233)), (u = h(u, v, w, t, x[o + 11], B, 2304563134)), (t = h(t, u, v, w, x[o + 12], y, 1804603682)), (w = h(w, t, u, v, x[o + 13], z, 4254626195)), (v = h(v, w, t, u, x[o + 14], A, 2792965006)), (u = h(u, v, w, t, x[o + 15], B, 1236535329)), (t = i(t, u, v, w, x[o + 1], C, 4129170786)), (w = i(w, t, u, v, x[o + 6], D, 3225465664)), (v = i(v, w, t, u, x[o + 11], E, 643717713)), (u = i(u, v, w, t, x[o + 0], F, 3921069994)), (t = i(t, u, v, w, x[o + 5], C, 3593408605)), (w = i(w, t, u, v, x[o + 10], D, 38016083)), (v = i(v, w, t, u, x[o + 15], E, 3634488961)), (u = i(u, v, w, t, x[o + 4], F, 3889429448)), (t = i(t, u, v, w, x[o + 9], C, 568446438)), (w = i(w, t, u, v, x[o + 14], D, 3275163606)), (v = i(v, w, t, u, x[o + 3], E, 4107603335)), (u = i(u, v, w, t, x[o + 8], F, 1163531501)), (t = i(t, u, v, w, x[o + 13], C, 2850285829)), (w = i(w, t, u, v, x[o + 2], D, 4243563512)), (v = i(v, w, t, u, x[o + 7], E, 1735328473)), (u = i(u, v, w, t, x[o + 12], F, 2368359562)), (t = j(t, u, v, w, x[o + 5], G, 4294588738)), (w = j(w, t, u, v, x[o + 8], H, 2272392833)), (v = j(v, w, t, u, x[o + 11], I, 1839030562)), (u = j(u, v, w, t, x[o + 14], J, 4259657740)), (t = j(t, u, v, w, x[o + 1], G, 2763975236)), (w = j(w, t, u, v, x[o + 4], H, 1272893353)), (v = j(v, w, t, u, x[o + 7], I, 4139469664)), (u = j(u, v, w, t, x[o + 10], J, 3200236656)), (t = j(t, u, v, w, x[o + 13], G, 681279174)), (w = j(w, t, u, v, x[o + 0], H, 3936430074)), (v = j(v, w, t, u, x[o + 3], I, 3572445317)), (u = j(u, v, w, t, x[o + 6], J, 76029189)), (t = j(t, u, v, w, x[o + 9], G, 3654602809)), (w = j(w, t, u, v, x[o + 12], H, 3873151461)), (v = j(v, w, t, u, x[o + 15], I, 530742520)), (u = j(u, v, w, t, x[o + 2], J, 3299628645)), (t = k(t, u, v, w, x[o + 0], K, 4096336452)), (w = k(w, t, u, v, x[o + 7], L, 1126891415)), (v = k(v, w, t, u, x[o + 14], M, 2878612391)), (u = k(u, v, w, t, x[o + 5], N, 4237533241)), (t = k(t, u, v, w, x[o + 12], K, 1700485571)), (w = k(w, t, u, v, x[o + 3], L, 2399980690)), (v = k(v, w, t, u, x[o + 10], M, 4293915773)), (u = k(u, v, w, t, x[o + 1], N, 2240044497)), (t = k(t, u, v, w, x[o + 8], K, 1873313359)), (w = k(w, t, u, v, x[o + 15], L, 4264355552)), (v = k(v, w, t, u, x[o + 6], M, 2734768916)), (u = k(u, v, w, t, x[o + 13], N, 1309151649)), (t = k(t, u, v, w, x[o + 4], K, 4149444226)), (w = k(w, t, u, v, x[o + 11], L, 3174756917)), (v = k(v, w, t, u, x[o + 2], M, 718787259)), (u = k(u, v, w, t, x[o + 9], N, 3951481745)), (t = c(t, p)), (u = c(u, q)), (v = c(v, r)), (w = c(w, s)); var O = m(t) + m(u) + m(v) + m(w); return O.toLowerCase(); }
// ==================== API ==================== //
function Env(t, e) { class s { constructor(t) { this.env = t } send(t, e = "GET") { t = "string" == typeof t ? { url: t } : t; let s = this.get; return ("POST" === e && (s = this.post), new Promise((e, a) => { s.call(this, t, (t, s, r) => { t ? a(t) : e(s) }) })) } get(t) { return this.send.call(this.env, t) } post(t) { return this.send.call(this.env, t, "POST") } } return new (class { constructor(t, e) { this.userList = []; this.userIdx = 0; (this.name = t), (this.http = new s(this)), (this.data = null), (this.dataFile = "box.dat"), (this.logs = []), (this.isMute = !1), (this.isNeedRewrite = !1), (this.logSeparator = "\n"), (this.encoding = "utf-8"), (this.startTime = new Date().getTime()), Object.assign(this, e), this.log("", `🔔${this.name},开始!`) } getEnv() { return "undefined" != typeof $environment && $environment["surge-version"] ? "Surge" : "undefined" != typeof $environment && $environment["stash-version"] ? "Stash" : "undefined" != typeof module && module.exports ? "Node.js" : "undefined" != typeof $task ? "Quantumult X" : "undefined" != typeof $loon ? "Loon" : "undefined" != typeof $rocket ? "Shadowrocket" : void 0 } isNode() { return "Node.js" === this.getEnv() } isQuanX() { return "Quantumult X" === this.getEnv() } isSurge() { return "Surge" === this.getEnv() } isLoon() { return "Loon" === this.getEnv() } isShadowrocket() { return "Shadowrocket" === this.getEnv() } isStash() { return "Stash" === this.getEnv() } toObj(t, e = null) { try { return JSON.parse(t) } catch { return e } } toStr(t, e = null) { try { return JSON.stringify(t) } catch { return e } } getjson(t, e) { let s = e; const a = this.getdata(t); if (a) try { s = JSON.parse(this.getdata(t)) } catch { } return s } setjson(t, e) { try { return this.setdata(JSON.stringify(t), e) } catch { return !1 } } getScript(t) { return new Promise((e) => { this.get({ url: t }, (t, s, a) => e(a)) }) } runScript(t, e) { return new Promise((s) => { let a = this.getdata("@chavy_boxjs_userCfgs.httpapi"); a = a ? a.replace(/\n/g, "").trim() : a; let r = this.getdata("@chavy_boxjs_userCfgs.httpapi_timeout"); (r = r ? 1 * r : 20), (r = e && e.timeout ? e.timeout : r); const [i, o] = a.split("@"), n = { url: `http://${o}/v1/scripting/evaluate`, body: { script_text: t, mock_type: "cron", timeout: r }, headers: { "X-Key": i, Accept: "*/*" }, timeout: r, }; this.post(n, (t, e, a) => s(a)) }).catch((t) => this.logErr(t)) } loaddata() { if (!this.isNode()) return {}; { (this.fs = this.fs ? this.fs : require("fs")), (this.path = this.path ? this.path : require("path")); const t = this.path.resolve(this.dataFile), e = this.path.resolve(process.cwd(), this.dataFile), s = this.fs.existsSync(t), a = !s && this.fs.existsSync(e); if (!s && !a) return {}; { const a = s ? t : e; try { return JSON.parse(this.fs.readFileSync(a)) } catch (t) { return {} } } } } writedata() { if (this.isNode()) { (this.fs = this.fs ? this.fs : require("fs")), (this.path = this.path ? this.path : require("path")); const t = this.path.resolve(this.dataFile), e = this.path.resolve(process.cwd(), this.dataFile), s = this.fs.existsSync(t), a = !s && this.fs.existsSync(e), r = JSON.stringify(this.data); s ? this.fs.writeFileSync(t, r) : a ? this.fs.writeFileSync(e, r) : this.fs.writeFileSync(t, r) } } lodash_get(t, e, s) { const a = e.replace(/\[(\d+)\]/g, ".$1").split("."); let r = t; for (const t of a) if (((r = Object(r)[t]), void 0 === r)) return s; return r } lodash_set(t, e, s) { return Object(t) !== t ? t : (Array.isArray(e) || (e = e.toString().match(/[^.[\]]+/g) || []), (e.slice(0, -1).reduce((t, s, a) => Object(t[s]) === t[s] ? t[s] : (t[s] = Math.abs(e[a + 1]) >> 0 == +e[a + 1] ? [] : {}), t)[e[e.length - 1]] = s), t) } getdata(t) { let e = this.getval(t); if (/^@/.test(t)) { const [, s, a] = /^@(.*?)\.(.*?)$/.exec(t), r = s ? this.getval(s) : ""; if (r) try { const t = JSON.parse(r); e = t ? this.lodash_get(t, a, "") : e } catch (t) { e = "" } } return e } setdata(t, e) { let s = !1; if (/^@/.test(e)) { const [, a, r] = /^@(.*?)\.(.*?)$/.exec(e), i = this.getval(a), o = a ? ("null" === i ? null : i || "{}") : "{}"; try { const e = JSON.parse(o); this.lodash_set(e, r, t), (s = this.setval(JSON.stringify(e), a)) } catch (e) { const i = {}; this.lodash_set(i, r, t), (s = this.setval(JSON.stringify(i), a)) } } else s = this.setval(t, e); return s } getval(t) { switch (this.getEnv()) { case "Surge": case "Loon": case "Stash": case "Shadowrocket": return $persistentStore.read(t); case "Quantumult X": return $prefs.valueForKey(t); case "Node.js": return (this.data = this.loaddata()), this.data[t]; default: return (this.data && this.data[t]) || null } } setval(t, e) { switch (this.getEnv()) { case "Surge": case "Loon": case "Stash": case "Shadowrocket": return $persistentStore.write(t, e); case "Quantumult X": return $prefs.setValueForKey(t, e); case "Node.js": return ((this.data = this.loaddata()), (this.data[e] = t), this.writedata(), !0); default: return (this.data && this.data[e]) || null } } initGotEnv(t) { (this.got = this.got ? this.got : require("got")), (this.cktough = this.cktough ? this.cktough : require("tough-cookie")), (this.ckjar = this.ckjar ? this.ckjar : new this.cktough.CookieJar()), t && ((t.headers = t.headers ? t.headers : {}), void 0 === t.headers.Cookie && void 0 === t.cookieJar && (t.cookieJar = this.ckjar)) } get(t, e = () => { }) { switch ((t.headers && (delete t.headers["Content-Type"], delete t.headers["Content-Length"], delete t.headers["content-type"], delete t.headers["content-length"]), this.getEnv())) { case "Surge": case "Loon": case "Stash": case "Shadowrocket": default: this.isSurge() && this.isNeedRewrite && ((t.headers = t.headers || {}), Object.assign(t.headers, { "X-Surge-Skip-Scripting": !1 })), $httpClient.get(t, (t, s, a) => { !t && s && ((s.body = a), (s.statusCode = s.status ? s.status : s.statusCode), (s.status = s.statusCode)), e(t, s, a) }); break; case "Quantumult X": this.isNeedRewrite && ((t.opts = t.opts || {}), Object.assign(t.opts, { hints: !1 })), $task.fetch(t).then((t) => { const { statusCode: s, statusCode: a, headers: r, body: i, bodyBytes: o, } = t; e(null, { status: s, statusCode: a, headers: r, body: i, bodyBytes: o, }, i, o) }, (t) => e((t && t.error) || "UndefinedError")); break; case "Node.js": let s = require("iconv-lite"); this.initGotEnv(t), this.got(t).on("redirect", (t, e) => { try { if (t.headers["set-cookie"]) { const s = t.headers["set-cookie"].map(this.cktough.Cookie.parse).toString(); s && this.ckjar.setCookieSync(s, null), (e.cookieJar = this.ckjar) } } catch (t) { this.logErr(t) } }).then((t) => { const { statusCode: a, statusCode: r, headers: i, rawBody: o, } = t, n = s.decode(o, this.encoding); e(null, { status: a, statusCode: r, headers: i, rawBody: o, body: n, }, n) }, (t) => { const { message: a, response: r } = t; e(a, r, r && s.decode(r.rawBody, this.encoding)) }) } } post(t, e = () => { }) { const s = t.method ? t.method.toLocaleLowerCase() : "post"; switch ((t.body && t.headers && !t.headers["Content-Type"] && !t.headers["content-type"] && (t.headers["content-type"] = "application/x-www-form-urlencoded"), t.headers && (delete t.headers["Content-Length"], delete t.headers["content-length"]), this.getEnv())) { case "Surge": case "Loon": case "Stash": case "Shadowrocket": default: this.isSurge() && this.isNeedRewrite && ((t.headers = t.headers || {}), Object.assign(t.headers, { "X-Surge-Skip-Scripting": !1 })), $httpClient[s](t, (t, s, a) => { !t && s && ((s.body = a), (s.statusCode = s.status ? s.status : s.statusCode), (s.status = s.statusCode)), e(t, s, a) }); break; case "Quantumult X": (t.method = s), this.isNeedRewrite && ((t.opts = t.opts || {}), Object.assign(t.opts, { hints: !1 })), $task.fetch(t).then((t) => { const { statusCode: s, statusCode: a, headers: r, body: i, bodyBytes: o, } = t; e(null, { status: s, statusCode: a, headers: r, body: i, bodyBytes: o, }, i, o) }, (t) => e((t && t.error) || "UndefinedError")); break; case "Node.js": let a = require("iconv-lite"); this.initGotEnv(t); const { url: r, ...i } = t; this.got[s](r, i).then((t) => { const { statusCode: s, statusCode: r, headers: i, rawBody: o, } = t, n = a.decode(o, this.encoding); e(null, { status: s, statusCode: r, headers: i, rawBody: o, body: n }, n) }, (t) => { const { message: s, response: r } = t; e(s, r, r && a.decode(r.rawBody, this.encoding)) }) } } time(t, e = null) { const s = e ? new Date(e) : new Date(); let a = { "M+": s.getMonth() + 1, "d+": s.getDate(), "H+": s.getHours(), "m+": s.getMinutes(), "s+": s.getSeconds(), "q+": Math.floor((s.getMonth() + 3) / 3), S: s.getMilliseconds(), }; /(y+)/.test(t) && (t = t.replace(RegExp.$1, (s.getFullYear() + "").substr(4 - RegExp.$1.length))); for (let e in a) new RegExp("(" + e + ")").test(t) && (t = t.replace(RegExp.$1, 1 == RegExp.$1.length ? a[e] : ("00" + a[e]).substr(("" + a[e]).length))); return t } queryStr(t) { let e = ""; for (const s in t) { let a = t[s]; null != a && "" !== a && ("object" == typeof a && (a = JSON.stringify(a)), (e += `${s}=${a}&`)) } return (e = e.substring(0, e.length - 1)), e } msg(e = t, s = "", a = "", r) { const i = (t) => { switch (typeof t) { case void 0: return t; case "string": switch (this.getEnv()) { case "Surge": case "Stash": default: return { url: t }; case "Loon": case "Shadowrocket": return t; case "Quantumult X": return { "open-url": t }; case "Node.js": return }case "object": switch (this.getEnv()) { case "Surge": case "Stash": case "Shadowrocket": default: { let e = t.url || t.openUrl || t["open-url"]; return { url: e } } case "Loon": { let e = t.openUrl || t.url || t["open-url"], s = t.mediaUrl || t["media-url"]; return { openUrl: e, mediaUrl: s } } case "Quantumult X": { let e = t["open-url"] || t.url || t.openUrl, s = t["media-url"] || t.mediaUrl, a = t["update-pasteboard"] || t.updatePasteboard; return { "open-url": e, "media-url": s, "update-pasteboard": a, } } case "Node.js": return }default: return } }; if (!this.isMute) switch (this.getEnv()) { case "Surge": case "Loon": case "Stash": case "Shadowrocket": default: $notification.post(e, s, a, i(r)); break; case "Quantumult X": $notify(e, s, a, i(r)); break; case "Node.js": }if (!this.isMuteLog) { let t = ["", "==============📣系统通知📣==============",]; t.push(e), s && t.push(s), a && t.push(a), console.log(t.join("\n")), (this.logs = this.logs.concat(t)) } } log(...t) { t.length > 0 && (this.logs = [...this.logs, ...t]), console.log(t.join(this.logSeparator)) } logErr(t, e) { switch (this.getEnv()) { case "Surge": case "Loon": case "Stash": case "Shadowrocket": case "Quantumult X": default: this.log("", `❗️${this.name},错误!`, t); break; case "Node.js": this.log("", `❗️${this.name},错误!`, t.stack) } } wait(t) { return new Promise((e) => setTimeout(e, t)) } DoubleLog(d) { if (this.isNode()) { if (d) { console.log(`${d}`); msg += `\n ${d}` } } else { console.log(`${d}`); msg += `\n ${d}` } } async SendMsg(m) { if (!m) return; if (Notify > 0) { if (this.isNode()) { var notify = require("./sendNotify"); await notify.sendNotify(this.name, m) } else { this.msg(this.name, "", m) } } else { console.log(m) } } done(t = {}) { const e = new Date().getTime(), s = (e - this.startTime) / 1e3; switch ((this.log("", `🔔${this.name},结束!🕛${s}秒`), this.log(), this.getEnv())) { case "Surge": case "Loon": case "Stash": case "Shadowrocket": case "Quantumult X": default: $done(t); break; case "Node.js": process.exit(1) } } })(t, e) }
//Env rewrite:smallfawn Update-time:23-6-30 newAdd:DoubleLog & SendMsg
