document.addEventListener('DOMContentLoaded', () => {
   // Connect to websocket
   var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

   // Disables the buttons
   document.querySelector('#onesubmit').disabled = true;
   let room = sessionStorage.getItem("room");
   let name = sessionStorage.getItem("name");

   if (sessionStorage.getItem("name")) {
       const name = sessionStorage.getItem("name");
       socket.emit('submit-name', {'name': name});
       document.querySelector('#name-holder').innerHTML = `${name}'s chat`;
   }

   socket.emit("jroom", {'name':name, 'room':room});
   socket.emit('history-call', {'room': room});


   socket.on('history-response', data => {

     while (document.getElementById("li-message")) {
       document.getElementById("li-message").remove()
     };

     for ( let i = 0; i < data.length; i++)
     {
       var obj = data[i];
       if (obj.name === sessionStorage.getItem("name")){

         const li = document.createElement('p');
         li.innerHTML = `${obj.name}, at ${obj.time} said: ${obj.text}`;
         li.id = "li-message";
         document.querySelector('#message-box').appendChild(li);
       }
       else {
         const li = document.createElement('p');
         li.innerHTML = `${obj.name}, at ${obj.time} said: ${obj.text}`;
         li.style = "color : red;";
         li.align = "right";
         li.id = "li-message";
         document.querySelector('#message-box').appendChild(li);
       }
     }
   });

   //search for name
   if (sessionStorage.getItem("name")) {
       const name = sessionStorage.getItem("name");
       socket.emit('submit-name', {'name': name});
       document.querySelector('#name-holder').innerHTML = `${name}'s chat`;
   }

    document.querySelector('#text').onkeyup  = () => {
         if (document.querySelector('#text').value.length > 0 &&
              sessionStorage.getItem('room')) {
             document.querySelector('#onesubmit').disabled = false;
           }
         else {
             document.querySelector('#onesubmit').disabled = true;
           }
     };

     document.querySelector('#new-message').onsubmit = () => {
       // Only able to send if name is set.
       if (!sessionStorage.getItem("name") || !sessionStorage.getItem("room"))
       {
         alert("please enter room/name");
         return false;
       }

       // Gets data and emits it
       const text = document.querySelector('#text').value;
       const name = sessionStorage.getItem("name");

       const room = sessionStorage.getItem("room");
       socket.emit('message-room', {'selection': text, 'name':name, 'room':room});

       // Reset clean state
       document.querySelector('#text').value = '';
       document.querySelector('#onesubmit').disabled = true;

       // Rejects autoload
       return false;
     }

   // When connected, configure buttons
   document.querySelector('#room_form').onsubmit = () => {
     // Only able to send if name is set.
     if (document.querySelector('#value_room').value === 'join') {
       // Gets data and emits it
       let name = sessionStorage.getItem("name");
       let room = document.querySelector('.room_name').value;
       if (!(sessionStorage.setItem("room", room) == room))
       {
         socket.emit("jroom", {'name':name, 'room':room});
         socket.emit('history', {'room': room});
         sessionStorage.setItem("room", room);
       }
     }
     else {
       // Gets data and emits it
       let name = sessionStorage.getItem("name");
       let room = document.querySelector('.room_name').value;

       socket.emit("create-room", {'name':name, 'room':room});
       sessionStorage.setItem("room", room);
     }

     // Reset clean state
     document.querySelector('#text').value = '';
     document.querySelector('#onesubmit').disabled = true;

     // Rejects autoload
     return false;
   }

  socket.on('message-room', data => {
    if (data.name === sessionStorage.getItem("name")){

      const li = document.createElement('p');
      li.innerHTML = `${data.name}, at ${data.time} said: ${data.text}`;
      li.id = "li-message";
      document.querySelector('#message-box').appendChild(li);
    }
    else {
      const li = document.createElement('p');
      li.innerHTML = `${data.name}, at ${data.time} said: ${data.text}`;
      li.style = "color : red;"
      li.align = "right"
      li.id = "li-message";
      document.querySelector('#message-box').appendChild(li);
    }
  });
  socket.on('new_member', data => {
    if (data.succes){
      alert("Room name taken")
    }
    else if (!data.name) {
      alert("Room does not exist")
    }
    else {
      const p = document.createElement('p');
      p.innerHTML = `${data.name}, at ${data.time} joined the room`;
      p.style = "color : blue;"
      p.align = "center"
      p.id = "li-message";
      document.querySelector('#message-box').appendChild(p);
    }
  });
  socket.on('rooms', data => {

      while (document.getElementById("li-room")) {
        document.getElementById("li-room").remove()
      };

      for (var i = 0; i < data.length; i++)
      {

          var obj = data[i];
          const option = document.createElement('li');
          option.innerHTML = `${obj.name}`;
          option.id = "li-room"
          document.querySelector('#room-list').append(option);

      }
  });
});
