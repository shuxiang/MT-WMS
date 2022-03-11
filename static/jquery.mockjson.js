(function($) {

var _mocked = [];
$.mockJSON = function(request, template) {
    for (var i = 0; i < _mocked.length; i++) {
        var mock = _mocked[i];
        if (mock.request.toString() == request.toString()) {
            _mocked.splice(i, 1);
            break;
        }
    }

    _mocked.push({
        request:request,
        template:template
    });
    
    return $;
};

$.mockJSON.random = true;


var _original_ajax = $.ajax;
$.ajax = function(options) {
    if (options.dataType === 'json') {
        for (var i = 0; i < _mocked.length; i++) {
            var mock = _mocked[i];
            if (mock.request.test(options.url)) {
                options.success($.mockJSON.generateFromTemplate(mock.template));
                return $;
            }
        }
    }
    
    return _original_ajax.apply(this, arguments);
}


$.mockJSON.generateFromTemplate = function(template, name) {
    var length = 0;
    var matches = (name || '').match(/\w+\|(\d+)-(\d+)/);
    if (matches) {
        var length_min = parseInt(matches[1], 10);
        var length_max = parseInt(matches[2], 10);
        length = Math.round(rand() * (length_max - length_min)) + length_min;
    }
        
    var generated = null;
    switch (type(template)) {
        case 'array':
            generated = [];
            for (var i = 0; i < length; i++) {
                generated[i] = $.mockJSON.generateFromTemplate(template[0]);
            }
            break;

        case 'object':
            generated = {};
            for (var p in template) {
                generated[p.replace(/\|(\d+-\d+|\+\d+)/, '')] = $.mockJSON.generateFromTemplate(template[p], p);
                var inc_matches = p.match(/\w+\|\+(\d+)/);
                if (inc_matches && type(template[p]) == 'number') {
                    var increment = parseInt(inc_matches[1], 10);
                    template[p] += increment;
                }
            }
            break;

        case 'number':
            generated = (matches)
                ? length
                : template;
            break;

        case 'boolean':
            generated = (matches)
                ? rand() >= 0.5
                : template;
            break;

        case 'string':
            if (template.length) {
                generated = '';
                length = length || 1;
                for (var i = 0; i < length; i++) {
                    generated += template;
                }
                var keys = generated.match(/@([A-Z_0-9\(\),]+)/g) || [];
                for (var i = 0; i < keys.length; i++) {
                    var key = keys[i];
                    var randomData = getRandomData(key);
                    generated = generated.replace(key, randomData);
                    if (type(randomData) == 'number')
                        generated = Number(generated);
                }
            } else {
                generated = ""
                for (var i = 0; i < length; i++) {
                    generated += String.fromCharCode(Math.floor(rand() * 255));
                }
            }
            break

        default:
            generated = template;
            break;
    }
    return generated;

}


function getRandomData(key) {
    key = key.substr(1); // remove "@"
    
    //var params = key.match(/\(((\d+),?)+\)/g) || [];
    var params = key.match(/\(([^\)]+)\)/g) || [];
    
    if (!(key in $.mockJSON.data)) {
        console.log(key);
        console.log(params);
        return key;
    }
    
    var a = $.mockJSON.data[key];
    
    switch (type(a)) {
        case 'array':
            var index = Math.floor(a.length * rand());
            return a[index];
            
        case 'function':
            return a();
    }
}


function type(obj) {
    return $.isArray(obj)
        ? 'array' 
        : (obj === null)
            ? 'null'
            : typeof obj;
}


function pad(num) {
    if (num < 10) {
        return '0' + num;
    }
    return num + '';
}

var _random_numbers = [0.021768910889510606,0.23762323165420307,0.9079616118204306,0.6534305309997466,0.22049697572443694,0.07687466163364898,0.8017428775547905,0.16165353264404825,0.5124345671670483,0.19337327636624613,0.39963994200698416,0.8012592654139514,0.22474962687229938,0.9791396234452399,0.7965428353317756,0.9777664340629622,0.5135216702983731,0.7407128236192145,0.12880984991420075,0.8186600800491484,0.5187691445438851,0.034723021925916586,0.5625092833040853,0.02502838571997701,0.663696305503698,0.3481608684353138,0.8991623585175106,0.3640542564277087,0.8320766874121723,0.012778915627689846,0.1427680370061336,0.9774408289203956,0.010229381207667587,0.2596610885223093,0.6150540104297127,0.7130773919030915,0.8638338302974085,0.6178483032907357,0.980312844391733,0.5007277415012348,0.6348672031113127,0.4400097775503303,0.8468458451408212,0.38724997893647317,0.690237920987028,0.19850102297146477,0.44895115941315766,0.22283381913760725,0.031228117310125314,0.3367510872581615,0.28155752394210787,0.14696694832580504,0.08164635161760991,0.8837733477785624,0.4590179148539142,0.9613195413217465,0.11263127577456922,0.743695635896287,0.0002424891439143373,0.1964622832546613,0.7333363138878922,0.5575568682003356,0.20426374168098604,0.18030934250338893,0.9792636408392759,0.30121911048336913,0.7734906886720265,0.6984051127767527,0.6638058511379343,0.3310956256388182,0.36632372827973203,0.8996494702333895,0.8235917663049763,0.418496734118911,0.8164648495097332,0.9457831606354686,0.2845227542117049,0.42374718399151545,0.3431728911657228,0.5289314006219973,0.6029243600407113,0.6528301140700757,0.6948768236197832,0.7887302784092911,0.8950274196119906,0.6121642239166305,0.31797481561514696,0.34903732589844216,0.3580320092281766,0.8312225728434115,0.32331010157206974,0.16395388672837796,0.6072960306003872,0.6580526967999424,0.23472961545632742,0.6138637855489343,0.3067303339060682,0.44935935129958315,0.24729465243280668,0.8244189715967711];
function rand() {
    if ($.mockJSON.random) {
        return Math.random();
    } else {
        _random_numbers = _random_numbers.concat(_random_numbers.splice(0,1));
        return _random_numbers[0];
    }
}


function randomDate() {
    return new Date(Math.floor(rand() * new Date().valueOf()));
}


$.mockJSON.data = {
    NUMBER : "0123456789".split(''),
    LETTER_UPPER : "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split(''),
    LETTER_LOWER : "abcdefghijklmnopqrstuvwxyz".split(''),
    MALE_FIRST_NAME : ["James", "John", "Robert", "Michael", "William", "David",
        "Richard", "Charles", "Joseph", "Thomas", "Christopher", "Daniel", 
        "Paul", "Mark", "Donald", "George", "Kenneth", "Steven", "Edward",
        "Brian", "Ronald", "Anthony", "Kevin", "Jason", "Matthew", "Gary",
        "Timothy", "Jose", "Larry", "Jeffrey", "Frank", "Scott", "Eric"],
    FEMALE_FIRST_NAME : ["Mary", "Patricia", "Linda", "Barbara", "Elizabeth", 
        "Jennifer", "Maria", "Susan", "Margaret", "Dorothy", "Lisa", "Nancy", 
        "Karen", "Betty", "Helen", "Sandra", "Donna", "Carol", "Ruth", "Sharon",
        "Michelle", "Laura", "Sarah", "Kimberly", "Deborah", "Jessica", 
        "Shirley", "Cynthia", "Angela", "Melissa", "Brenda", "Amy", "Anna"], 
    LAST_NAME : ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller",
        "Davis", "Garcia", "Rodriguez", "Wilson", "Martinez", "Anderson",
        "Taylor", "Thomas", "Hernandez", "Moore", "Martin", "Jackson",
        "Thompson", "White", "Lopez", "Lee", "Gonzalez", "Harris", "Clark",
        "Lewis", "Robinson", "Walker", "Perez", "Hall", "Young", "Allen"],
    TITLE: ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller",
        "Davis", "Garcia", "Rodriguez", "Wilson", "Martinez", "Anderson",
        "Taylor", "Thomas", "Hernandez", "Moore", "Martin", "Jackson",
        "Thompson", "White", "Lopez", "Lee", "Gonzalez", "Harris", "Clark",
        "Lewis", "Robinson", "Walker", "Perez", "Hall", "Young", "Allen"],
    CTITLE: ["春","集","丈","木","研","班","普","导","顿","睡","展","跳","获","艺","六","波","察","群","皇","段","急","庭","创","区","奥","器","谢","弟","店","否","害","草","排","背","止","组","州","朝","封","睛","板","角","况","曲","馆","育","忙","质","河","续","哥","呼","若","推","境","遇","雨","标","姐","充","围","案","伦","护","冷","警","贝","著","雪","索","剧","啊","船","险","烟","依","斗","值","帮","汉","慢","佛","肯","闻","唱","沙","局","伯","族","低","玩","资","屋","击","速","顾","泪","洲","团","圣","旁","堂","兵","七","露","园","牛","哭","旅","街","劳","型","烈","姑","陈","莫","鱼","异","抱","宝","权","鲁","简","态","级","票","怪","寻","杀","律","胜","份","汽","右","洋","范","床","舞","秘","午","登","楼","贵","吸","责","例","追","较","职","属","渐","左","录","丝","牙","党","继","托","赶","章","智","冲","叶","胡","吉","卖","坚","喝","肉","遗","救","修","松","临","藏","担","戏","善","卫","药","悲","敢","靠","伊","村","戴","词","森","耳","差","短","祖","云","规","窗","散","迷","油","旧","适","乡","架","恩","投","弹","铁","博","雷","府","压","超","负","勒","杂","醒","洗","采","毫","嘴","毕","九","冰","既","状","乱","景","席","珍","童","顶","派","素","脱","农","疑","练","野","按","犯","拍","征","坏","骨","余","承","置", "彩","灯","巨","琴","免","环","姆","暗","换","技","翻","束","增","忍","餐","洛","塞","缺","忆","判","欧","层","付","阵","玛","批","岛","项","狗","休","懂","武","革","良","恶","恋","委","拥","娜","妙","探","呀","营","退","摇","弄","桌","熟","诺","宣","银","势","奖","宫","忽","套","康","供","优","课","鸟","喊","降","夏","困","刘","罪","亡","鞋","健","模","败","伴","守","挥","鲜","财","孤","枪","禁","恐","伙","杰","迹","妹","遍","盖","副","坦","牌","江","顺","秋","萨","菜","划","授","归","浪","听","凡","预","奶","雄","升","编","典","袋","莱","含","盛","济","蒙","棋","端","腿","招","释","介","烧"],
    EMAIL : function() {
        return getRandomData('@LETTER_LOWER')
            + '.'
            + getRandomData('@LAST_NAME').toLowerCase()
            + '@'
            + getRandomData('@LAST_NAME').toLowerCase()
            + '.com';
    },
    DATE_YYYY : function() {
        var yyyy = randomDate().getFullYear();
        return yyyy + '';
    },
    DATE_DD : function() {
        return pad(randomDate().getDate());
    },
    DATE_MM : function() {
        return pad(randomDate().getMonth() + 1);
    },
    TIME_HH : function() {
        return pad(randomDate().getHours());
    },
    TIME_MM : function() {
        return pad(randomDate().getMinutes());
    },
    TIME_SS : function() {
        return pad(randomDate().getSeconds());
    },
    LOREM : function() {
        var words = 'lorem ipsum dolor sit amet consectetur adipisicing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua Ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur Excepteur sint occaecat cupidatat non proident sunt in culpa qui officia deserunt mollit anim id est laborum'.split(' ');
        var index = Math.floor(rand() * words.length);
        return words[index];
    },
    LOREM_IPSUM : function() {
        var words = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum'.split(' ');
        var result = [];
        var length = Math.floor(rand() * words.length / 2);
        for (var i = 0; i < length; i++) {
            var index = Math.floor(rand() * words.length);
            result.push(words[index]);
        }
        return result.join(' ');
    },
    NOW_DATETIME:function(){
        var n = new Date()
        return n.getFullYear()+'-'+(n.getMonth()+1)+'-'+n.getDate()+' '+n.getHours()+':'+n.getMinutes()+':'+n.getSeconds();
    },
    TIMESTAMP: function(){
        var n = new Date()
        return n.getTime();
    },
    NOW_DATE: function(){
        var n = new Date()
        return n.getFullYear()+'-'+(n.getMonth()+1)+'-'+n.getDate()
    },
    UUID4: function(){
        var d = new Date().getTime();
        var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = (d + Math.random()*16)%16 | 0;
            d = Math.floor(d/16);
            return (c=='x' ? r : (r&0x3|0x8)).toString(16);
        });
        return uuid;
    },
    DECIMAL1: function(){
        return parseFloat(Math.floor(Math.random()*10)+"."+Math.floor(Math.random()*10))
    },
    DECIMAL2: function(){
        return parseFloat(Math.floor(Math.random()*10)+"."+Math.floor(Math.random()*100))
    },
    DECIMAL3: function(){
        return parseFloat(Math.floor(Math.random()*10)+"."+Math.floor(Math.random()*1000))
    },
    DECIMAL3: function(){
        return parseFloat(Math.floor(Math.random()*10)+"."+Math.floor(Math.random()*10000))
    },
    DECIMAL5: function(){
        return parseFloat(Math.floor(Math.random()*10)+"."+Math.floor(Math.random()*100000))
    }
};


})(jQuery);