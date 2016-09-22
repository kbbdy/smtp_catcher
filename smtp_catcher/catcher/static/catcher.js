$(document).ready(function() {

    function clear_preview() {
        $("#message_view").attr("src", "/empty")
        $("#message_title").text("")
        $("#message_from").text("")
        $("#message_to").text("")
        $("#message_preview_tags").empty().hide()
    }
    function reload_messages(newid){
        if (newid!=null){
            var id = newid.data
            if (id!=null){
                id = parseInt(id)
                if ((id>1) && (id<maxid)) {
                    return
                }
            }
        }
        maxid = 0;
        $("#spinner").stop(true, true).show();
        $.get("/messages", function(data) {
            $("#messages" ).html(data);
            var cnt = $("#messages tr:first-child").data('max')
            if (cnt==null) var cnt=0;
            $("#mail_counter").text(cnt)
            $("#spinner").delay(200).fadeOut(200)
            $('.clickable').on('click', on_message_click )
            $("#messages tr").each(function(){
                var row = $(this)
                var id = parseInt( row.data('id') )
                if (id>maxid) { maxid = id }
            })
        })
        return false
    }
    function empty_db(event){
        maxid = 0;
        clear_preview()
        $("#spinner").stop(true, true).show();
        $.get("/clear", function(data) {
            reload_messages()
        })
        return false
    }
    function err(text){
         $('#err').html('<img src="/static/warn.gif"/> '+text)
    }

    function mail_load_preview(url){
        $("#message_view").attr("src", url);
    }

    function on_message_click(ev){
        $("#messages tr").removeClass("selected")
        var obj = $(ev.currentTarget)
        var i=10; // because shit happens
        while (true){
            if (obj==undefined) return;
            var link = obj.data("preview")
            if (link) {
                obj.removeClass("new")
                obj.addClass("selected")
                $('#message_view').hide()
                $('#message_title').text( obj.find('.mail_subject').text() )
                $('#message_from').text( obj.find('.addr_from').text() )
                $('#message_to').text( obj.find('.addr_to').text() )
                $('#message_preview_tags').empty().hide()
                var tags = obj.find('div.tags').html()
                if (tags != null) {
                    $('#message_preview_tags').html(tags).show()
                }
                mail_load_preview(link)
                return false
            }
            var obj = obj.parent()
            i=i-1
            if (i==0) return false;
        }
    }

    function on_tag_click (ev){
        var obj = $(ev.currentTarget)
        var tagname = obj.data("fiterby")
        if (tagname==""){
            $("#messages tr").show()
            return false
        }
        $("#messages tr").hide()
        $("#messages tr[data-tags='"+tagname+"']").show()
    }

    function on_preview_loaded(ev){
        $('#message_view').show()
        var iframe = $(ev.currentTarget)
        //var w = iframe.contents().width()
        //iframe.width(w)
        iframe.height(0)
        var h = iframe.contents().height()
        iframe.height(h)
    }

    $('#reload').on('click', reload_messages )
    $('#clear').on('click', empty_db )
    $('.clickable').on('click', on_message_click )
    //$('div.head span.tag a').on('click', on_tag_click)
    $('#message_view').on('load', on_preview_loaded)

    function connect(){
        try {
            var addr = "ws://"+window.location.hostname+":8026/"
            var socket = new WebSocket(addr)
            //socket.onopen = function(){}
            socket.onmessage = reload_messages
            socket.onclose = function(){ err('Connectin lost, autorefresh is disabled') }
        } catch(exception) {
            err("Can't connext to server")
        }
    }

    if(!("WebSocket" in window)){
       err('Auto refresh is not working in this browser')
    } else {
        connect()
        $('#clear').attr('href','#')
    }

    var preimg=new Image();
    preimg.src='/static/warn.gif';
    var maxid = 0;
})