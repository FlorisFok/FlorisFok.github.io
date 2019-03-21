document.addEventListener('DOMContentLoaded', () => {
   // Connect to websocket
   var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

   // Disables the buttons
   document.querySelector('#twosubmit').disabled = true;
   document.querySelector('#onesubmit').disabled = true;
   document.querySelector('#text').readOnly = true;

   let name = sessionStorage.getItem("name");
   socket.emit('history-call', {'name': name});

   socket.on('history-response', data => {

     for ( let i = 0; i < data.length; i++)
     {
       var obj = data[i];
       if (obj.name === sessionStorage.getItem("name")){

         const li = document.createElement('p');
         li.innerHTML = `${obj.name}, at ${obj.time} said: ${obj.text}`;
         li.class = "li-message";
         document.querySelector('#message-box').appendChild(li);
       }
       else {
         const li = document.createElement('p');
         li.innerHTML = `${obj.name}, at ${obj.time} said: ${obj.text}`;
         li.style = "color : red;";
         li.align = "right";
         li.class = "li-message";
         document.querySelector('#message-box').appendChild(li);
       }
     }
   });

   //search for name
   if (sessionStorage.getItem("name")) {
       const name = sessionStorage.getItem("name");
       document.querySelector('#name').value = name;
       socket.emit('submit-name', {'name': name});
       document.querySelector('#name-holder').innerHTML = `${name}'s chat`;
       sessionStorage.setItem("name", name);

       // rejects autoload
       document.querySelector('#name').readOnly = true;
       document.querySelector('#twosubmit').disabled = true;
       document.querySelector('#text').readOnly = false;
   }

   // Enable button only if there is text in the input field
   document.querySelector('#name').onkeyup  = () => {
        if (document.querySelector('#name').value.length > 0 &&
            !sessionStorage.getItem("name"))
            document.querySelector('#twosubmit').disabled = false;
        else
            document.querySelector('#twosubmit').disabled = true;
    };

    document.querySelector('#text').onkeyup  = () => {
         if (document.querySelector('#text').value.length > 0 &&
              document.querySelector('#name').readOnly){
             document.querySelector('#onesubmit').disabled = false;
           }
         else {
             document.querySelector('#onesubmit').disabled = true;
           }
     };

   // When connected, configure buttons
   document.querySelector('#new-message').onsubmit = () => {
     // Only able to send if name is set.
     if (!sessionStorage.getItem("name")){
       alert("please enter name");
       return false;
     }

     // Gets data and emits it
     const text = document.querySelector('#text').value;
     const name = sessionStorage.getItem("name");

     const sid = document.querySelector('#sid').value;
     socket.emit('message', {'selection': text, 'sender':name, 'reciever':sid});

     // Reset clean state
     document.querySelector('#text').value = '';
     document.querySelector('#onesubmit').disabled = true;

     // Rejects autoload
     return false;
   }
   //on name submit
   document.querySelector('#username').onsubmit = () => {
     if (!sessionStorage.getItem("name")){
       const name = document.querySelector('#name').value;
       socket.emit('submit-name', {'name': name});
       document.querySelector('#name-holder').innerHTML = `${name}'s chat`;
       sessionStorage.setItem("name", name);

       // rejects autoload
       document.querySelector('#name').readOnly = true;
       document.querySelector('#twosubmit').disabled = true;
       document.querySelector('#text').readOnly = false;
       return false;
     }
   }

  //When a new vote is announced, add to the unordered list
  socket.on('message', data => {
    if (data.name === sessionStorage.getItem("name")){

      const li = document.createElement('p');
      li.innerHTML = `${data.name}, at ${data.time} said: ${data.text}`;
      document.querySelector('#message-box').appendChild(li);
    }
    else {
      const li = document.createElement('p');
      li.innerHTML = `${data.name}, at ${data.time} said: ${data.text}`;
      li.style = "color : red;"
      li.align = "right"
      document.querySelector('#message-box').appendChild(li);
    }
  });

  socket.on('contacts', data => {
      var drop_down_obj = document.getElementById("sid");
      var len = drop_down_obj.length;
      for (var i=0; i < len; i++)
      {
        drop_down_obj.remove(0);
      }

      const option = document.createElement('option');
      option.innerHTML = "All";
      option.value = "None";
      document.querySelector('#sid').append(option);

      for (var i = 0; i < data.length; i++)
      {
          var obj = data[i];
          if (!(obj.name === sessionStorage.getItem("name")))
          {
            const option = document.createElement('option');
            option.innerHTML = `${obj.name}`;
            option.value = obj.name;
            document.querySelector('#sid').append(option);
          }
      }
  });
});
