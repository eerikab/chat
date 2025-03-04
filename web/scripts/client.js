///Functions for chatting room

const chatbox_short = document.querySelector(".chatbox_short");
const chatbox = document.querySelector(".chatbox");
const postbox = document.querySelector(".postbox");
const userlist = document.querySelector(".contactlist");
const userbox = document.querySelector(".userlist_box");
const title_label = document.getElementById("page_title");
let temp_max = -1;
let temp_min = -1;
let num = 0;
let msgs = {};
let users = {"main" : "Main"};
let get_id = "";
let users_raw = [];
let posts = {};
let friend_list = [];
let phase = "contacts";
let first_load = true;
let friend_used = [];
let checking = false;
let delay = 600000;
sessionStorage.setItem("prevpage",location.href);

if (!username)
    location.href = "index.html";

//Button classes
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

        var date = time_format(msg[1]);
        for (i = 0; i < 5; i++)
            date += String.fromCharCode(160)
        date += String(msg[3]-1) + " replies"

        //Put post content on button
        writemsg(this.btn, msg[0], date, content);
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

        add_text(this.btn, users[id]);

        userlist.prepend(this.btn);

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
                userbox.prepend(btn);
            }
            else
            {
                if (!(msgs[id]))
                {
                    msgs[id] = {};
                }

                if (num.toString() in msgs[id])
                {
                    var data = msgs[id][num.toString()];
                    var msg = data[2].split("\n")[0]
                    writemsg(btn,id,time_format(data[1]),"\n"+msg);
                    userbox.appendChild(btn);
                }
                else
                {
                    request_user("get",id+"\n"+num.toString(),function(result)
                    {
                        var data = result.split("\n");
                        var msg = "";

                        for (var i = 2; i < data.length; i++)
                        {
                            msg += data[i] + "\n";
                        }

                        msgs[id][String(num)] = [data[0],data[1], msg];
                        writemsg(btn,id,time_format(data[1]),"\n"+data[2]);
                        userbox.appendChild(btn);
                        save_msgs();
                    });
                }
            }
        })

        btn.addEventListener("click",function(){
            sessionStorage.setItem("friend", id);
            sessionStorage.setItem("room", id);
            location.href = "messages.html";
        });
    }
}

//Display username on the page
function display_user()
{
    const userfield = document.getElementById("userdisplay");
    userfield.textContent = username;
}

//Get messages and posts
function receive_start()
{
    if (checking)
        return;

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

    checking = true;

    //Clear chatbox from default content
    if (first_load)
    {
        first_load = false;
        if (chat)
        {
            while(chat.firstChild)
                chat.removeChild(chat.lastChild);
            add_node(chat, "Loading messages...");
        }


        if (userlist)
        {
            while(userlist.firstChild)
                userlist.removeChild(userlist.lastChild);

            /*for (var i = 0; i < friend_list.length; i++)
            {
                new userbtn(friend_list[i]);
                friend_used.push(friend_list[i]);
            }*/
        }
        //Set room on private messages
        if (userlist)
            room = friend;

        phase = "contacts";
        
        if (chatbox || chatbox_short) {
            //Set page title
            if (room.substring(0,4) == "post")
                set_title("Post by " 
                    + users[posts[parseInt(room.substring(4,room.length))][0]]);
            if (userlist)
                set_title("Messages - " + users[room]);

            //Check for new messages periodically
            window.setInterval(refresh, delay);
            request_user("broadcast","",broadcast)
            
        }
    
        if (postbox)
            request_user("postnum","",post_num);
        else if (userlist)
            request_user("contacts","",get_friend);
        else
            request_user("num",room,receive_num);
    }
    else
    {
        if (postbox)
            request_user("postnum","",post_num);
        else if (chatbox || chatbox_short)
            request_user("num",room,receive_num);
        else
            request_user("contacts","",get_friend);
    }
}

function receive_num(result)
{
    //Gets the number of messages in room
    num = parseInt(result);
    if (temp_max >= num && num > 0) {
        checking = false;
        return;
    }
    if (!(room in msgs))
    {
        msgs[room] = {};
        msgs[room]["max"] = -1;
        msgs[room]["min"] = -1;
    }
    if (!num)
    {
        display_messages();
        return;
    }    

    let to_add = [];
    temp_max = num;
    temp_min = num-50;
    if (temp_min < 1)
        temp_min = 1;
    phase = "messages";
    if ("max" in msgs[room] && msgs[room]["max"] < temp_min) {
        msgs[room]["max"] = num;
        msgs[room]["min"] = num; 
    }

    while (num >= temp_min) 
    {
        if (!(String(num) in msgs[room]))
        {
            to_add.push(num);
        }
        num -= 1;
    }
    messagebox.value = "";

    if (to_add.length)
    {
        request_user(
            "get", 
            room + "\n" + String(to_add.at(-1)) + "\n" + String(to_add[0]),
            receive_msg
        );
    }
    else 
        display_messages();
}

function post_num(result)
{
    //Gets the number of posts
    num = parseInt(result);
    if (!num)
        return;
    let to_add = [];
    temp_max = num;
    temp_min = num-50;
    room = "post";
    phase = "posts";
    if (temp_min < 1)
        temp_min = 1;
    while (num >= temp_min)
    {
        if (!(String(num) in posts))
        {
            to_add.push(num);
        }
        num -= 1;
    }

    if (to_add.length)
        request_user(
            "getposts",
            String(to_add.at(-1)) + "\n" + String(to_add[0]),
            receive_msg
        );
    else
        display_posts();
}

function receive_msg(result)
{
    var data = JSON.parse(result);
    console.log(data);

    if (postbox)
    {
        for (i = 0; i < data.length; i++)
        {
            var user = data[i][2];
            if (!(user in users_raw))
                users_raw.push(user);

            var date = data[i][3];
            var msg = data[i][4];
            var length = data[i][6];
            num = data[i][0];

            posts[String(num)] = [user, date, msg, length];
            if (!("max" in posts) || num > posts["max"])
                posts["max"] = num;
            if (!("min" in posts) || num < posts["min"])
                posts["min"] = num;
        }
        get_user();
    }
    else
    {
        for (i = 0; i < data.length; i++)
        {
            console.log(i);
            var user = data[i][1];
            if (!(user in users_raw))
                users_raw.push(user);

            var date = data[i][2];
            var msg = data[i][3];
            num = data[i][0];

            msgs[room][String(num)] = [
                user, date, msg
            ];
            if (!("max" in msgs[room]) || num > msgs[room]["max"])
                msgs[room]["max"] = num;
            if (!("min" in msgs[room]) || num < msgs[room]["min"])
                msgs[room]["min"] = num;
        }
        get_user();
    }
}

//Display messages
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

    while(chat.firstChild)
        chat.removeChild(chat.lastChild);
    console.log(Object.entries(msgs));

    //Write out messages to chatbox
    num = msgs[room]["min"];
    if (msgs[room]["max"] < 1)
    {
        add_node(chat, "No messages have been sent here yet");
        checking = false;
        return;
    }    
    if (num == 1)
    {
        add_node(chat, "This is the start of the chat room");
        linebreak(chat);
        linebreak(chat);
    }    
    var msg = "";
    while (num <= msgs[room]["max"] && num > 0)
    {
        msg = msgs[room][String(num)];
        writemsg(chat,msg[0], time_format(msg[1]), msg[2]);
        linebreak(chat);
        linebreak(chat);
        num += 1;
    }

    save_msgs();
    window.scrollTo(0, document.body.scrollHeight);

    checking = false;
}

function refresh()
{
    //Ping server periodically
    request_user("ping");
}

function broadcast(data="")
{
    var resp = data.split("\n");
    if (resp[0] !== "update")
        return;
    if (resp[1].indexOf("room") && id_to_room(room) == resp[1])
        resp[1] == room
    if (resp[1] in msgs && resp[1] == room)
        receive_start();
}

function display_posts()
{
    while(postbox.firstChild)
        postbox.removeChild(postbox.lastChild);

    //Write out messages to chatbox
    var num = posts["max"];
    console.log(posts);
    if (num < 1)
    {
        add_node(postbox, String.fromCharCode(160) 
            + "No posts have been found yet");
        return;
    }    
    while (num >= posts["min"])
    {
        new postbtn(num);
        num -= 1;
    }
    linebreak(postbox);
    linebreak(postbox);
    if (posts["min"] === 1)
    {
        add_node(postbox, String.fromCharCode(160) + " End of the post list");
        linebreak(postbox);
        linebreak(postbox);
    }


    save_msgs();
    checking = false;
}

//Get user names
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

//Writing functions
function linebreak(node)
{
    br = document.createElement("br");
    node.appendChild(br);

}

function writemsg(master,user,date,message)
{
    //Writes out the message in correct format
    //User
    add_node(master, users[user], "b", "user");

    //Spaces between username and date
    for(var i = 0; i < 5; i++)
    {
        add_text(master, String.fromCharCode(160));
    }

    //Date
    add_node(master, date);

    //Message
    var msg_split = message.split("\n");
    msg_split.forEach(function(value){
        linebreak(master)
        add_text(master, value);
    })
}

//Contacts
function get_friend(result)
{
    friend_list = result.split("\n");
    for (var i = 0; i < friend_list.length; i++)
    {
        if (friend_list[i] && !(friend_list[i] in users_raw))
            users_raw.push(friend_list[i]);
    }   
    get_user();
}

function display_friends()
{
    if (userbox) {
        while(userbox.lastChild)
            userbox.removeChild(userbox.lastChild);
    }
    while(userlist.lastChild)
        userlist.removeChild(userlist.lastChild);

    for (var i = 0; i < friend_list.length; i++)
    {
        if (friend_list[i])
        {
            if (!(friend_list[i] in friend_used))
            {
                new userbtn(friend_list[i]);
                friend_used.push(friend_list[i]);
            }  

            if (userbox)
            {
                new contact_btn(friend_list[i]);
            }
        }
    }

    new userbtn("main");
    friend_used.push("main");

    save_msgs();

    if (postbox)
        request_user("postnum","",post_num);
    else if (!userbox)
        request_user("num",room,receive_num);
    else
        checking = false;
}

//Text fields
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

    request_user("message",room+"\n"+message);
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

    request_user("addcontact",message,receive_start);
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

//Data saving
function save_msgs()
{
    sessionStorage.setItem("msgs",JSON.stringify(msgs));
    sessionStorage.setItem("users",JSON.stringify(users));
    sessionStorage.setItem("posts",JSON.stringify(posts));
    sessionStorage.setItem("friends",JSON.stringify(friend_list));
}

function load_msgs()
{
    let msgs_raw = sessionStorage.getItem("msgs");
    if (msgs_raw)
        msgs = JSON.parse(msgs_raw);

    let users_raw = sessionStorage.getItem("users");
    if (users_raw)
        users = JSON.parse(users_raw);

    let posts_raw = sessionStorage.getItem("posts");
    if (posts_raw)
        posts = JSON.parse(posts_raw);

    let friend_raw = sessionStorage.getItem("friends");
    if (friend_raw)
        friend_list = JSON.parse(friend_raw);
}

function logout()
{
    localStorage.removeItem("username");
    localStorage.removeItem("password");
    location.href = "index.html";
}

function set_title(text)
{
    document.title = "Chat - " + text;
    title_label.textContent = text;
}

//Functions to use on page open
display_user();
load_msgs();
receive_start();