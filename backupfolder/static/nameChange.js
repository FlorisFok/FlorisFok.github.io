document.addEventListener('DOMContentLoaded', () => {
  document.querySelector('#name_change').onsubmit  = () => {

    // set up ajax request
    const request = new XMLHttpRequest();
    request.open('POST', '/name_check');

    // if data is recieved, check the awnser
    request.onload = () => {
      const data = JSON.parse(request.responseText);

      if (data.success) {
        alert("It was succesful");
        sessionStorage.setItem("name", data.name);
      }
      else {
        alert("Name taken");
      }
      // Reset form
      document.querySelector('#new_name').value = '';
    }

    // send AJAX with data
    const data = new FormData();
    const new_name = document.querySelector('#new_name').value;
    data.append('old_name', sessionStorage.getItem("name"));
    data.append('new_name', new_name);
    request.send(data);
    // reject autoload
    return false;
  }
})
