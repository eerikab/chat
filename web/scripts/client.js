///Functions for chatting room

const chatbox_short = document.querySelector(".chatbox_short");
const chatbox = document.querySelector(".chatbox");
const postbox = document.querySelector(".postbox");
const userlist = document.querySelector(".contactlist");
const userbox = document.querySelector(".userlist_box");
let msg_max = -1;
let msg_min = -1;
let temp_max = -1;
let temp_min = -1;
let post_max = -1;
let post_min = -1;
let num = 0;
let msgs = {};
let users = {"main" : "Main", userid : username};
let get_id = "";
let users_raw = [];
let posts = {};
let friend_list = [];
let phase = "contacts";

class postbtn {
    num;
    constructor(num)
    {
        //this.num = num;

        

        this.btn = document.createElement("button");
        this.btn.classList.add("postbtn");
        var msg = posts[String(num)];
        
        //Get only the first 3 lines of the post
        var content_split = msg[2].split("\n");
        var content = "";
        for (var i = 0; i < content_split.length; i++)
        {
            console.log(content_split.length);
            if (i < 3)
            {
                content += "\n" + content_split[i];
            }
            else
                break;
        }

        //Put post content on button
        writemsg(this.btn,msg[0], msg[1], content);
        postbox.appendChild(this.btn);

        this.btn.addEventListener("click",function(){
            sessionStorage.setItem("room", "post"+num);
            location.href = "chat.html";
        });
    }
}

class userbtn {
    id;
    constructor(id)
    {
        this.id = id;

        this.btn = document.createElement("button");
        if (id === friend && !userbox)
            this.btn.classList.add("btn_active");
        else
            this.btn.classList.add("btn_inactive");

        this.btn.appendChild(document.createTextNode(users[id]));

        userlist.appendChild(this.btn);

        this.btn.addEventListener("click",function(){
            sessionStorage.setItem("friend", id);
            sessionStorage.setItem("room", id);
            location.href = "messages.html";
        });
    }
}

class contact_btn {
    id;
    constructor(id)
    {
        this.id = id;

        var btn = document.createElement("button");
        btn.classList.add("postbtn");

        request_user("num",id,function(result)
        {
            var num = parseInt(result)
            if (num == 0)
            {
                writemsg(btn,id,"","\nNo messages");
                userbox.appendChild(btn);
            }
            else
            {
                request_user("get",id+"\nmsg"+(num-1).toString(),function(result)
                {
                    var data = result.split("\n");
                    writemsg(btn,id,data[1],"\n"+data[2]);
                    userbox.appendChild(btn);
                });
            }
        })

        btn.addEventListener("click",function(){
            sessionStorage.setItem("friend", id);
            sessionStorage.setItem("room", id);
            location.href = "messages.html";
        });
    }

    receive_num(result)
    {
        alert("num" + result);
        var num = parseInt(result)
        if (num == 0)
        {
            writemsg(btn,id,"","No messages");
            userbox.appendChild(btn);
        }
        else
        {
            request_user("get",id,this.receive_msg);
        }
    }

    receive_msg(result)
    {
        var data = result.split("\n");
        writemsg(btn,id,data[1],data[2]);
        userbox.appendChild(btn);
    }
}

function display_user()
{
    const userfield = document.getElementById("userdisplay");
    userfield.textContent = username
}

function reset()
{
    msg_max = -1;
    msg_min = -1;
    temp_max = -1;
    temp_min = -1;
    post_max = -1;
    post_min = -1;
    num = 0;
    msgs = {};
    posts = {};
    phase = "contacts";
}

function receive_start()
{
    //Find correct chatbox node
    var chat = "";
    if (chatbox)
        chat = chatbox;
    else if (chatbox_short)
        chat = chatbox_short;
    else if (postbox)
        chat = postbox;
    else if (userbox)
        chat = userbox;

    reset();

    //Clear textbox
    while(chat.firstChild)
        chat.removeChild(chat.lastChild);

    if (userlist)
    {
        while(userlist.firstChild)
            userlist.removeChild(userlist.lastChild);
    }
        

    //Set room on privamte messages
    if (userlist)
        room = friend;

    if (postbox)
        request_user("postnum","",post_num);
    else if (userlist)
        request_user("contacts","",get_friend);
    else
        request_user("num",room,receive_num);
}

function receive_num(result)
{
    //Gets the number of messages in room
    num = parseInt(result);
    temp_max = num-1;
    temp_min = num-51;
    if (!num)
        return;
    if (temp_min < 0)
        temp_min = 0;
    request_user("get",room + "\nmsg" + String(temp_max),receive_msg);
    num -= 1;
    phase = "messages";
    messagebox.value = "";
}

function post_num(result)
{
    //Gets the number of posts
    num = parseInt(result);
    if (!num)
        return;
    temp_max = num-1;
    temp_min = num-51;
    room = "post";
    if (temp_min < 0)
        temp_min = 0;
    request_user("get","post" + String(temp_max) + "\nmsg0",receive_msg);
    num -= 1;
    phase = "posts";
}

function receive_msg(result)
{
    var data = result.split("\n");
    console.log(data)

    var user = data[0];
    if (!(user in users_raw))
        users_raw.push(user);

    var date = data[1];
    var msg = "";
    for (var i = 2; i < data.length; i++)
    {
        msg += data[i]+"\n";
    }

    if (postbox)
    {
        posts[String(num)] = [user, date, msg];
        if (num > post_max)
            post_max = num;
        if (num < post_min || post_min == -1)
            post_min = num;

        num -= 1;

        if (num >= temp_min)
            request_user("get","post" + String(num) + "\nmsg0",receive_msg);
        else
            get_user();
    }
    else
    {
        msgs[String(num)] = [user, date, msg];
        if (num > msg_max)
            msg_max = num;
        if (num < msg_min || msg_min == -1)
            msg_min = num;

        num -= 1;

        if (num >= temp_min)
            request_user("get",room + "\nmsg" + String(num),receive_msg);
        else
            get_user();
    }
}

function display_messages()
{
    //Find correct chatbox node
    var chat;
    if (chatbox)
        chat = chatbox;
    else if (chatbox_short)
        chat = chatbox_short;
    else if (postbox)
    {
        display_posts();
        return;
    }
    else return;

    console.log(Object.entries(msgs));

    //Write out messages to chatbox
    num = msg_min;
    var msg = "";
    while (num <= msg_max)
    {
        msg = msgs[String(num)];
        writemsg(chat,msg[0], msg[1], msg[2]);
        linebreak(chat)
        num += 1;
    }
}

function display_posts()
{
    //Write out messages to chatbox
    var num = post_max;
    console.log(posts);
    while (num >= post_min)
    {
        new postbtn(num);
        num -= 1;
    }
    linebreak(postbox);
    linebreak(postbox);
}

function get_user()
{
    var id = users_raw.pop();
    if (id === undefined)
    {
        if (phase === "contacts")
            display_friends();
        else if (postbox)
            display_posts();
        else
            display_messages();
        return;
    }

    if (!(id in users))
    {
        get_id = id;
        request_user("user",id,add_user);
    }
    else
    {
        get_user();
    }
}

function add_user(result)
{
    users[get_id] = result;
    get_user();
}

function linebreak(node)
{
    br = document.createElement("br");
    node.appendChild(br);
}

function writemsg(master,user,date,message)
{
    //Writes out the message in correct format
    //User
    var txt = document.createElement("b");
    var txt_node = document.createTextNode(users[user]);
    txt.appendChild(txt_node)
    txt.classList.add("user");
    master.appendChild(txt);

    //Spaces between username and date
    for(var i = 0; i < 5; i++)
    {
        var space = document.createTextNode(String.fromCharCode(160));
        master.appendChild(space);
    }

    //Date
    txt = document.createElement("span");
    txt_node = document.createTextNode(""+date);
    txt.appendChild(txt_node);
    txt.classList.add("comment");
    master.appendChild(txt);

    //Message
    var msg_split = message.split("\n");
    msg_split.forEach(function(value){
        linebreak(master)
        txt_node = document.createTextNode(value);
        master.appendChild(txt_node);
    })
}

function get_friend(result)
{
    friend_list = result.split("\n");
    for (var i = 0; i < friend_list.length; i++)
    {
        if (!(friend_list[i] in users_raw))
            users_raw.push(friend_list[i]);
    }   
    get_user();
}

function display_friends()
{
    new userbtn("main");

    for (var i = 0; i < friend_list.length; i++)
    {
        new userbtn(friend_list[i]);
        
        if (userbox)
        {
            new contact_btn(friend_list[i]);
        }
    }

    if (postbox)
        request_user("postnum","",post_num);
    else
        request_user("num",room,receive_num);
}

const send_msg_button = document.getElementById("send_msg");
const send_post_button = document.getElementById("send_post");
const send_user_button = document.getElementById("send_user");

const messagebox = document.querySelector(".message");
const friend_input = document.getElementById("name");

function send_msg()
{
    var message = messagebox.value;
    if (message.length < 1)
        return;

    request_user("message",room+"\n"+message,receive_start);
}
    
function send_post()
{
    var message = messagebox.value;
    if (message.length < 1)
        return;

    request_user("post",message,receive_start);
}

function send_user()
{
    var message = friend_input.value;
    if (message.length < 1)
        return;

    request_user("add_contact",room+"\n"+message,receive_start);
}

if (send_msg_button)
{
    send_msg_button.addEventListener("click",send_msg);
}

if (send_post_button)
{
    send_post_button.addEventListener("click",send_post);
}

if (send_user_button)
{
    send_user_button.addEventListener("click",send_user);
}

display_user();
receive_start();