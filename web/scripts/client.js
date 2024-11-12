///Functions for chatting room

let room = "main";
const chatbox_short = document.querySelector(".chatbox_short");
const chatbox = document.querySelector(".chatbox");
const postbox = document.querySelector(".postbox");
let msg_max = -1;
let msg_min = -1;
let temp_max = -1;
let temp_min = -1;
let post_max = -1;
let post_min = -1;
let num = 0;
let msgs = {};
let users = {};
let get_id = "";
let users_raw = [];
let posts = {};
let func_to;

function display_user()
{
    const userfield = document.getElementById("userdisplay");
    userfield.textContent = username;
}

function receive_start()
{
    //Find correct chatbox node
    var chat;
    if (chatbox)
        chat = chatbox;
    else if (chatbox_short)
        chat = chatbox_short;
    else if (postbox)
        chat = postbox;
    else return;

    //Clear textbox
    while(chat.firstChild)
        chat.removeChild(chat.lastChild);

    if (postbox)
        request_user("postnum","",post_num);
    else
        request_user("num",room,receive_num);
}

function receive_num(result)
{
    //Gets the number of messages in room
    num = parseInt(result);
    temp_max = num-1;
    temp_min = num-51;
    if (temp_min < 0)
        temp_min = 0;
    request_user("get",room + "\nmsg" + String(temp_max),receive_msg);
    num -= 1;
}

function post_num(result)
{
    //Gets the number of posts
    num = parseInt(result);
    temp_max = num-1;
    temp_min = num-51;
    room = "post";
    if (temp_min < 0)
        temp_min = 0;
    request_user("get","post" + String(temp_max) + "\nmsg0",receive_msg);
    num -= 1;
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
    var num = post_min;
    var msg = "";
    var btn;
    console.log(posts);
    while (num <= post_max)
    {
        btn = document.createElement("button");
        btn.classList.add("postbtn");
        msg = posts[String(num)];
        
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
        writemsg(btn,msg[0], msg[1], content);
        postbox.appendChild(btn);
        num += 1;
    }
    linebreak(postbox);
    linebreak(postbox);
}

function get_user()
{
    var id = users_raw.pop();
    if (id === undefined)
    {
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
        if (users_raw.length > 0)
            get_user();
        else
            display_messages();
    }
}

function add_user(result)
{
    users[get_id] = result;
    if (users_raw.length > 1)
        get_user();
    else
        display_messages();
}

function linebreak(node)
{
    br = document.createElement("br");
    node.appendChild(br);
}

function writemsg(master,user,date,message,sep=false)
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

    if (sep)
        linebreak(master);

    //Message
    var msg_split = message.split("\n");
    msg_split.forEach(function(value){
        linebreak(master)
        txt_node = document.createTextNode(value);
        master.appendChild(txt_node);
    })
}

display_user();
receive_start();