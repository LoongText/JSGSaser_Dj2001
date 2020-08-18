// 退出
function login_out() {
    layer.confirm('确定退出吗？', {icon: 3}, function (e) {
        $.ajax({
            url: '/back/login_out/',
            dataType: 'json',
            type: 'get',
            async: true,
            success: function (res) {
                // closewin()
            },
            error: function (res) {
                console.log(res)
            },
            complete: function (jqXHR, textStatus) {
                // window.open('http://wlaq.cnki.net/vue-jsg/#/', '_self')
                window.open('http://wlaq.cnki.net/vue-jsg/#/', '_self')
                // window.open('http://10.170.128.108:8088/static/dist/index.html#/', '_self')
            },
        });
    });
    //window.open("/back/login_out/", "_self")
}

// 不同浏览器关闭打开的窗口
function closewin() {
    if (navigator.userAgent.indexOf("Firefox") != -1 || navigator.userAgent.indexOf("Chrome") != -1) {
        // window.location.href = "about:blank";
        // window.close();

        window.opener = null;
        window.open(' ', '_self');
        window.close();
    } else {
        window.opener = null;
        window.open("", "_self");
        window.close();
    }
}