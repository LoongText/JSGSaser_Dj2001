// -----------招标开始---------------
//招标填充详情函数
function show_detail(data) {
    // console.log('1111111');
    //移除旧数据结构
    if ($("#pop-content-con-id")) {
        $("#pop-content-con-id").remove();
    }
    if ($(".stamp-box")) {
        $(".stamp-box").remove();
    }
    //邮戳
    var $stamp_div = $('<div class="stamp-box"></div>');
    var $stamp_div_img = $('<img src="/static/backstage/images/stamp.png" alt="">');
    var $stamp_div_p = $('<p class="txt"></p>');

    //定义新数据结构
    var $divW = $('<div class="pop-content-con" id="pop-content-con-id"></div>');
    var $divForm = $('<form method="post" enctype="multipart/form-data" class="form-horizontal"></form>');
    // 开始时间
    var $divF_div = $('<div class="row form-group"></div>');
    var $divF_div_div = $('<div class="col col-md-3"></div>');
    var $divF_div_div_label = $('<label for="disabled-input" class=" form-control-label">开始时间</label>');
    var $divF_div_div2 = $('<div class="col-12 col-md-9"></div>');
    var $divF_div_div2_input = $('<input type="text" id="re-start_date" value="" disabled="" class="form-control">');
    // 结束时间
    var $divF_div2 = $('<div class="row form-group"></div>');
    var $divF_div2_div = $('<div class="col col-md-3"></div>');
    var $divF_div2_div_label = $('<label for="disabled-input" class=" form-control-label">结束时间</label>');
    var $divF_div2_div2 = $('<div class="col-12 col-md-9"></div>');
    var $divF_div2_div2_input = $('<input type="text" id="re-end_date" value="" disabled="" class="form-control">');
    // 分类
    var $divF_div3 = $('<div class="row form-group"></div>');
    var $divF_div3_div = $('<div class="col col-md-3"></div>');
    var $divF_div3_div_label = $('<label for="disabled-input" class=" form-control-label">分类</label>');
    var $divF_div3_div2 = $('<div class="col-12 col-md-9"></div>');
    var $divF_div3_div2_input = $('<input type="text" id="re-classify" value="" disabled="" class="form-control">');
    // 经费
    var $divF_div4 = $('<div class="row form-group"></div>');
    var $divF_div4_div = $('<div class="col col-md-3"></div>');
    var $divF_div4_div_label = $('<label for="disabled-input" class=" form-control-label">经费/万元</label>');
    var $divF_div4_div2 = $('<div class="col-12 col-md-9"></div>');
    var $divF_div4_div2_input = $('<input type="text" id="re-funds" value="" disabled="" class="form-control">');
    // 具体要求
    var $divF_div5 = $('<div class="row form-group"></div>');
    var $divF_div5_div = $('<div class="col col-md-3"></div>');
    var $divF_div5_div_label = $('<label for="disabled-input" class=" form-control-label">具体要求</label>');
    var $divF_div5_div2 = $('<div class="col-12 col-md-9"></div>');
    var $divF_div5_div2_text = $('<textarea id="re-brief" rows="9" disabled="" class="form-control"></textarea>');
    // 联系人
    var $divF_div6 = $('<div class="row form-group"></div>');
    var $divF_div6_div = $('<div class="col col-md-3"></div>');
    var $divF_div6_div_label = $('<label for="disabled-input" class=" form-control-label">联系人</label>');
    var $divF_div6_div2 = $('<div class="col-12 col-md-9"></div>');
    var $divF_div6_div2_input = $('<input type="text" id="re-contacts" value="" disabled="" class="form-control">');
    // 联系电话
    var $divF_div7 = $('<div class="row form-group"></div>');
    var $divF_div7_div = $('<div class="col col-md-3"></div>');
    var $divF_div7_div_label = $('<label for="disabled-input" class=" form-control-label">联系人电话</label>');
    var $divF_div7_div2 = $('<div class="col-12 col-md-9"></div>');
    var $divF_div7_div2_input = $('<input type="text" id="re-phone" value="" disabled="" class="form-control">');
    // 状态
    // var $divF_div8 = $('<div class="row form-group"></div>');
    // var $divF_div8_div = $('<div class="col col-md-3"></div>');
    // var $divF_div8_div_label = $('<label for="disabled-input" class=" form-control-label">状态</label>');
    // var $divF_div8_div2 = $('<div class="col-12 col-md-9"></div>');
    // var $divF_div8_div2_input = $('<input type="text" id="re-status" value="" disabled="" class="form-control">');
    // 组织方
    var $divF_div9 = $('<div class="row form-group"></div>');
    var $divF_div9_div = $('<div class="col col-md-3"></div>');
    var $divF_div9_div_label = $('<label for="disabled-input" class=" form-control-label">组织方</label>');
    var $divF_div9_div2 = $('<div class="col-12 col-md-9"></div>');
    var $divF_div9_div2_input = $('<input type="text" id="re-user" value="" disabled="" class="form-control">');
    //获取数据对象
    var con = data;
    // 开始时间
    $divF_div_div2_input.attr('value', con.start_date);
    $divF_div_div.append($divF_div_div_label);
    $divF_div_div2.append($divF_div_div2_input);
    $divF_div.append($divF_div_div);
    $divF_div.append($divF_div_div2);
    $divForm.append($divF_div);
    // 结束时间
    $divF_div2_div2_input.attr('value', con.end_date);
    $divF_div2_div.append($divF_div2_div_label);
    $divF_div2_div2.append($divF_div2_div2_input);
    $divF_div2.append($divF_div2_div);
    $divF_div2.append($divF_div2_div2);
    $divForm.append($divF_div2);
    // 分类
    $divF_div3_div2_input.attr('value', con.classify__cls_name);
    $divF_div3_div.append($divF_div3_div_label);
    $divF_div3_div2.append($divF_div3_div2_input);
    $divF_div3.append($divF_div3_div);
    $divF_div3.append($divF_div3_div2);
    $divForm.append($divF_div3);
    // 经费
    $divF_div4_div2_input.attr('value', con.funds);
    $divF_div4_div.append($divF_div4_div_label);
    $divF_div4_div2.append($divF_div4_div2_input);
    $divF_div4.append($divF_div4_div);
    $divF_div4.append($divF_div4_div2);
    $divForm.append($divF_div4);
    // 具体要求
    $divF_div5_div2_text.text(con.brief);
    $divF_div5_div.append($divF_div5_div_label);
    $divF_div5_div2.append($divF_div5_div2_text);
    $divF_div5.append($divF_div5_div);
    $divF_div5.append($divF_div5_div2);
    $divForm.append($divF_div5);
    // 联系人
    $divF_div6_div2_input.attr('value', con.contacts);
    $divF_div6_div.append($divF_div6_div_label);
    $divF_div6_div2.append($divF_div6_div2_input);
    $divF_div6.append($divF_div6_div);
    $divF_div6.append($divF_div6_div2);
    $divForm.append($divF_div6);
    // 联系电话
    $divF_div7_div2_input.attr('value', con.phone);
    $divF_div7_div.append($divF_div7_div_label);
    $divF_div7_div2.append($divF_div7_div2_input);
    $divF_div7.append($divF_div7_div);
    $divF_div7.append($divF_div7_div2);
    $divForm.append($divF_div7);
    // 状态
    // $divF_div8_div2_input.attr('value', con.status);
    // $divF_div8_div.append($divF_div8_div_label);
    // $divF_div8_div2.append($divF_div8_div2_input);
    // $divF_div8.append($divF_div8_div);
    // $divF_div8.append($divF_div8_div2);
    // $divForm.append($divF_div8);
    // 组织方
    $divF_div9_div2_input.attr('value', con.user__username);
    $divF_div9_div.append($divF_div9_div_label);
    $divF_div9_div2.append($divF_div9_div2_input);
    $divF_div9.append($divF_div9_div);
    $divF_div9.append($divF_div9_div2);
    $divForm.append($divF_div9);

    //邮戳
    $stamp_div_p.text(con.status);
    $stamp_div.append($stamp_div_img);
    $stamp_div.append($stamp_div_p);

    $divW.append($stamp_div);
    $divW.append($divForm);
    $('.pop-content').append($divW);
}

// 招标查看详情传值
function detail_bt(uuid) {
    // var uuid = $(this).attr('data-uuid');
    $.ajax({
        url: "/back/rd",
        type: "GET",
        data: {'uuid': uuid},
        success: function (data) {
            // console.log(data);
            con = data.data;
            $('#re-name').text(con.name);
            show_detail(con);
            $('.bgPop,.pop').show();
        },

        error: function (jqXHR, textStatus, err) {
            console.log(arguments);
        },

        complete: function (jqXHR, textStatus) {
            console.log(textStatus);
        },

        statusCode: {
            '403': function (jqXHR, textStatus, err) {
                console.log(arguments);
            },

            '400': function (jqXHR, textStatus, err) {
                console.log(arguments);
            }
        }
    })
}

//招标添加
function research_add(param) {
    var re_name = $('#research-add-re-name').val();
    var re_date = $('#research-add-re-date').val();
    if (re_name === '') {
        layer.alert("题名不能为空！", {icon: 0}, function (index) {
            layer.close(index);
        });
    } else if (re_date === '') {
        layer.alert("起止日期不能为空！", {icon: 0}, function (index) {
            layer.close(index);
        });
    } else {
        $('#research-add-bt-value').val(param);
        var data = new FormData($("#research-add-form")[0]);
        $.ajax({
            url: "/back/rm_add",
            type: "POST",
            data: data,
            processData: false,   // 告诉jQuery不要处理数据
            contentType: false,   // 告诉jQuery不要设置类型
            success: function (res) {
                console.log(res);
                if (res == 200) {
                    layer.alert("操作成功", {icon: 1}, function (index) {
                        layer.close(index);
                        window.open('/back/rm', '_self')
                    });
                } else {
                    layer.alert("操作失败，请联系管理员", {icon: 2}, function (index) {
                        layer.close(index)
                    });
                }

            },

            error: function (jqXHR, textStatus, err) {
                console.log(arguments);
            },

            complete: function (jqXHR, textStatus) {
                console.log(textStatus);
            },

            statusCode: {
                '403': function (jqXHR, textStatus, err) {
                    console.log(arguments);
                },

                '400': function (jqXHR, textStatus, err) {
                    console.log(arguments);
                }
            }
        })
    }
}

// 招标编辑
function research_edit(param) {
    var re_name = $('#research-edit-re-name').val();
    var re_date = $('#research-edit-re-date').val();
    if (re_name === '') {
        layer.alert("题名不能为空！", {icon: 0}, function (index) {
            layer.close(index);
        });
    } else if (re_date === '') {
        layer.alert("起止日期不能为空！", {icon: 0}, function (index) {
            layer.close(index);
        });
    } else {
        $('#research-edit-bt-value').val(param);
        var data = new FormData($("#research-edit-form")[0]);
        $.ajax({
            url: "/back/rm_ed",
            type: "POST",
            data: data,
            processData: false,   // 告诉jQuery不要处理数据
            contentType: false,   // 告诉jQuery不要设置类型
            success: function (res) {
                console.log(res);
                if (res == 200) {
                    layer.alert("操作成功", {icon: 1}, function (index) {
                        layer.close(index);
                        window.open('/back/rm', '_self')
                    });
                } else {
                    layer.alert("操作失败，请联系管理员", {icon: 2}, function (index) {
                        layer.close(index)
                    });
                }

            },

            error: function (jqXHR, textStatus, err) {
                console.log(arguments);
            },

            complete: function (jqXHR, textStatus) {
                console.log(textStatus);
            },

            statusCode: {
                '403': function (jqXHR, textStatus, err) {
                    console.log(arguments);
                },

                '400': function (jqXHR, textStatus, err) {
                    console.log(arguments);
                }
            }
        })
    }
}

// -----------招标结束---------------


// -----------投标开始---------------
// 投标编辑
function bid_edit(param) {
    $('#bid-edit-bt-value').val(param);
    var data = new FormData($("#bid-edit-form")[0]);
    $.ajax({
        url: "/back/bm_ed",
        type: "POST",
        data: data,
        processData: false,   // 告诉jQuery不要处理数据
        contentType: false,   // 告诉jQuery不要设置类型
        success: function (res) {
            console.log(res);
            if (res == 200) {
                layer.alert("操作成功", {icon: 1}, function (index) {
                    layer.close(index);
                    window.open('/back/bm', '_self')
                });
            } else {
                layer.alert("操作失败，请联系管理员", {icon: 2}, function (index) {
                    layer.close(index)
                });
            }

        },

        error: function (jqXHR, textStatus, err) {
            console.log(arguments);
        },

        complete: function (jqXHR, textStatus) {
            console.log(textStatus);
        },

        statusCode: {
            '403': function (jqXHR, textStatus, err) {
                console.log(arguments);
            },

            '400': function (jqXHR, textStatus, err) {
                console.log(arguments);
            }
        }
    })
}

// 填充审批投标函数
function show_bidder(data) {
    // console.log('222222');
    //移除旧数据结构
    if ($('#pop-content-con-id')) {
        $('#pop-content-con-id').remove();
    }
    if ($('.stamp-box')) {
        $('.stamp-box').remove();
    }
    //定义新数据结构
    var $divW = $('<div class="pop-content-con" id="pop-content-con-id"></div>');
    var $divButton1 = $('<button type="button" class="btn btn-outline-success btn-sm " style="margin-right: 15px; margin-bottom: 10px" onclick="bidder_more_agree(1)">批量同意</button>');
    var $divButton2 = $('<button type="button" class="btn btn-outline-danger btn-sm " style="margin-bottom: 10px" onclick="bidder_more_agree(0)">批量驳回</button>');
    var $divTable = $('<table id="bootstrap-data-table-export" class="table table-striped table-bordered"></table>');
    // 表头
    var $divT_thead = $('<thead></thead>>');
    var $divF_thead_tr = $('<tr></tr>');
    var $divF_thead_tr_th0 = $('<th><input type="checkbox" name="all-checkbox" id="all_checked_id" onclick="all_checked()"></th>');
    var $divF_thead_tr_th1 = $('<th>申报课题名称</th>');
    var $divF_thead_tr_th2 = $('<th>申报单位</th>');
    var $divF_thead_tr_th3 = $('<th>负责人</th>');
    var $divF_thead_tr_th4 = $('<th>负责人电话</th>');
    // var $divF_thead_tr_th5 = $('<th>联系人</th>');
    // var $divF_thead_tr_th6 = $('<th>联系人电话</th>');
    var $divF_thead_tr_th7 = $('<th>申报时间</th>');
    var $divF_tbody = $('<tbody></tbody>');
    //每一行
    var $divF_tbody_tr = $('<tr class="single-tr-count"></tr>');
    var $divF_tbody_tr_td0 = $('<td><input type="checkbox" name="checkbox" onclick="single_more_checked()"></td>');
    var $divF_tbody_tr_td1 = $('<td></td>');
    var $divF_tbody_tr_td1_a = $('<a></a>');
    var $divF_tbody_tr_td2 = $('<td></td>');
    var $divF_tbody_tr_td3 = $('<td></td>');
    var $divF_tbody_tr_td4 = $('<td></td>');
    // var $divF_tbody_tr_td5 = $('<td></td>');
    // var $divF_tbody_tr_td6 = $('<td></td>');
    var $divF_tbody_tr_td7 = $('<td></td>');

    $divF_thead_tr.append($divF_thead_tr_th0);
    $divF_thead_tr.append($divF_thead_tr_th1);
    $divF_thead_tr.append($divF_thead_tr_th2);
    $divF_thead_tr.append($divF_thead_tr_th3);
    $divF_thead_tr.append($divF_thead_tr_th4);
    // $divF_thead_tr.append($divF_thead_tr_th5);
    // $divF_thead_tr.append($divF_thead_tr_th6);
    $divF_thead_tr.append($divF_thead_tr_th7);
    $divT_thead.append($divF_thead_tr);

    var con = data;
    for (var i = 0; i < con.length; i++) {
        $divF_tbody_tr_c = $divF_tbody_tr.clone();
        $divF_tbody_tr_td0_c = $divF_tbody_tr_td0.clone();
        $divF_tbody_tr_td1_c = $divF_tbody_tr_td1.clone();
        $divF_tbody_tr_td1_a_c = $divF_tbody_tr_td1_a.clone();
        $divF_tbody_tr_td2_c = $divF_tbody_tr_td2.clone();
        $divF_tbody_tr_td3_c = $divF_tbody_tr_td3.clone();
        $divF_tbody_tr_td4_c = $divF_tbody_tr_td4.clone();
        // $divF_tbody_tr_td5_c = $divF_tbody_tr_td5.clone();
        // $divF_tbody_tr_td6_c = $divF_tbody_tr_td6.clone();
        $divF_tbody_tr_td7_c = $divF_tbody_tr_td7.clone();

        $divF_tbody_tr_c.attr('data-id', con[i]['id']);
        $divF_tbody_tr_td1_a_c.text(con[i]['re_title']);
        $divF_tbody_tr_td1_a_c.attr('href', '/back/bd?single=1&uuid=' + con[i]['id']);
        $divF_tbody_tr_td1_a_c.attr('target', '_blank');
        $divF_tbody_tr_td2_c.text(con[i]['bidder']);
        $divF_tbody_tr_td3_c.text(con[i]['leader']);
        $divF_tbody_tr_td4_c.text(con[i]['lea_phone']);
        // $divF_tbody_tr_td5_c.text(con[i]['contacts']);
        // $divF_tbody_tr_td6_c.text(con[i]['con_phone']);
        $divF_tbody_tr_td7_c.text(con[i]['bidder_date']);

        $divF_tbody_tr_c.append($divF_tbody_tr_td0_c);
        $divF_tbody_tr_td1_c.append($divF_tbody_tr_td1_a_c);
        $divF_tbody_tr_c.append($divF_tbody_tr_td1_c);
        $divF_tbody_tr_c.append($divF_tbody_tr_td2_c);
        $divF_tbody_tr_c.append($divF_tbody_tr_td3_c);
        $divF_tbody_tr_c.append($divF_tbody_tr_td4_c);
        // $divF_tbody_tr_c.append($divF_tbody_tr_td5_c);
        // $divF_tbody_tr_c.append($divF_tbody_tr_td6_c);
        $divF_tbody_tr_c.append($divF_tbody_tr_td7_c);
        $divF_tbody.append($divF_tbody_tr_c);
    }

    $divTable.append($divT_thead);
    $divTable.append($divF_tbody);
    $divW.append($divButton1);
    $divW.append($divButton2);
    $divW.append($divTable);
    $('.pop-content').append($divW);
}

//投标审批
function toubiao_bt(uuid) {
    // var uuid = $(this).attr('data-id');
    $.ajax({
        url: "/back/rm_bid",
        type: "GET",
        data: {'id': uuid},
        success: function (data) {
            con = data.data;
            // $('.stamp-box').remove();
            $('#re-name').text('项目名称：' + data.re_name);
            show_bidder(con);
            $('.bgPop,.pop').show();
        },

        error: function (jqXHR, textStatus, err) {
            console.log(arguments);
        },

        complete: function (jqXHR, textStatus) {
            console.log(textStatus);
        },

        statusCode: {
            '403': function (jqXHR, textStatus, err) {
                console.log(arguments);
            },

            '400': function (jqXHR, textStatus, err) {
                console.log(arguments);
            }
        }
    })
}

//申请批量同意/驳回
function bidder_more_agree(is_true) {
    if (bidder_checked_list.length != 0) {
        layer.confirm('此操作不可逆,请谨慎操作！', {icon: 0}, function (e) {
            $.ajax({
                url: '/back/rm_bid',
                dataType: 'json',
                type: 'post',
                async: true,
                data: {
                    'id_list': JSON.stringify(bidder_checked_list),
                    'is_true': JSON.stringify(is_true)
                },
                success: function (res) {
                    // console.log(res);
                    if (res != 0) {
                        layer.alert('操作成功', {icon: 1}, function (index) {
                            layer.close(index);
                            var url = '/back/rm';
                            window.open(url, '_self')
                        });
                    } else {
                        layer.msg('出现故障！', {icon: 2});
                    }
                },
                error: function (res) {
                    console.log(res)
                }
            })
        });
    } else {
        layer.msg('请选择要操作的数据！', {icon: 2});
    }
}

//投标搜索
function bid_search(keyword) {
    console.log('keyword---' + keyword);
    // 用哪个按钮，方法不一样
    var currentBtn0 = document.getElementById('pop-search-button3');
    currentBtn0.style.display = "";
    var currentBtn = document.getElementById('pop-search-button');
    currentBtn.style.display = "none";
    var currentBtn2 = document.getElementById('pop-search-button2');
    currentBtn2.style.display = "none";
    $.ajax({
        url: "/back/bid_search",
        type: "GET",
        data: {'keyword': keyword},
        success: function (data) {
            console.log(data);
            con = data.data;
            var bid_id = $('#pro-bid-input-hidden').val();
            bid_search_show(con, bid_id);
            $('.bgPop,.pop').show();
        },

        error: function (jqXHR, textStatus, err) {
            console.log(arguments);
        },

        complete: function (jqXHR, textStatus) {
            console.log(textStatus);
        },

        statusCode: {
            '403':

                function (jqXHR, textStatus, err) {
                    console.log(arguments);
                },

            '400':

                function (jqXHR, textStatus, err) {
                    console.log(arguments);
                }
        }
    })
}

// 搜索投标结构填充
function bid_search_show(data, bid_id) {
    //移除旧数据结构
    if ($('#pop-content-con-id')) {
        $('#pop-content-con-id').remove();
    }
    //定义新数据结构
    var $divW = $('<div class="pop-content-con" id="pop-content-con-id"></div>');
    var $divTable = $('<table class="table table-striped table-bordered"></table>');
    // 表头
    var $divT_thead = $('<thead></thead>>');
    var $divF_thead_tr = $('<tr></tr>');
    var $divF_thead_tr_th1 = $('<th>课题名称</th>');
    var $divF_thead_tr_th2 = $('<th>投标时间</th>');
    var $divF_thead_tr_th4 = $('<th></th>');
    var $divF_tbody = $('<tbody></tbody>');
    //每一行
    var $divF_tbody_tr = $('<tr></tr>');
    var $divF_tbody_tr_td1 = $('<td></td>');
    var $divF_tbody_tr_td2 = $('<td></td>');
    var $divF_tbody_tr_td4 = $('<td></td>');
    var $divF_tbody_tr_td4_bt = $('<button class="btn btn-success btn-sm" onclick="bid_click_add(this)">选择</button>');
    var $divF_tbody_tr_td4_bt2 = $('<button class="btn btn-outline-secondary btn-sm">已选择</button>');

    $divF_thead_tr.append($divF_thead_tr_th1);
    $divF_thead_tr.append($divF_thead_tr_th2);
    $divF_thead_tr.append($divF_thead_tr_th4);
    $divT_thead.append($divF_thead_tr);
    var con = data;
    for (var i = 0; i < con.length; i++) {
        $divF_tbody_tr_c = $divF_tbody_tr.clone();
        $divF_tbody_tr_td1_c = $divF_tbody_tr_td1.clone();
        $divF_tbody_tr_td2_c = $divF_tbody_tr_td2.clone();
        $divF_tbody_tr_td4_c = $divF_tbody_tr_td4.clone();
        $divF_tbody_tr_td4_bt_c = $divF_tbody_tr_td4_bt.clone();
        $divF_tbody_tr_td4_bt2_c = $divF_tbody_tr_td4_bt2.clone();

        $divF_tbody_tr_td1_c.text(con[i]['re_title']);
        $divF_tbody_tr_td2_c.text(con[i]['bidder_date']);
        $divF_tbody_tr_td4_bt_c.attr('data-name', con[i]['re_title']);
        $divF_tbody_tr_td4_bt_c.attr('data-id', con[i]['id']);

        $divF_tbody_tr_c.append($divF_tbody_tr_td1_c);
        $divF_tbody_tr_c.append($divF_tbody_tr_td2_c);

        // 判断是否已添加
        if (String(bid_id)===String(con[i]['id'])) {
            $divF_tbody_tr_td4_c.append($divF_tbody_tr_td4_bt2_c);
        } else {
            $divF_tbody_tr_td4_c.append($divF_tbody_tr_td4_bt_c);
        }


        $divF_tbody_tr_c.append($divF_tbody_tr_td4_c);
        $divF_tbody.append($divF_tbody_tr_c);
    }

    $divTable.append($divT_thead);
    $divTable.append($divF_tbody);
    $divW.append($divTable);
    $('.pop-content').append($divW);
}

//点击添加
function bid_click_add(obj) {
    var bid_value = $(obj).attr('data-name');
    var bid_id = $(obj).attr('data-id');
    $('#pro-bid-input').val(bid_value);
    $('#pro-bid-input-hidden').val(bid_id);


    layer.alert("操作成功", {icon: 1}, function (index) {
        layer.close(index);
    });
    var item=$(obj).parents('#pop-content-con-id').find('.btn');
    item.addClass('btn-success');
    item.removeClass('btn-outline-secondary');
    item.text('选择');
    item.attr('onclick','bid_click_add(this)');

    $(obj).removeClass('btn-success');
    $(obj).addClass('btn-outline-secondary');
    $(obj).text('已选择');
    $(obj).removeAttr("onclick");

}

// -----------投标结束---------------

// -----------结题开始---------------
//结填充题审批函数
function show_bidder_jieti(data) {
    // console.log('222222');
    //移除旧数据结构
    if ($('#pop-content-con-id')) {
        $('#pop-content-con-id').remove();
    }
    if ($('.stamp-box')) {
        $('.stamp-box').remove();
    }
    //定义新数据结构
    var $divW = $('<div class="pop-content-con" id="pop-content-con-id"></div>');
    var $divButton1 = $('<button type="button" class="btn btn-outline-success btn-sm " style="margin-right: 15px; margin-bottom: 10px" onclick="jieti_more_agree(1)">批量同意</button>');
    var $divButton2 = $('<button type="button" class="btn btn-outline-danger btn-sm " style="margin-bottom: 10px" onclick="jieti_more_agree(0)">批量驳回</button>');
    var $divTable = $('<table id="bootstrap-data-table-export" class="table table-striped table-bordered"></table>');
    // 表头
    var $divT_thead = $('<thead></thead>>');
    var $divF_thead_tr = $('<tr></tr>');
    var $divF_thead_tr_th0 = $('<th><input type="checkbox" name="all-checkbox" id="all_checked_id" onclick="all_checked()"></th>');
    var $divF_thead_tr_th1 = $('<th>申报课题名称</th>');
    var $divF_thead_tr_th2 = $('<th>申报单位</th>');
    // var $divF_thead_tr_th3 = $('<th>负责人</th>');
    // var $divF_thead_tr_th4 = $('<th>负责人电话</th>');
    // var $divF_thead_tr_th5 = $('<th>联系人</th>');
    // var $divF_thead_tr_th6 = $('<th>联系人电话</th>');
    var $divF_thead_tr_th7 = $('<th>申报时间</th>');
    // var $divF_thead_tr_th8 = $('<th>成果报告</th>');
    var $divF_tbody = $('<tbody></tbody>');
    //每一行
    var $divF_tbody_tr = $('<tr class="single-tr-count"></tr>');
    var $divF_tbody_tr_td0 = $('<td><input type="checkbox" name="checkbox" onclick="single_more_checked()"></td>');
    var $divF_tbody_tr_td1 = $('<td></td>');
    var $divF_tbody_tr_td2 = $('<td></td>');
    // var $divF_tbody_tr_td3 = $('<td></td>');
    // var $divF_tbody_tr_td4 = $('<td></td>');
    // var $divF_tbody_tr_td5 = $('<td></td>');
    // var $divF_tbody_tr_td6 = $('<td></td>');
    var $divF_tbody_tr_td7 = $('<td></td>');
    // var $divF_tbody_tr_td8 = $('<td></td>');
    // var $divF_tbody_tr_td8_a = $('<a></a>');

    $divF_thead_tr.append($divF_thead_tr_th0);
    $divF_thead_tr.append($divF_thead_tr_th1);
    $divF_thead_tr.append($divF_thead_tr_th2);
    // $divF_thead_tr.append($divF_thead_tr_th3);
    // $divF_thead_tr.append($divF_thead_tr_th4);
    // $divF_thead_tr.append($divF_thead_tr_th5);
    // $divF_thead_tr.append($divF_thead_tr_th6);
    $divF_thead_tr.append($divF_thead_tr_th7);
    // $divF_thead_tr.append($divF_thead_tr_th8);
    $divT_thead.append($divF_thead_tr);

    var con = data;
    for (var i = 0; i < con.length; i++) {
        $divF_tbody_tr_c = $divF_tbody_tr.clone();
        $divF_tbody_tr_td0_c = $divF_tbody_tr_td0.clone();
        $divF_tbody_tr_td1_c = $divF_tbody_tr_td1.clone();
        $divF_tbody_tr_td2_c = $divF_tbody_tr_td2.clone();
        // $divF_tbody_tr_td3_c = $divF_tbody_tr_td3.clone();
        // $divF_tbody_tr_td4_c = $divF_tbody_tr_td4.clone();
        // $divF_tbody_tr_td5_c = $divF_tbody_tr_td5.clone();
        // $divF_tbody_tr_td6_c = $divF_tbody_tr_td6.clone();
        $divF_tbody_tr_td7_c = $divF_tbody_tr_td7.clone();
        // $divF_tbody_tr_td8_a_c = $divF_tbody_tr_td8_a.clone();
        // $divF_tbody_tr_td8_c = $divF_tbody_tr_td8.clone();

        $divF_tbody_tr_c.attr('data-id', con[i]['id']);
        $divF_tbody_tr_td1_c.text(con[i]['re_title']);
        $divF_tbody_tr_td2_c.text(con[i]['bidder']);
        // $divF_tbody_tr_td3_c.text(con[i]['leader']);
        // $divF_tbody_tr_td4_c.text(con[i]['lea_phone']);
        // $divF_tbody_tr_td5_c.text(con[i]['contacts']);
        // $divF_tbody_tr_td6_c.text(con[i]['con_phone']);
        $divF_tbody_tr_td7_c.text(con[i]['bidder_date']);
        // $divF_tbody_tr_td8_a_c.attr('href', '/static/' + con[i]['pro_attached']);
        // $divF_tbody_tr_td8_a_c.attr('target', '_blank');
        // $divF_tbody_tr_td8_a_c.text(con[i]['pro_name']);

        $divF_tbody_tr_c.append($divF_tbody_tr_td0_c);
        $divF_tbody_tr_c.append($divF_tbody_tr_td1_c);
        $divF_tbody_tr_c.append($divF_tbody_tr_td2_c);
        // $divF_tbody_tr_c.append($divF_tbody_tr_td3_c);
        // $divF_tbody_tr_c.append($divF_tbody_tr_td4_c);
        // $divF_tbody_tr_c.append($divF_tbody_tr_td5_c);
        // $divF_tbody_tr_c.append($divF_tbody_tr_td6_c);
        $divF_tbody_tr_c.append($divF_tbody_tr_td7_c);
        // $divF_tbody_tr_td8_c.append($divF_tbody_tr_td8_a_c);
        // $divF_tbody_tr_c.append($divF_tbody_tr_td8_c);
        $divF_tbody.append($divF_tbody_tr_c);
    }

    $divTable.append($divT_thead);
    $divTable.append($divF_tbody);
    $divW.append($divButton1);
    $divW.append($divButton2);
    $divW.append($divTable);
    $('.pop-content').append($divW);
}

//结题审批
function jieti_sp_bt(uuid) {
    $.ajax({
        url: "/back/rm_bid_jt",
        type: "GET",
        data: {'id': uuid},
        success: function (data) {
            con = data.data;
            $('#re-name').text('项目名称：' + data.re_name);
            show_bidder_jieti(con);
            $('.bgPop,.pop').show();
        },

        error: function (jqXHR, textStatus, err) {
            console.log(arguments);
        },

        complete: function (jqXHR, textStatus) {
            console.log(textStatus);
        },

        statusCode: {
            '403': function (jqXHR, textStatus, err) {
                console.log(arguments);
            },

            '400': function (jqXHR, textStatus, err) {
                console.log(arguments);
            }
        }
    })
}

// 保存选中的招标对应的课题id值
var bidder_checked_list = [];

// 全选按钮事件
function all_checked() {
    // console.log(222);
    var checkItem = $("input[type=checkbox][name=all-checkbox]:checked");
    // console.log(checkItem);
    bidder_checked_list = [];
    if (checkItem.length > 0) {
        $('#pop-content-con-id table tbody tr').each(function () {
            // console.log(111);
            $(this).find('input').attr('checked', 'checked');
            bidder_checked_list.push($(this).attr('data-id'))
        })
    } else {
        $('#pop-content-con-id table tbody tr').each(function () {
            // console.log(333);
            $(this).find('input').removeAttr('checked')
        })
    }
    // console.log(bidder_checked_list)
}

//单独点击多选按钮--注意自行选择导致全选的情况
function single_more_checked() {
    // console.log(222);
    var trItem = $("tr[class=single-tr-count]");
    // console.log(trItem.length);
    bidder_checked_list = [];  // 点击前每一下都清空原先的id，重新遍历取值
    var checkItem = $("input[type=checkbox][name=checkbox]:checked");

    if (checkItem.length == trItem.length) {
        $('#all_checked_id').attr('checked', 'checked');
    } else {
        $('#all_checked_id').removeAttr('checked');
    }
    $('#pop-content-con-id table tbody tr').each(function () {
        if ($(this).find('input').is(":checked")) {
            bidder_checked_list.push($(this).attr('data-id'))
        }
    });
    // console.log(bidder_checked_list)
}

//结题批量同意/驳回
function jieti_more_agree(is_true) {
    if (bidder_checked_list.length != 0) {
        layer.confirm('此操作不可逆,请谨慎操作！', {icon: 0}, function (e) {
            var data = {
                "id_list": JSON.stringify(bidder_checked_list),
                "is_true": JSON.stringify(is_true)
            };
            $.ajax({
                url: '/back/rm_bid_jt',
                dataType: 'json',  //返回值格式
                type: 'post',
                async: true,
                data: data,
                success: function (res) {
                    // console.log(res);
                    if (res != 0) {
                        // layer.msg('操作成功！' ,{icon: 1});
                        layer.alert('操作成功！', {icon: 1}, function (index) {
                            layer.close(index);
                            window.location.reload();
                        });
                        // var url = '/back/rm';
                        // window.open(url, '_self')
                    } else {
                        // layer.msg('出现故障！', {icon: 2});
                        layer.alert('操作失败！请联系管理员', {icon: 2}, function (index) {
                            layer.close(index);
                        });
                    }
                },
                error: function (res) {
                    console.log(res)
                }
            })
        })
    } else {
        layer.msg('请选择要操作的数据！', {icon: 2});
    }
}

// -----------结题结束---------------

//------------成果开始---------------
//成果编辑
function pro_edit(param) {
    var pro_name = $('#pro_edit_pro_name').val();
    if (pro_name === '') {
        layer.alert("成果名称不能为空！", {icon: 0}, function (index) {
            layer.close(index)
        });
    } else {
        $('#project-edit-bt-value').val(param);
        var data = new FormData($("#project-edit-form")[0]);
        $.ajax({
            url: "/back/pm_ed",
            type: "POST",
            data: data,
            processData: false,   // 告诉jQuery不要处理数据
            contentType: false,   // 告诉jQuery不要设置类型
            success: function (res) {
                console.log('成果编辑' + res);
                if (res == 200) {
                    layer.alert("操作成功", {icon: 1}, function (index) {
                        layer.close(index);
                        window.open('/back/pm', '_self')
                    });
                } else {
                    layer.alert("操作失败，请联系管理员", {icon: 2}, function (index) {
                        layer.close(index)
                    });
                }

            },

            error: function (jqXHR, textStatus, err) {
                console.log(arguments);
            },

            complete: function (jqXHR, textStatus) {
                console.log(textStatus);
            },

            statusCode: {
                '403': function (jqXHR, textStatus, err) {
                    console.log(arguments);
                },

                '400': function (jqXHR, textStatus, err) {
                    console.log(arguments);
                }
            }
        })
    }
}

//成果添加
function pro_add(param) {
    var pro_name = $('#pro_add_pro_name').val();
    if (pro_name === '') {
        layer.alert("成果名称不能为空！", {icon: 0}, function (index) {
            layer.close(index)
        });
    } else {
        $('#project-add-bt-value').val(param);
        var data = new FormData($("#project-add-form")[0]);
        $.ajax({
            url: "/back/pro_add",
            type: "POST",
            // data: $('#project-add-form').serialize(),
            data: data,
            processData: false,   // 告诉jQuery不要处理数据
            contentType: false,   // 告诉jQuery不要设置类型
            success: function (res) {
                console.log(res);
                if (res == 200) {
                    layer.alert("创建成功", {icon: 1}, function (index) {
                        layer.close(index);
                        window.open('/back/pm', '_self')
                    });
                } else {
                    layer.alert("创建失败，请联系管理员", {icon: 2}, function (index) {
                        layer.close(index)
                    });
                }

            },

            error: function (jqXHR, textStatus, err) {
                console.log(arguments);
            },

            complete: function (jqXHR, textStatus) {
                console.log(textStatus);
            },

            statusCode: {
                '403': function (jqXHR, textStatus, err) {
                    console.log(arguments);
                },

                '400': function (jqXHR, textStatus, err) {
                    console.log(arguments);
                }
            }
        })
    }
}

// 添加课题小组--人员搜索
function par_search(keyword) {
    var currentBtn0 = document.getElementById('pop-search-button');
    currentBtn0.style.display = "";
    var currentBtn = document.getElementById('pop-search-button2');
    currentBtn.style.display = "none";
    var currentBtn3 = document.getElementById('pop-search-button3');
    currentBtn3.style.display = "none";
    $.ajax({
        url: "/back/par_search",
        type: "GET",
        data: {'keyword': keyword},
        success: function (data) {
            console.log(data);
            con = data.data;
            var par_id_list = [];
            $('#pro-edit-table-id tbody button').each(function () {
                par_id_list.push($(this).attr('data-id'))
            });
            par_search_show(con, par_id_list);
            $('.bgPop,.pop').show();
        },

        error: function (jqXHR, textStatus, err) {
            console.log(arguments);
        },

        complete: function (jqXHR, textStatus) {
            console.log(textStatus);
        },

        statusCode: {
            '403':

                function (jqXHR, textStatus, err) {
                    console.log(arguments);
                },

            '400':

                function (jqXHR, textStatus, err) {
                    console.log(arguments);
                }
        }
    })
}

//成果撤回
function withdraw(obj, url) {
    var uuid = $(obj).attr('data-uuid');
    layer.confirm('确定要撤回吗？', {icon: 3}, function (e) {
        $.post(url, {'uuid': uuid}, function (res) {
                if (res == 1) {
                    // $(obj).parents('tr').remove();
                    layer.alert('撤回成功', {icon: 1}, function (index) {
                        layer.close(index);
                        window.location.reload();
                    });
                } else {
                    layer.alert('操作失败，请联系管理员！', {icon: 2}, function (index) {
                        layer.close(index)
                    });
                }
            }
        )
    })

}

//------------成果结束---------------

// -----------用户开始---------------
//用户填充详情函数
function show_user_detail(data) {
    //移除旧数据结构
    if ($('#pop-content-con-id')) {
        $('#pop-content-con-id').remove();
    }
    //定义新数据结构
    var $divW = $('<div class="pop-content-con" id="pop-content-con-id"></div>');
    var $divForm = $('<form method="post" enctype="multipart/form-data" class="form-horizontal"></form>');
    // 昵称
    var $divF_div = $('<div class="row form-group"></div>');
    var $divF_div_div = $('<div class="col col-md-3"></div>');
    var $divF_div_div_label = $('<label for="disabled-input" class=" form-control-label">昵称</label>');
    var $divF_div_div2 = $('<div class="col-12 col-md-9"></div>');
    var $divF_div_div2_input = $('<input type="text" id="user-first_name" value="" disabled="" class="form-control">');
    // 关联机构
    var $divF_div2 = $('<div class="row form-group"></div>');
    var $divF_div2_div = $('<div class="col col-md-3"></div>');
    var $divF_div2_div_label = $('<label for="disabled-input" class=" form-control-label">关联机构</label>');
    var $divF_div2_div2 = $('<div class="col-12 col-md-9"></div>');
    var $divF_div2_div2_input = $('<input type="text" id="user-org" value="" disabled="" class="form-control">');
    // 创建时间
    var $divF_div3 = $('<div class="row form-group"></div>');
    var $divF_div3_div = $('<div class="col col-md-3"></div>');
    var $divF_div3_div_label = $('<label for="disabled-input" class=" form-control-label">加入时间</label>');
    var $divF_div3_div2 = $('<div class="col-12 col-md-9"></div>');
    var $divF_div3_div2_input = $('<input type="text" id="user-created" value="" disabled="" class="form-control">');
    // 最新登录时间
    var $divF_div4 = $('<div class="row form-group"></div>');
    var $divF_div4_div = $('<div class="col col-md-3"></div>');
    var $divF_div4_div_label = $('<label for="disabled-input" class=" form-control-label">最新登录时间</label>');
    var $divF_div4_div2 = $('<div class="col-12 col-md-9"></div>');
    var $divF_div4_div2_input = $('<input type="text" id="user-last_login" value="" disabled="" class="form-control">');

    //获取数据对象
    var con = data;
    // 昵称
    $divF_div_div2_input.attr('value', con.first_name);
    $divF_div_div.append($divF_div_div_label);
    $divF_div_div2.append($divF_div_div2_input);
    $divF_div.append($divF_div_div);
    $divF_div.append($divF_div_div2);
    $divForm.append($divF_div);
    // 关联机构
    $divF_div2_div2_input.attr('value', con.org__name);
    $divF_div2_div.append($divF_div2_div_label);
    $divF_div2_div2.append($divF_div2_div2_input);
    $divF_div2.append($divF_div2_div);
    $divF_div2.append($divF_div2_div2);
    $divForm.append($divF_div2);
    // 加入时间
    $divF_div3_div2_input.attr('value', con.date_joined);
    $divF_div3_div.append($divF_div3_div_label);
    $divF_div3_div2.append($divF_div3_div2_input);
    $divF_div3.append($divF_div3_div);
    $divF_div3.append($divF_div3_div2);
    $divForm.append($divF_div3);
    // 最新登陆时间
    $divF_div4_div2_input.attr('value', con.last_login);
    $divF_div4_div.append($divF_div4_div_label);
    $divF_div4_div2.append($divF_div4_div2_input);
    $divF_div4.append($divF_div4_div);
    $divF_div4.append($divF_div4_div2);
    $divForm.append($divF_div4);

    $divW.append($divForm);
    $('.pop-content').append($divW);
}

// 用户查看详情传值
function user_detail_bt(uuid) {
    $.ajax({
        url: "/back/userd",
        type: "GET",
        data: {'uuid': uuid},
        success: function (data) {
            // console.log(data);
            con = data.data;
            // console.log(con.name);
            $('#user-name').text(con.username);
            show_user_detail(con);

            $('.bgPop,.pop').show();
        },

        error: function (jqXHR, textStatus, err) {
            console.log(arguments);
        },

        complete: function (jqXHR, textStatus) {
            console.log(textStatus);
        },

        statusCode: {
            '403': function (jqXHR, textStatus, err) {
                console.log(arguments);
            },

            '400': function (jqXHR, textStatus, err) {
                console.log(arguments);
            }
        }
    })
}

//添加用户
function user_add_bt() {
    if ($('#user-org-rzjg').val() == '') {
        layer.alert("认证机构不能为空", {icon: 0}, function (index) {
            layer.close(index)
        });
    } else if ($('#user-username').val() == '') {
        layer.alert("用户名不能为空", {icon: 0}, function (index) {
            layer.close(index)
        });
    } else if ($('#user-password').val() == '') {
        layer.alert("密码不能为空", {icon: 0}, function (index) {
            layer.close(index)
        });
    } else {
        var data = new FormData($("#user-add-form")[0]);
        $.ajax({
            url: "/back/user_add",
            type: "POST",
            data: data,
            processData: false,   // 告诉jQuery不要处理数据
            contentType: false,   // 告诉jQuery不要设置类型
            success: function (res) {
                console.log(res);
                if (res == 201) {
                    layer.alert("创建成功", {icon: 1}, function (index) {
                        layer.close(index);
                        window.open('/back/user', '_self')
                    });
                } else if (res == 404) {
                    layer.alert("您输入的机构不存在，请重新选择或新建", {icon: 0}, function (index) {
                        layer.close(index)
                    });
                } else {
                    layer.alert("创建失败，请联系管理员", {icon: 2}, function (index) {
                        layer.close(index)
                    });
                }

            },

            error: function (jqXHR, textStatus, err) {
                console.log(arguments);
            },

            complete: function (jqXHR, textStatus) {
                console.log(textStatus);
            },

            statusCode: {
                '403': function (jqXHR, textStatus, err) {
                    console.log(arguments);
                },

                '400': function (jqXHR, textStatus, err) {
                    console.log(arguments);
                }
            }
        })
    }
}

//编辑用户
function user_edit_bt() {
    if ($('#user-org-rzjg').val() == '') {
        layer.alert("认证机构不能为空", {icon: 0}, function (index) {
            layer.close(index)
        });
    } else {
        var data = new FormData($("#user-edit-form")[0]);
        $.ajax({
            url: "/back/user_ed",
            type: "POST",
            data: data,
            processData: false,   // 告诉jQuery不要处理数据
            contentType: false,   // 告诉jQuery不要设置类型
            success: function (res) {
                console.log(res);
                if (res == 1) {
                    layer.alert("操作成功", {icon: 1}, function (index) {
                        layer.close(index);
                        window.open('/back/user', '_self')
                    });
                } else if (res == 404) {
                    layer.alert("您输入的机构不存在，请重新选择或新建", {icon: 0}, function (index) {
                        layer.close(index)
                    });
                } else {
                    layer.alert("操作失败，请联系管理员", {icon: 2}, function (index) {
                        layer.close(index)
                    });
                }

            },

            error: function (jqXHR, textStatus, err) {
                console.log(arguments);
            },

            complete: function (jqXHR, textStatus) {
                console.log(textStatus);
            },

            statusCode: {
                '403': function (jqXHR, textStatus, err) {
                    console.log(arguments);
                },

                '400': function (jqXHR, textStatus, err) {
                    console.log(arguments);
                }
            }
        })
    }
}

//用户查询认证机构
function user_org_select() {
    var input_keyword = $('#user-org-rzjg').val();
    $.ajax({
        url: "/back/user_org",
        type: "GET",
        data: {'input_keyword': input_keyword},
        success: function (data) {
            con = data.data;
            // console.log(con);
            //移除旧数据结构
            if ($('#org-rzjg-tj')) {
                $('#org-rzjg-tj div').remove();
            }
            var $c = $('<div onclick="org_tjxz_bt(this)"></div>');
            for (var i = 0; i < con.length; i++) {
                $c_c = $c.clone();
                var data_uuid = con[i].uuid;
                var data_name = con[i].name;
                $c_c.attr('data-uuid', data_uuid);
                $c_c.text(data_name);
                // console.log($c_c);
                $('#org-rzjg-tj').append($c_c);
            }
        },

        error: function (jqXHR, textStatus, err) {
            console.log(arguments);
        },

        complete: function (jqXHR, textStatus) {
            console.log(textStatus);
        },

        statusCode: {
            '403': function (jqXHR, textStatus, err) {
                console.log(arguments);
            },

            '400': function (jqXHR, textStatus, err) {
                console.log(arguments);
            }
        }
    })
}

function org_tjxz_bt(obj) {
    var uuid = $(obj).attr("data-uuid");
    var name = $(obj).text();
    $('#user-org-rzjg').val(name);
    $('#user-org-rzjg-uuid').attr('value', uuid);
    $('#org-rzjg-tj div').remove();
}

//验证用户名是否已存在
function verify_username_exist() {
    var username = $('#user-username').val();
    $.ajax({
        url: "/back/user_uname",
        type: "GET",
        data: {'username': username},
        success: function (res) {
            console.log(res);
            //移除旧数据结构
            if (res == 200) {
                layer.alert("用户名已存在，请从新输入！", {icon: 2}, function (index) {
                    $('#user-username').val('');
                    layer.close(index)
                });
            }

        },

        error: function (jqXHR, textStatus, err) {
            console.log(arguments);
        },

        complete: function (jqXHR, textStatus) {
            console.log(textStatus);
        },

        statusCode: {
            '403': function (jqXHR, textStatus, err) {
                console.log(arguments);
            },

            '400': function (jqXHR, textStatus, err) {
                console.log(arguments);
            }
        }
    })

}

//验证密码
function validationPassword(ob) {
    if (ob.value.length < 8) {
        layer.alert("密码长度不能少于8位", {icon: 2}, function (index) {
            layer.close(index);
            ob.value = ''
        })
    } else if (ob.value.match(/^\d+$/)) {
        ob.value = "";
        layer.alert("密码不能全设为数字", {icon: 2}, function (index) {
            layer.close(index);
            ob.value = ''
        })
    }
}

// -----------用户结束---------------

// -----------机构开始---------------
//添加机构
function org_add() {
    var name = $('#org_name').val();
    // var nature = $('#org_nature').val();
    // var is_a = $('#org_is_a label input[type=radio][name=is_a]:checked').val();
    // var is_b = $('#org_is_b label input[type=radio][name=is_b]:checked').val();
    // var brief = $('#org_brief').val();
    if (name === '') {
        layer.alert("机构名称不可为空", {icon: 0}, function (index) {
            layer.close(index)
        });
    } else {
        var data = new FormData($("#org-add-form")[0]);
        $.ajax({
            url: "/back/org_add",
            type: "POST",
            // data: {'name': name, "nature": nature, "is_a": is_a, "is_b": is_b, "brief": brief},
            data: data,
            processData: false,   // 告诉jQuery不要处理数据
            contentType: false,   // 告诉jQuery不要设置类型
            success: function (data) {
                console.log(data);
                if (data == 1) {
                    layer.alert('创建成功！', {icon: 1}, function (index) {
                        layer.close(index);
                        window.open('/back/org', '_self');
                    });
                } else if (data == 2) {
                    layer.alert('机构信息已存在，请不要重复添加！', {icon: 2}, function (index) {
                        layer.close(index);
                        window.location.reload();
                    });
                } else {
                    layer.alert('创建失败，请联系管理员！', {icon: 2}, function (index) {
                        layer.close(index);
                    });
                }
            },

            error: function (jqXHR, textStatus, err) {
                console.log(arguments);
            },

            complete: function (jqXHR, textStatus) {
                console.log(textStatus);
            },

            statusCode: {
                '403': function (jqXHR, textStatus, err) {
                    console.log(arguments);
                },

                '400': function (jqXHR, textStatus, err) {
                    console.log(arguments);
                }
            }
        })
    }
}

//机构搜索
function org_search(roles, keyword) {
    console.log('roles---' + roles);
    console.log('keyword---' + keyword);
    //将角色保存好
    $('#pop-search-roles').attr('data-roles', roles);
    // 用哪个按钮，方法不一样
    var currentBtn0 = document.getElementById('pop-search-button2');
    currentBtn0.style.display = "";
    var currentBtn = document.getElementById('pop-search-button');
    currentBtn.style.display = "none";
    var currentBtn3 = document.getElementById('pop-search-button3');
    currentBtn3.style.display = "none";
    $.ajax({
        url: "/back/org_search",
        type: "GET",
        data: {'roles': roles, 'keyword': keyword},
        success: function (data) {
            console.log(data);
            con = data.data;
            if (roles === 'a') {
                var org_id_list = $('#pro-lead_org-input-hidden').val().split(';');
            } else {
                var org_id_list = $('#pro-research-input-hidden').val().split(';');
            }

            org_search_show(con, org_id_list, roles);
            $('.bgPop,.pop').show();
        },

        error: function (jqXHR, textStatus, err) {
            console.log(arguments);
        },

        complete: function (jqXHR, textStatus) {
            console.log(textStatus);
        },

        statusCode: {
            '403':

                function (jqXHR, textStatus, err) {
                    console.log(arguments);
                },

            '400':

                function (jqXHR, textStatus, err) {
                    console.log(arguments);
                }
        }
    })
}

// 搜索机构结构填充
function org_search_show(data, org_id_list, roles) {
    //移除旧数据结构
    if ($('#pop-content-con-id')) {
        $('#pop-content-con-id').remove();
    }
    //定义新数据结构
    var $divW = $('<div class="pop-content-con" id="pop-content-con-id"></div>');
    var $divTable = $('<table class="table table-striped table-bordered"></table>');
    // 表头
    var $divT_thead = $('<thead></thead>>');
    var $divF_thead_tr = $('<tr></tr>');
    var $divF_thead_tr_th1 = $('<th>机构名称</th>');
    var $divF_thead_tr_th2 = $('<th>机构性质</th>');
    var $divF_thead_tr_th4 = $('<th></th>');
    var $divF_tbody = $('<tbody></tbody>');
    //每一行
    var $divF_tbody_tr = $('<tr></tr>');
    var $divF_tbody_tr_td1 = $('<td></td>');
    var $divF_tbody_tr_td2 = $('<td></td>');
    var $divF_tbody_tr_td4 = $('<td></td>');
    var $divF_tbody_tr_td4_bt = $('<button class="btn btn-success btn-sm" onclick="org_click_add(this)">添加</button>');
    $divF_tbody_tr_td4_bt.attr('data-roles', roles);
    var $divF_tbody_tr_td4_bt2 = $('<button class="btn btn-outline-secondary btn-sm">已添加</button>');

    $divF_thead_tr.append($divF_thead_tr_th1);
    $divF_thead_tr.append($divF_thead_tr_th2);
    $divF_thead_tr.append($divF_thead_tr_th4);
    $divT_thead.append($divF_thead_tr);
    var con = data;
    for (var i = 0; i < con.length; i++) {
        $divF_tbody_tr_c = $divF_tbody_tr.clone();
        $divF_tbody_tr_td1_c = $divF_tbody_tr_td1.clone();
        $divF_tbody_tr_td2_c = $divF_tbody_tr_td2.clone();
        $divF_tbody_tr_td4_c = $divF_tbody_tr_td4.clone();
        $divF_tbody_tr_td4_bt_c = $divF_tbody_tr_td4_bt.clone();
        $divF_tbody_tr_td4_bt2_c = $divF_tbody_tr_td4_bt2.clone();

        $divF_tbody_tr_td1_c.text(con[i]['name']);
        $divF_tbody_tr_td2_c.text(con[i]['nature__remarks']);
        $divF_tbody_tr_td4_bt_c.attr('data-name', con[i]['name']);
        $divF_tbody_tr_td4_bt_c.attr('data-id', con[i]['id']);

        $divF_tbody_tr_c.append($divF_tbody_tr_td1_c);
        $divF_tbody_tr_c.append($divF_tbody_tr_td2_c);

        // 判断是否已添加
        if (org_id_list.indexOf(String(con[i]['id'])) > -1) {
            $divF_tbody_tr_td4_c.append($divF_tbody_tr_td4_bt2_c);
        } else {
            $divF_tbody_tr_td4_c.append($divF_tbody_tr_td4_bt_c);
        }

        $divF_tbody_tr_c.append($divF_tbody_tr_td4_c);
        $divF_tbody.append($divF_tbody_tr_c);
    }

    $divTable.append($divT_thead);
    $divTable.append($divF_tbody);
    $divW.append($divTable);
    $('.pop-content').append($divW);
}

//点击添加
function org_click_add(obj) {
    if ($(obj).attr('data-roles') === 'a') {
        if ($('#pro-lead_org-input').val() == '') {
            var org_value = $(obj).attr('data-name');
            var org_id = $(obj).attr('data-id');
        } else {
            var org_value = $('#pro-lead_org-input').val() + ';' + $(obj).attr('data-name');
            var org_id = $('#pro-lead_org-input-hidden').val() + ';' + $(obj).attr('data-id');
        }
        $('#pro-lead_org-input').val(org_value);
        $('#pro-lead_org-input-hidden').val(org_id);
    } else {
        if ($('#pro-research-input').val() == '') {
            var org_value = $(obj).attr('data-name');
            var org_id = $(obj).attr('data-id');
        } else {
            var org_value = $('#pro-research-input').val() + ';' + $(obj).attr('data-name');
            var org_id = $('#pro-research-input-hidden').val() + ';' + $(obj).attr('data-id');
        }
        $('#pro-research-input').val(org_value);
        $('#pro-research-input-hidden').val(org_id);
    }

    layer.alert("添加成功", {icon: 1}, function (index) {
        layer.close(index);
    });
    $(obj).removeClass('btn-success');
    $(obj).addClass('btn-outline-secondary');
    $(obj).text('已添加');
    $(obj).removeAttr("onclick");
}

//重置
function pro_org_reset(role) {
    if (role === 'a') {
        $('#pro-lead_org-input').val('');
        $('#pro-lead_org-input-hidden').val('')
    } else if (role === 'b') {
        $('#pro-research-input').val('');
        $('#pro-research-input-hidden').val('')
    } else {
        $('#pro-bid-input').val('');
        $('#pro-bid-input-hidden').val('')
    }

}

// -----------机构结束---------------

//------------人员开始----------------
// 添加人员
function par_add() {
    if ($('#par-name').val() == '') {
        layer.alert("姓名不能为空", {icon: 0}, function (index) {
            layer.close(index)
        });
    } else if ($('#par-email').val() == '') {
        layer.alert("邮箱不能为空", {icon: 0}, function (index) {
            layer.close(index)
        });
    } else if ($('#par-unit').val() == '') {
        layer.alert("所在单位不能为空", {icon: 0}, function (index) {
            layer.close(index)
        });
    } else if ($('#par-job').val() == '') {
        layer.alert("职务职称不能为空", {icon: 0}, function (index) {
            layer.close(index)
        });
    } else {
        var data = new FormData($("#par-add-form")[0]);
        $.ajax({
            url: "/back/par_add",
            type: "POST",
            data: data,
            processData: false,   // 告诉jQuery不要处理数据
            contentType: false,   // 告诉jQuery不要设置类型
            success: function (res) {
                console.log(res);
                if (res == 201) {
                    layer.alert("创建成功", {icon: 1}, function (index) {
                        layer.close(index);
                        window.open('/back/parm', '_self')
                    });
                } else if (res == 404) {
                    layer.alert("您输入的机构不存在，请重新选择或新建", {icon: 0}, function (index) {
                        layer.close(index)
                    });
                } else {
                    layer.alert("创建失败，请联系管理员", {icon: 2}, function (index) {
                        layer.close(index)
                    });
                }

            },

            error: function (jqXHR, textStatus, err) {
                console.log(arguments);
            },

            complete: function (jqXHR, textStatus) {
                console.log(textStatus);
            },

            statusCode: {
                '403': function (jqXHR, textStatus, err) {
                    console.log(arguments);
                },

                '400': function (jqXHR, textStatus, err) {
                    console.log(arguments);
                }
            }
        })
    }
}

// 搜索人员结构填充
function par_search_show(data, par_id_list) {
    //移除旧数据结构
    if ($('#pop-content-con-id')) {
        $('#pop-content-con-id').remove();
    }
    //定义新数据结构
    // var $pop_input = $('<input id="par-search" placeholder="请输入检索词" style="width: 50%;height: 37px;border: 1px solid #dee2e6;border-radius: 10px;padding-left: 10px"/>');
    // var $pop_button = $('<button type="button" class="btn btn-primary btn-sm" style="height: 37px;margin-bottom: 6px;margin-left: -12px"><i class="fa fa-search">搜索</i></button>');
    // $pop_button.attr('onclick', par_search($('#pop-search-input').val()));
    // var $pop_span = $('<span class="pop-close">Ｘ</span>');
    // $('.pop-top').append($pop_input);
    // $('.pop-top').append($pop_button);
    // $('.pop-top').append($pop_span);

    var $divW = $('<div class="pop-content-con" id="pop-content-con-id"></div>');
    var $divTable = $('<table class="table table-striped table-bordered"></table>');
    // 表头
    var $divT_thead = $('<thead></thead>>');
    var $divF_thead_tr = $('<tr></tr>');
    var $divF_thead_tr_th1 = $('<th>姓名</th>');
    var $divF_thead_tr_th2 = $('<th>所在单位</th>');
    var $divF_thead_tr_th3 = $('<th>职务职称</th>');
    var $divF_thead_tr_th4 = $('<th></th>');
    var $divF_tbody = $('<tbody></tbody>');
    //每一行
    var $divF_tbody_tr = $('<tr class="click-tr-count"></tr>');
    var $divF_tbody_tr_td1 = $('<td style="width: 12%"></td>');
    var $divF_tbody_tr_td2 = $('<td></td>');
    var $divF_tbody_tr_td3 = $('<td></td>');
    var $divF_tbody_tr_td4 = $('<td></td>');
    var $divF_tbody_tr_td4_bt = $('<button class="btn btn-success btn-sm" onclick="par_click_add(this)">添加</button>');
    var $divF_tbody_tr_td4_bt2 = $('<button class="btn btn-outline-secondary btn-sm">已添加</button>');

    $divF_thead_tr.append($divF_thead_tr_th1);
    $divF_thead_tr.append($divF_thead_tr_th2);
    $divF_thead_tr.append($divF_thead_tr_th3);
    $divF_thead_tr.append($divF_thead_tr_th4);
    $divT_thead.append($divF_thead_tr);
    // console.log('2222---'+par_id_list);
    var con = data;
    for (var i = 0; i < con.length; i++) {
        $divF_tbody_tr_c = $divF_tbody_tr.clone();
        $divF_tbody_tr_td1_c = $divF_tbody_tr_td1.clone();
        $divF_tbody_tr_td2_c = $divF_tbody_tr_td2.clone();
        $divF_tbody_tr_td3_c = $divF_tbody_tr_td3.clone();
        $divF_tbody_tr_td4_c = $divF_tbody_tr_td4.clone();
        $divF_tbody_tr_td4_bt_c = $divF_tbody_tr_td4_bt.clone();
        $divF_tbody_tr_td4_bt2_c = $divF_tbody_tr_td4_bt2.clone();

        $divF_tbody_tr_td1_c.text(con[i]['name']);
        $divF_tbody_tr_td2_c.text(con[i]['unit__name']);
        $divF_tbody_tr_td3_c.text(con[i]['job']);
        $divF_tbody_tr_td4_bt_c.attr('data-id', con[i]['id']);

        $divF_tbody_tr_c.append($divF_tbody_tr_td1_c);
        $divF_tbody_tr_c.append($divF_tbody_tr_td2_c);
        $divF_tbody_tr_c.append($divF_tbody_tr_td3_c);

        // 判断是否已添加
        if (par_id_list.indexOf(con[i]['id'].toString()) > -1) {
            $divF_tbody_tr_td4_c.append($divF_tbody_tr_td4_bt2_c);
        } else {
            $divF_tbody_tr_td4_c.append($divF_tbody_tr_td4_bt_c);
        }

        $divF_tbody_tr_c.append($divF_tbody_tr_td4_c);
        $divF_tbody.append($divF_tbody_tr_c);
    }

    $divTable.append($divT_thead);
    $divTable.append($divF_tbody);
    $divW.append($divTable);
    $('.pop-content').append($divW);
}

//点击添加构造结构和数据
function par_click_add_show(data) {
    var $tr = $('<tr></tr>');
    var $tr_td1 = $('<td></td>');
    var $tr_td1_input = $('<input type="text" name="par_id" hidden>');
    var $tr_td2 = $('<td></td>');
    var $tr_td2_input = $('<input type="text" name="job">');
    var $tr_td3 = $('<td></td>');
    var $tr_td3_select = $('<select name="roles" class="form-control"></select>');
    var $tr_td3_select_option1 = $('<option value="1">组长</option>');
    var $tr_td3_select_option2 = $('<option value="2">副组长</option>');
    var $tr_td3_select_option3 = $('<option value="3" selected>组员</option>');
    var $tr_td4 = $('<td></td>');
    var $tr_td5 = $('<td></td>');
    var $tr_td5_bt = $('<button class="btn btn-outline-danger btn-sm" onclick="par_click_del(this)">删除</button>');

    $tr_td1_input.attr('value', data.id);
    // console.log(data.id);
    $tr_td1.text(data.name);
    $tr_td4.text(data.unit__name);
    $tr_td5_bt.attr('data-id', data.id);

    $tr_td1.append($tr_td1_input);
    $tr_td2.append($tr_td2_input);
    $tr_td3_select.append($tr_td3_select_option1);
    $tr_td3_select.append($tr_td3_select_option2);
    $tr_td3_select.append($tr_td3_select_option3);
    $tr_td3.append($tr_td3_select);
    $tr_td5.append($tr_td5_bt);

    $tr.append($tr_td1);
    $tr.append($tr_td2);
    $tr.append($tr_td3);
    $tr.append($tr_td4);
    $tr.append($tr_td5);
    $('#pro-edit-table-id tbody').append($tr)
}

//点击添加
function par_click_add(obj) {
    $.ajax({
        url: "/back/par_search",
        type: "GET",
        data: {'id': $(obj).attr('data-id')},
        success: function (data) {
            console.log(data);
            if (data.data) {
                par_click_add_show(data.data);
                //变化按钮--已添加
                layer.alert("添加成功", {icon: 1}, function (index) {
                    layer.close(index);
                });
                $(obj).removeClass('btn-success');
                $(obj).addClass('btn-outline-secondary');
                $(obj).text('已添加');
                $(obj).removeAttr("onclick");
            } else {
                layer.alert("添加失败，请联系管理员", {icon: 2}, function (index) {
                    layer.close(index)
                });
            }
        },
        error: function (jqXHR, textStatus, err) {
            console.log(arguments);
        },
        complete: function (jqXHR, textStatus) {
            console.log(textStatus);
        },
        statusCode: {
            '403': function (jqXHR, textStatus, err) {
                console.log(arguments);
            },
            '400': function (jqXHR, textStatus, err) {
                console.log(arguments);
            }
        }
    })
}

//点击删除
function par_click_del(obj) {
    var pro_uuid = $('#pro-form-input-uuid').attr('value');
    var par_uuid = $(obj).attr('data-id');
    layer.confirm('确定要删除吗？', {icon: 2}, function (e) {
        $.post("/back/pro_rel_del", {'par_id': par_uuid, 'pro_uuid': pro_uuid}, function (res) {
            console.log(res);
            if (res == 1) {
                $(obj).parents('tr').remove();
                layer.alert('删除成功', {icon: 1}, function (index) {
                    layer.close(index)
                });
            }
        })
    })
}

//------------人员结束----------------
// 提示
function tips(msg, icon1) {
    layer.alert(msg, {icon: icon1}, function (index) {
        layer.close(index)
    });
}

// 数字格式
function validationNumber(ob) {
    if (!ob.value.match(/^(?:[\+\-]?\d+(?:\.\d+)?|\.\d*?)?$/)) {
        ob.value = "";
        layer.alert("请输入正确的数字", {icon: 2}, function (index) {
            layer.close(index)
        })
    } else {
        if (ob.value.match(/^\.\d+$/)) ob.value = 0 + ob.value;
        if (ob.value.match(/^\.$/)) ob.value = 0;
    }
}

// 所有查询
function search_all(url, param, reset) {
    var keyword = $('#search-id').val();
    if (reset === 1) {
        $('#search-hidden-keyword-input').val('');
        $('#search-a-id-reset').attr('href', '/back/' + url + '?keyword=&' + param);
    } else {
        $('#search-hidden-keyword-input').val(keyword);
        $('#search-a-id').attr('href', '/back/' + url + '?keyword=' + keyword + '&' + param);
    }
}

//所有删除
function dele(obj, url) {
    var uuid = $(obj).attr('data-uuid');
    layer.confirm('确定要删除吗？', {icon: 2}, function (e) {
        $.post(url, {'uuid': uuid}, function (res) {
                if (res == 1) {
                    // $(obj).parents('tr').remove();
                    layer.alert('删除成功', {icon: 1}, function (index) {
                        layer.close(index);
                        window.location.reload();
                    });
                } else {
                    layer.alert('操作失败，请联系管理员！', {icon: 2}, function (index) {
                        layer.close(index)
                    });
                }
            }
        )
    })

}